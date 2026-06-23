"""Solution: Finding Functions.

Modify the test runner so that it uses callable() to verify that each
name starting with 'test_' actually refers to something callable.
Non-callable objects with 'test_' names are silently skipped.

The script also demonstrates what happens when a non-callable 'test_'
name is defined at module level.
"""


def sign(value):
    if value < 0:
        return -1
    else:
        return 1


# -- test functions ----------------------------------------------------

def test_sign_negative():
    assert sign(-3) == -1


def test_sign_positive():
    assert sign(19) == 1


def test_sign_zero():
    assert sign(0) == 0


def test_sign_error():
    assert sgn(1) == 1          # deliberate NameError


# -- non-callable with a 'test_' name (should be skipped) --------------

test_data = [1, 2, 3]           # not a function; callable() returns False


# -- modified runner ---------------------------------------------------

def run_tests():
    results = {"pass": 0, "fail": 0, "error": 0}
    for (name, obj) in globals().items():
        if not name.startswith("test_"):
            continue
        if not callable(obj):
            print(f"skip   {name} (not callable)")
            continue
        try:
            obj()
            results["pass"] += 1
        except AssertionError:
            results["fail"] += 1
        except Exception:
            results["error"] += 1
    print(f"pass  {results['pass']}")
    print(f"fail  {results['fail']}")
    print(f"error {results['error']}")


if __name__ == "__main__":
    run_tests()
