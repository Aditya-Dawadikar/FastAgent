"""Cross-platform timeout implementation using a thread pool executor."""
from __future__ import annotations

import concurrent.futures
from typing import Any, Callable

from fastagent.exceptions import NodeTimeoutError


def call_with_timeout(fn: Callable[..., Any], state: Any, seconds: float, node_name: str) -> Any:
    """Execute fn(state) and raise NodeTimeoutError if it exceeds seconds."""
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(fn, state)
        try:
            return future.result(timeout=seconds)
        except concurrent.futures.TimeoutError:
            raise NodeTimeoutError(node_name, seconds) from None
