from __future__ import annotations


class FastAgentError(Exception):
    """Base exception for all FastAgent errors."""


class MaxIterationsExceeded(FastAgentError):
    """Raised when a node exceeds its configured max_iterations limit."""

    def __init__(self, node_name: str, limit: int) -> None:
        self.node_name = node_name
        self.limit = limit
        super().__init__(f"Node '{node_name}' exceeded max_iterations={limit}")


class NodeTimeoutError(FastAgentError):
    """Raised when a node execution exceeds its configured timeout."""

    def __init__(self, node_name: str, timeout: float) -> None:
        self.node_name = node_name
        self.timeout = timeout
        super().__init__(f"Node '{node_name}' timed out after {timeout}s")


class AllRetriesExhausted(FastAgentError):
    """Raised when a node fails all retry attempts and no fallback is configured."""

    def __init__(self, node_name: str, attempts: int, last_error: BaseException) -> None:
        self.node_name = node_name
        self.attempts = attempts
        self.last_error = last_error
        super().__init__(f"Node '{node_name}' failed after {attempts} attempt(s): {last_error}")
