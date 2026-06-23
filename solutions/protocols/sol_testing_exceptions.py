"""Solution: a context manager that works like pytest.raises."""


class ExpectRaises:
    """Context manager that checks for an expected exception.

    If the expected exception is raised inside the ``with`` block,
    it is silently suppressed.  If no exception is raised, an
    ``AssertionError`` is raised.  If a different exception is raised,
    it propagates normally.
    """

    def __init__(self, expected):
        self.expected = expected

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        if exc_type is None:
            raise AssertionError(
                f"expected {self.expected.__name__} but no exception was raised"
            )
        if issubclass(exc_type, self.expected):
            return True  # suppress the expected exception
        return False  # let other exceptions propagate


# --------------------------------------------------------------------
# Demo / self-test
# --------------------------------------------------------------------
if __name__ == "__main__":
    # Should pass: the expected exception is raised.
    with ExpectRaises(ValueError):
        raise ValueError("something went wrong")
    print("✓ ValueError correctly caught and suppressed")

    # Should pass: a subclass of the expected exception.
    with ExpectRaises(LookupError):
        raise KeyError("missing key")
    print("✓ KeyError (a LookupError subclass) correctly caught")

    # Should fail: no exception raised.
    try:
        with ExpectRaises(ValueError):
            pass  # no exception → AssertionError
    except AssertionError as exc:
        print(f"✓ AssertionError raised when no exception: {exc}")

    # Should fail: wrong exception type.
    try:
        with ExpectRaises(ValueError):
            raise TypeError("wrong type")
    except TypeError:
        print("✓ TypeError propagated normally (not the expected type)")
