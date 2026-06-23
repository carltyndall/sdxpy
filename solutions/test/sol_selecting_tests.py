"""Solution: Selecting Tests.

Extend the test runner so that '-s <pattern>' or '--select <pattern>' on
the command line restricts execution to tests whose names contain the
given pattern.
"""

import sys


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


# -- modified runner ---------------------------------------------------

def run_tests():
    pattern = None
    args = sys.argv[1:]
    for i, arg in enumerate(args):
        if arg in ("-s", "--select") and i + 1 < len(args):
            pattern = args[i + 1]
            break

    results = {"pass": 0, "fail": 0, "error": 0}
    for (name, test) in globals().items():
        if not name.startswith("test_"):
            continue
        if pattern and pattern not in name:
            continue
        try:
            test()
            results["pass"] += 1
        except AssertionError:
            results["fail"] += 1
        except Exception:
            results["error"] += 1

    if pattern:
        print(f"pattern: '{pattern}'")
    print(f"pass  {results['pass']}")
    print(f"fail  {results['fail']}")
    print(f"error {results['error']}")


if __name__ == "__main__":
    run_tests()
