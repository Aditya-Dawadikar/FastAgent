import time

import pytest

from fastagent import node
from fastagent.exceptions import AllRetriesExhausted, NodeTimeoutError


def test_timeout_does_not_fire_for_fast_node():
    @node(timeout=2.0)
    def fn(state):
        return {"ok": True}

    assert fn({}) == {"ok": True}


def test_timeout_raises_node_timeout_error():
    @node(timeout=0.1)
    def fn(state):
        time.sleep(5)
        return {}

    with pytest.raises(NodeTimeoutError) as exc_info:
        fn({})

    assert exc_info.value.timeout == 0.1
    assert "fn" in exc_info.value.node_name


def test_timeout_error_has_correct_node_name():
    @node(timeout=0.05)
    def my_slow_node(state):
        time.sleep(5)
        return {}

    with pytest.raises(NodeTimeoutError) as exc_info:
        my_slow_node({})

    assert "my_slow_node" in exc_info.value.node_name


def test_timeout_combined_with_retry():
    call_times = []

    @node(retry=1, timeout=0.1)
    def fn(state):
        call_times.append(time.monotonic())
        time.sleep(5)
        return {}

    # retry=1 → 2 attempts, both time out → AllRetriesExhausted wrapping NodeTimeoutError
    with pytest.raises(AllRetriesExhausted) as exc_info:
        fn({})

    assert isinstance(exc_info.value.last_error, NodeTimeoutError)
    assert len(call_times) == 2


def test_timeout_combined_with_fallback():
    @node(timeout=0.05, fallback=lambda s: {"source": "fallback"})
    def fn(state):
        time.sleep(5)
        return {}

    result = fn({})
    assert result == {"source": "fallback"}
