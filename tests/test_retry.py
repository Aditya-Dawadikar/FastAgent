import pytest
from fastagent import node
from fastagent.exceptions import AllRetriesExhausted


def test_no_retry_succeeds_on_first_call():
    @node
    def fn(state):
        return {"ok": True}

    assert fn({}) == {"ok": True}


def test_no_retry_raises_original_exception():
    @node
    def fn(state):
        raise ValueError("boom")

    # Single attempt (retry=0): original exception propagates directly, not wrapped.
    with pytest.raises(ValueError, match="boom"):
        fn({})


def test_retry_succeeds_on_second_attempt():
    calls = []

    @node(retry=1)
    def fn(state):
        calls.append(1)
        if len(calls) < 2:
            raise RuntimeError("transient")
        return {"ok": True}

    result = fn({})
    assert result == {"ok": True}
    assert len(calls) == 2


def test_retry_exhausted_raises_all_retries_exhausted():
    @node(retry=2)
    def fn(state):
        raise RuntimeError("always fails")

    with pytest.raises(AllRetriesExhausted) as exc_info:
        fn({})

    assert exc_info.value.attempts == 3
    assert isinstance(exc_info.value.last_error, RuntimeError)


def test_retry_zero_is_single_attempt():
    calls = []

    @node(retry=0)
    def fn(state):
        calls.append(1)
        raise ValueError("nope")

    # retry=0 → single attempt → original exception re-raised directly (not wrapped)
    with pytest.raises(ValueError, match="nope"):
        fn({})

    assert len(calls) == 1


def test_retry_passes_state_on_each_attempt():
    received = []

    @node(retry=2)
    def fn(state):
        received.append(state["x"])
        raise RuntimeError("fail")

    with pytest.raises(AllRetriesExhausted):
        fn({"x": 42})

    assert received == [42, 42, 42]
