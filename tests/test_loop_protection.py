import pytest

import fastagent
from fastagent import node
from fastagent.exceptions import MaxIterationsExceeded


def test_max_iterations_blocks_after_limit():
    @node(max_iterations=3)
    def fn(state):
        return {"ok": True}

    fn({})
    fn({})
    fn({})

    with pytest.raises(MaxIterationsExceeded) as exc_info:
        fn({})

    assert exc_info.value.limit == 3
    assert "fn" in exc_info.value.node_name


def test_max_iterations_resets_across_contexts():
    @node(max_iterations=1)
    def fn(state):
        return {}

    fn({})

    with pytest.raises(MaxIterationsExceeded):
        fn({})

    # New context — counter resets
    token = fastagent.new_run_context()
    try:
        fn({})  # Should succeed
    finally:
        fastagent.reset_run_context(token)


def test_max_iterations_independent_per_node():
    @node(max_iterations=1)
    def node_a(state):
        return {}

    @node(max_iterations=1)
    def node_b(state):
        return {}

    node_a({})
    node_b({})  # Different node — should not be blocked


def test_max_iterations_no_context_does_not_raise():
    """Without a run context (ContextVar is None), max_iterations never blocks."""
    from fastagent._context import _run_counters

    # Force the context to None, overriding the autouse fixture.
    token = _run_counters.set(None)
    try:

        @node(max_iterations=1)
        def fn(state):
            return {}

        fn({})
        fn({})  # No context - counter is always 0, never blocks
    finally:
        _run_counters.reset(token)


def test_max_iterations_error_message():
    @node(max_iterations=2)
    def my_node(state):
        return {}

    my_node({})
    my_node({})

    with pytest.raises(MaxIterationsExceeded) as exc_info:
        my_node({})

    assert "max_iterations=2" in str(exc_info.value)
    assert "my_node" in str(exc_info.value)
