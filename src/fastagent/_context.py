"""
Execution context for tracking per-run node invocation counts.

FastAgent uses a contextvars.ContextVar to isolate iteration counters
per graph execution. Call `new_run_context()` at the start of each graph
invocation to get a fresh context token, and `reset_run_context(token)` when
the run completes.

When using LangGraph, wrap your graph with `fastagent.wrap_graph()` to have
this managed automatically.
"""
from __future__ import annotations

import contextvars

_run_counters: contextvars.ContextVar[dict[str, int] | None] = contextvars.ContextVar(
    "fastagent_run_counters", default=None
)


def new_run_context() -> contextvars.Token[dict[str, int] | None]:
    """Start a new isolated execution context. Returns a token for cleanup."""
    return _run_counters.set({})


def reset_run_context(token: contextvars.Token[dict[str, int] | None]) -> None:
    """Restore the previous context state using the token from new_run_context()."""
    _run_counters.reset(token)


def get_counter(node_id: str) -> int:
    counters = _run_counters.get()
    if counters is None:
        return 0
    return counters.get(node_id, 0)


def increment_counter(node_id: str) -> int:
    counters = _run_counters.get()
    if counters is None:
        return 0
    count = counters.get(node_id, 0) + 1
    counters[node_id] = count
    return count
