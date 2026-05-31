import pytest
from fastagent import node
from fastagent.exceptions import AllRetriesExhausted


def backup(state):
    return {"source": "fallback"}


def test_fallback_invoked_when_primary_fails():
    @node(fallback=backup)
    def primary(state):
        raise RuntimeError("fail")

    result = primary({})
    assert result == {"source": "fallback"}


def test_fallback_not_invoked_when_primary_succeeds():
    @node(fallback=backup)
    def primary(state):
        return {"source": "primary"}

    result = primary({})
    assert result == {"source": "primary"}


def test_fallback_invoked_after_all_retries():
    calls = []

    @node(retry=2, fallback=backup)
    def primary(state):
        calls.append(1)
        raise RuntimeError("fail")

    result = primary({})
    assert result == {"source": "fallback"}
    assert len(calls) == 3


def test_fallback_receives_original_state():
    received = {}

    def capturing_fallback(state):
        received.update(state)
        return {}

    @node(fallback=capturing_fallback)
    def primary(state):
        raise RuntimeError("fail")

    primary({"key": "value"})
    assert received == {"key": "value"}


def test_no_fallback_raises_when_exhausted():
    @node(retry=1)
    def primary(state):
        raise RuntimeError("fail")

    with pytest.raises(AllRetriesExhausted):
        primary({})


def test_fallback_error_propagates():
    def bad_fallback(state):
        raise ValueError("fallback also failed")

    @node(fallback=bad_fallback)
    def primary(state):
        raise RuntimeError("primary failed")

    with pytest.raises(ValueError, match="fallback also failed"):
        primary({})
