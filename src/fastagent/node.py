"""The @node decorator — the primary public API for FastAgent."""
from __future__ import annotations

import functools
from typing import Any, Callable, Optional, TypeVar, overload

from fastagent._context import get_counter, increment_counter
from fastagent._timeout import call_with_timeout
from fastagent.exceptions import AllRetriesExhausted, MaxIterationsExceeded

F = TypeVar("F", bound=Callable[..., Any])


@overload
def node(fn: F) -> F: ...


@overload
def node(
    *,
    retry: int = 0,
    timeout: Optional[float] = None,
    fallback: Optional[Callable[..., Any]] = None,
    max_iterations: Optional[int] = None,
) -> Callable[[F], F]: ...


def node(
    fn: Optional[F] = None,
    *,
    retry: int = 0,
    timeout: Optional[float] = None,
    fallback: Optional[Callable[..., Any]] = None,
    max_iterations: Optional[int] = None,
) -> Any:
    """Wrap a LangGraph node with production reliability primitives.

    Parameters
    ----------
    retry:
        Number of additional attempts after the first failure (total attempts = retry + 1).
    timeout:
        Maximum seconds the node may run. Raises NodeTimeoutError on breach.
    fallback:
        Callable invoked with the original state when all retries are exhausted.
    max_iterations:
        Maximum times this node may be invoked within a single graph run.
        Requires the graph to be wrapped with fastagent.wrap_graph() or a
        manual call to fastagent.new_run_context() before each graph.invoke().
    """

    def decorator(func: F) -> F:
        node_name = func.__qualname__

        @functools.wraps(func)
        def wrapper(state: Any) -> Any:
            if max_iterations is not None:
                count = get_counter(node_name)
                if count >= max_iterations:
                    raise MaxIterationsExceeded(node_name, max_iterations)
                increment_counter(node_name)

            last_exc: Optional[BaseException] = None
            total_attempts = max(1, retry + 1)

            for _ in range(total_attempts):
                try:
                    if timeout is not None:
                        return call_with_timeout(func, state, timeout, node_name)
                    return func(state)
                except Exception as exc:
                    last_exc = exc

            if fallback is not None:
                return fallback(state)

            # Single attempt: re-raise directly so callers can catch the original error type.
            # Multiple attempts: wrap so callers know all retries were exhausted.
            if total_attempts == 1:
                raise last_exc  # type: ignore[misc]
            raise AllRetriesExhausted(node_name, total_attempts, last_exc)  # type: ignore[arg-type]

        return wrapper  # type: ignore[return-value]

    if fn is not None:
        return decorator(fn)

    return decorator
