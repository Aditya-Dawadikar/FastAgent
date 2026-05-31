"""Tests for wrap_graph() — uses a lightweight mock instead of a real LangGraph graph."""
import pytest
import fastagent
from fastagent import node, wrap_graph
from fastagent.exceptions import MaxIterationsExceeded


class _FakeGraph:
    """Minimal stand-in for a LangGraph compiled graph (sync + async)."""

    def __init__(self, invoke_fn=None, stream_results=None):
        self._invoke_fn = invoke_fn or (lambda s, **kw: s)
        self._stream_results = stream_results or [{}]

    def invoke(self, state, **kwargs):
        return self._invoke_fn(state, **kwargs)

    def stream(self, state, **kwargs):
        yield from self._stream_results

    async def ainvoke(self, state, **kwargs):
        return self._invoke_fn(state, **kwargs)

    async def astream(self, state, **kwargs):
        for chunk in self._stream_results:
            yield chunk


def test_wrap_graph_returns_same_graph_object():
    graph = _FakeGraph()
    result = wrap_graph(graph)
    assert result is graph


def test_wrap_graph_invoke_still_works():
    graph = _FakeGraph(invoke_fn=lambda s, **kw: {**s, "done": True})
    wrap_graph(graph)
    result = graph.invoke({"x": 1})
    assert result == {"x": 1, "done": True}


def test_wrap_graph_resets_iteration_counters_between_invocations():
    @node(max_iterations=1)
    def guarded(state):
        return state

    def run(state, **kwargs):
        return guarded(state)

    graph = _FakeGraph(invoke_fn=run)
    wrap_graph(graph)

    graph.invoke({})   # first run — counter reaches 1
    graph.invoke({})   # second run — counter should reset to 0, so this succeeds


def test_wrap_graph_max_iterations_still_blocks_within_single_run():
    @node(max_iterations=1)
    def guarded(state):
        return state

    def run(state, **kwargs):
        guarded(state)
        guarded(state)  # second call in the same run — should be blocked

    graph = _FakeGraph(invoke_fn=run)
    wrap_graph(graph)

    with pytest.raises(MaxIterationsExceeded):
        graph.invoke({})


def test_wrap_graph_stream_still_yields():
    graph = _FakeGraph(stream_results=[{"a": 1}, {"b": 2}])
    wrap_graph(graph)
    chunks = list(graph.stream({}))
    assert chunks == [{"a": 1}, {"b": 2}]


def test_wrap_graph_stream_resets_counters_between_calls():
    @node(max_iterations=1)
    def guarded(state):
        return state

    def make_stream(state, **kwargs):
        guarded(state)
        yield state

    graph = _FakeGraph()
    graph.stream = make_stream  # type: ignore[assignment]
    wrap_graph(graph)

    list(graph.stream({}))  # first stream run
    list(graph.stream({}))  # second — counter should be fresh


@pytest.mark.asyncio
async def test_wrap_graph_ainvoke_still_works():
    graph = _FakeGraph(invoke_fn=lambda s, **kw: {**s, "async": True})
    wrap_graph(graph)
    result = await graph.ainvoke({"x": 1})
    assert result == {"x": 1, "async": True}


@pytest.mark.asyncio
async def test_wrap_graph_ainvoke_resets_counters_between_runs():
    @node(max_iterations=1)
    def guarded(state):
        return state

    graph = _FakeGraph(invoke_fn=lambda s, **kw: guarded(s))
    wrap_graph(graph)

    await graph.ainvoke({})   # first run
    await graph.ainvoke({})   # second — counter should be fresh


@pytest.mark.asyncio
async def test_wrap_graph_astream_yields_chunks():
    graph = _FakeGraph(stream_results=[{"a": 1}, {"b": 2}])
    wrap_graph(graph)
    chunks = [chunk async for chunk in graph.astream({})]
    assert chunks == [{"a": 1}, {"b": 2}]


@pytest.mark.asyncio
async def test_wrap_graph_astream_resets_counters_between_runs():
    @node(max_iterations=1)
    def guarded(state):
        return state

    async def make_astream(state, **kwargs):
        guarded(state)
        yield state

    graph = _FakeGraph()
    graph.astream = make_astream  # type: ignore[assignment]
    wrap_graph(graph)

    async for _ in graph.astream({}):
        pass
    async for _ in graph.astream({}):  # counter resets between calls
        pass
