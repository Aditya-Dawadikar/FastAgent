"""FastAgent — production-ready reliability layer for LangGraph agents."""

from __future__ import annotations

from fastagent._context import new_run_context, reset_run_context
from fastagent._graph import wrap_graph
from fastagent.exceptions import (
    AllRetriesExhausted,
    FastAgentError,
    MaxIterationsExceeded,
    NodeTimeoutError,
)
from fastagent.node import node

__version__ = "0.1.0"

__all__ = [
    "node",
    "wrap_graph",
    "new_run_context",
    "reset_run_context",
    "FastAgentError",
    "AllRetriesExhausted",
    "MaxIterationsExceeded",
    "NodeTimeoutError",
]
