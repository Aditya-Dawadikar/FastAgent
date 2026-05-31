"""Helpers for integrating FastAgent context into LangGraph graph objects."""
from __future__ import annotations

from typing import Any

from fastagent._context import new_run_context, reset_run_context


def wrap_graph(graph: Any) -> Any:
    """Wrap a LangGraph graph so each invoke/stream resets FastAgent's iteration counters.

    Example
    -------
    >>> graph = wrap_graph(builder.compile())
    >>> graph.invoke(state)
    """
    original_invoke = graph.invoke
    original_stream = getattr(graph, "stream", None)
    original_ainvoke = getattr(graph, "ainvoke", None)
    original_astream = getattr(graph, "astream", None)

    def invoke(state: Any, *args: Any, **kwargs: Any) -> Any:
        token = new_run_context()
        try:
            return original_invoke(state, *args, **kwargs)
        finally:
            reset_run_context(token)

    graph.invoke = invoke

    if original_stream is not None:

        def stream(state: Any, *args: Any, **kwargs: Any) -> Any:
            token = new_run_context()
            try:
                yield from original_stream(state, *args, **kwargs)
            finally:
                reset_run_context(token)

        graph.stream = stream

    if original_ainvoke is not None:

        async def ainvoke(state: Any, *args: Any, **kwargs: Any) -> Any:
            token = new_run_context()
            try:
                return await original_ainvoke(state, *args, **kwargs)
            finally:
                reset_run_context(token)

        graph.ainvoke = ainvoke

    if original_astream is not None:

        async def astream(state: Any, *args: Any, **kwargs: Any) -> Any:
            token = new_run_context()
            try:
                async for chunk in original_astream(state, *args, **kwargs):
                    yield chunk
            finally:
                reset_run_context(token)

        graph.astream = astream

    return graph
