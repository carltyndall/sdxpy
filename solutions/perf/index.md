## Solutions

### More Efficient Filtering

The original `DfCol.filter` builds a temporary dictionary containing
every column value for every row, then spreads it across the filter
function.  We can reduce this overhead by using `inspect` to discover
which parameters the function actually needs, and by passing a row
index `i_row` as an additional keyword argument.

The derived class `DfColIndexed` does exactly that.  When the filter
function declares only `i_row` (no columns at all), we skip dictionary
construction entirely — useful for subsampling every Nth row or
implementing train/test splits without touching column data.  When it
declares a subset of columns plus `i_row`, we build a smaller kwargs
dict.  The speedup is most pronounced for wide tables where most
columns are irrelevant to the predicate.

[%inc sol_more_efficient_filtering.py %]

### Empty Dataframes

`DfRow` cannot represent an empty dataframe because its constructor
infers column names from the first row.  The solution is to store
column names independently, accepting an explicit `cols` argument when
the row list is empty.  `DfRowEmpty` does this while keeping the
row-wise storage model.  Filtering an empty dataframe returns another
empty dataframe, and equality checks short-circuit correctly when row
counts differ.

[%inc sol_empty_dataframes.py %]

### Unified Constructors

`DfRow.__init__` takes a list of dicts; `DfCol.__init__` takes
`**kwargs` mapping column names to lists.  We can unify them by having
both accept `**kwargs` in column-list style.  `DfRowUnified` converts
those column lists into the internal list-of-dicts representation
during construction.  This is useful when a factory function needs to
instantiate either layout without knowing which class it holds — the
caller passes the class and the same keyword arguments regardless.

[%inc sol_unified_constructors.py %]

### Fixture Functions

Pytest's `@fixture` decorator replaces hand-rolled helper functions.
Fixtures are injected by name into test signatures, making
dependencies explicit.  Pytest also handles fixture teardown and can
share a single fixture instance across multiple tests when scope is
broadened, though the default per-function scope is appropriate here.

[%inc sol_fixture_functions.py %]

### Using Arrays

Python's `array` module stores homogeneous numeric values in a
contiguous C array, which reduces memory overhead and improves cache
locality.  `DfArray` wraps each column in an `array.array`, picking
the typecode from the first element's type.  For large integer or
float columns, this can be noticeably faster than a list of Python
int objects, though the benefit diminishes when the work is dominated
by Python-level iteration rather than memory access.

[%inc sol_using_arrays.py %]

### Crossover

We binary-search the fraction of filter operations (versus select)
where `DfRow` and `DfCol` have equal weighted time.  The crossover
depends on dataframe shape: wider tables favour column-wise storage
for select, pushing the crossover to a higher filter fraction.

With a fixed number of columns and growing rows, row-wise select
becomes linearly more expensive (every row must be visited to pluck
out column values), while column-wise select just returns references
to existing lists.  This fixed-column / growing-row scenario is the
more realistic one for most analytics workloads.

[%inc sol_crossover.py %]

### Conversion

Converting `DfRow` to `DfCol` iterates over every cell to repack
values from dictionaries into per-column lists.  Converting in the
opposite direction does the reverse.  Both are O(nrow × ncol), but
col→row is usually faster because building many small dicts has more
overhead than building lists via comprehension.  The gap widens as the
dataframe gets wider (more keys per dict).

[%inc sol_conversion.py %]

### Filtering by Strings

When columns contain strings rather than integers, the cost of string
comparison dilutes the overhead of building the temporary dictionary
in `DfCol.filter`.  Containment checks (`in`) are more expensive than
exact equality or `startswith`, further narrowing the proportional
difference between the two layouts.  For string-heavy workloads the
choice of storage layout matters less for filtering than it does for
selection.

[%inc sol_filtering_by_strings.py %]

### Inspection

`DfColInspect.filter` uses `inspect.signature` to discover which
parameters the user's function expects, then builds a kwargs dict
containing only those columns.  This lets the user write `def
f(label_0):` instead of `def f(label_0, **kwargs):`.  The speedup
grows with the ratio of total columns to columns actually used in the
predicate, making it particularly valuable for wide tables.

[%inc sol_inspection.py %]

### Join Performance

Both naive join implementations use a double loop, so the asymptotic
cost is O(n × m) regardless of storage layout.  Row-wise storage has a
slight edge because key lookups are cheap dict accesses, while
column-wise storage calls `.get()` for every cell.  As the key space
shrinks (more matches), the output grows and both slow down
proportionally — the fraction of matching keys affects total work but
the relative ranking stays similar.

[%inc sol_join_performance.py %]

### Join Optimization

Building an index (a dict from key values to lists of row indices) on
the smaller table reduces the join from O(n × m) to O(n + m + k),
where k is the number of matching pairs produced.  When key spaces are
large (few collisions), the index join is dramatically faster.  When
the key space is tiny (many collisions, large output), both approaches
converge because output construction dominates the cost.

[%inc sol_join_optimization.py %]
