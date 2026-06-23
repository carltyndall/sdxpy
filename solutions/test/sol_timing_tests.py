"""Solution: Timing Tests.

Extend the test runner so that it records how long each test takes to run,
reporting elapsed time in milliseconds alongside the result.
"""

import time


def sign(value):
    if value < 0:
        return -1
    else:
        return 1


# -- test functions (one deliberately slow) ----------------------------

def test_sign_negative():
    assert sign(-3) == -1


def test_sign_positive():
    assert sign(19) == 1


def test_sign_zero():
    assert sign(0) == 0


def test_sign_error():
    assert sgn(1) == 1          # deliberate NameError


def test_deliberately_slow():
    time.sleep(0.15)
    assert True


# -- modified runner ---------------------------------------------------

def run_tests():
    results = {"pass": 0, "fail": 0, "error": 0}
    for (name, test) in globals().items():
        if not name.startswith("test_"):
            continue
        start = time.time()
        try:
            test()
            results["pass"] += 1
            status = "pass"
        except AssertionError:
            results["fail"] += 1
            status = "fail"
        except Exception:
            results["error"] += 1
            status = "error"
        elapsed = (time.time() - start) * 1000
        print(f"{status:5} {name} ({elapsed:.2f} ms)")
    print(f"pass  {results['pass']}")
    print(f"fail  {results['fail']}")
    print(f"error {results['error']}")


if __name__ == "__main__":
    run_tests()
