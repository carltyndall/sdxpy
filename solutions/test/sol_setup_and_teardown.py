"""Solution: Setup and Teardown.

Extend the test runner so that if a function named 'setup' exists it is
called before each test, and if a function named 'teardown' exists it is
called after each test (in a finally block so it always runs).
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


# -- setup and teardown ------------------------------------------------

def setup():
    print("  setup called")


def teardown():
    print("  teardown called")


# -- modified runner ---------------------------------------------------

def run_tests():
    results = {"pass": 0, "fail": 0, "error": 0}
    setup_func = globals().get("setup")
    teardown_func = globals().get("teardown")
    for (name, test) in globals().items():
        if not name.startswith("test_"):
            continue
        try:
            if setup_func:
                setup_func()
            test()
            results["pass"] += 1
        except AssertionError:
            results["fail"] += 1
        except Exception:
            results["error"] += 1
        finally:
            if teardown_func:
                teardown_func()
    print(f"pass  {results['pass']}")
    print(f"fail  {results['fail']}")
    print(f"error {results['error']}")


if __name__ == "__main__":
    run_tests()
