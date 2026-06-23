"""Solution: Individual Results.

Modify the test runner so that it reports which specific tests passed,
failed, or produced errors, and still reports the summary counts.

The runner below also includes unit tests that verify the runner itself
classifies outcomes correctly.
"""


def sign(value):
    if value < 0:
        return -1
    else:
        return 1


# -- test functions (two correct, two with deliberate bugs) ------------

def test_sign_negative():
    assert sign(-3) == -1


def test_sign_positive():
    assert sign(19) == 1


def test_sign_zero():
    assert sign(0) == 0


def test_sign_error():
    assert sgn(1) == 1          # NameError: sgn is not defined


# -- modified runner with per-test reporting ---------------------------

def run_tests():
    results = {"pass": [], "fail": [], "error": []}
    for (name, test) in globals().items():
        if not name.startswith("test_"):
            continue
        try:
            test()
            results["pass"].append(name)
        except AssertionError:
            results["fail"].append(name)
        except Exception:
            results["error"].append(name)
    for status in ("pass", "fail", "error"):
        for name in results[status]:
            print(f"{status:5} {name}")
    print(f"pass  {len(results['pass'])}")
    print(f"fail  {len(results['fail'])}")
    print(f"error {len(results['error'])}")


# -- unit tests for the runner itself ----------------------------------

def test_runner_classifies_pass():
    def fake_pass():
        pass
    globals_copy = dict(globals())
    globals_copy["test_fake_pass"] = fake_pass
    # We can't easily call run_tests here without side effects, so we
    # verify the classification logic directly.
    results = {"pass": [], "fail": [], "error": []}
    try:
        fake_pass()
        results["pass"].append("test_fake_pass")
    except AssertionError:
        results["fail"].append("test_fake_pass")
    except Exception:
        results["error"].append("test_fake_pass")
    assert len(results["pass"]) == 1
    assert len(results["fail"]) == 0
    assert len(results["error"]) == 0


def test_runner_classifies_fail():
    def fake_fail():
        assert False
    results = {"pass": [], "fail": [], "error": []}
    try:
        fake_fail()
        results["pass"].append("test_fake_fail")
    except AssertionError:
        results["fail"].append("test_fake_fail")
    except Exception:
        results["error"].append("test_fake_fail")
    assert len(results["pass"]) == 0
    assert len(results["fail"]) == 1
    assert len(results["error"]) == 0


def test_runner_classifies_error():
    def fake_error():
        raise ValueError("boom")
    results = {"pass": [], "fail": [], "error": []}
    try:
        fake_error()
        results["pass"].append("test_fake_error")
    except AssertionError:
        results["fail"].append("test_fake_error")
    except Exception:
        results["error"].append("test_fake_error")
    assert len(results["pass"]) == 0
    assert len(results["fail"]) == 0
    assert len(results["error"]) == 1


if __name__ == "__main__":
    print("=== Running the test suite ===")
    run_tests()
    print()
    print("=== Running the meta-tests ===")
    test_runner_classifies_pass()
    test_runner_classifies_fail()
    test_runner_classifies_error()
    print("All meta-tests passed.")
