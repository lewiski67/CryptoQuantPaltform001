from collections.abc import Callable


def assert_value_error(match: str, call: Callable[[], object]) -> None:
    try:
        call()
    except ValueError as exc:
        assert match in str(exc)
    else:
        raise AssertionError("ValueError was not raised")
