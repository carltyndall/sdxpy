"""Solution: Element IDs exercise.

Discuss the pros and cons of generating element IDs by hashing content.

Pros:
- Deterministic and stable: the same content always produces the same ID,
  so bookmarks and cross-references survive rebuilds.
- No collision across different content: two different pieces of text
  won't accidentally get the same ID (assuming a good hash function).
- No need for authors to specify IDs manually.

Cons:
- Identical content produces the same hash, violating the HTML requirement
  that IDs be unique within a page.  Repeated boilerplate (footers,
  disclaimers) would cause collisions.
- Content changes break all references.  Even fixing a typo changes the
  hash, breaking every link that pointed to that element.
- Hashing is one-way, so you cannot reverse an ID to discover what content
  it points to during debugging.
- Cryptographic hash functions are not free; for a site with thousands of
  pages the cumulative cost is measurable.
- Hash-based IDs are opaque and unreadable, making the generated HTML
  harder to inspect and debug.

Most static site generators let authors specify IDs explicitly and fall
back to a slug derived from the heading text.  This gives authors control
while still providing human-readable, reasonably stable defaults.
"""


def main():
    print(__doc__)


if __name__ == "__main__":
    main()
