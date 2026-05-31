"""Integration-style tests for the @node decorator used without arguments."""

from fastagent import node


def test_bare_decorator_preserves_function_name():
    @node
    def my_planner(state):
        return {}

    assert my_planner.__name__ == "my_planner"


def test_factory_decorator_preserves_function_name():
    @node(retry=1)
    def my_planner(state):
        return {}

    assert my_planner.__name__ == "my_planner"


def test_bare_decorator_passes_state():
    @node
    def fn(state):
        return {"echo": state["x"]}

    assert fn({"x": 99}) == {"echo": 99}


def test_node_is_callable_without_arguments():
    @node
    def fn(state):
        return {}

    fn({})


def test_node_factory_with_no_options_is_transparent():
    original_calls = []

    @node()
    def fn(state):
        original_calls.append(state)
        return {"done": True}

    result = fn({"input": "hello"})
    assert result == {"done": True}
    assert original_calls == [{"input": "hello"}]


def test_combined_retry_timeout_fallback():
    import time

    @node(retry=1, timeout=0.05, fallback=lambda s: {"from": "fallback"})
    def slow_fn(state):
        time.sleep(5)
        return {}

    result = slow_fn({})
    assert result == {"from": "fallback"}
