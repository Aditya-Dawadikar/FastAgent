# FastAgent

**Production-ready reliability layer for LangGraph agents.**

[![CI](https://github.com/Aditya-Dawadikar/FastAgent/actions/workflows/ci.yml/badge.svg)](https://github.com/Aditya-Dawadikar/FastAgent/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/fastagent)](https://pypi.org/project/fastagent/)
[![Python](https://img.shields.io/pypi/pyversions/fastagent)](https://pypi.org/project/fastagent/)
[![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen)](https://github.com/Aditya-Dawadikar/FastAgent)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

---

Building a LangGraph agent is easy. Keeping it running reliably in production is not.

FastAgent adds retries, timeouts, fallbacks, and loop protection to any LangGraph node — with a single decorator. No new graph abstraction. No custom runtime. No DSL.

```python
@node(retry=3, timeout=10, fallback=backup_planner)
def planner(state):
    return llm.invoke(state["messages"])
```

---

## Installation

**From PyPI** (once published):

```bash
pip install fastagent
```

**Directly from GitHub** (latest `main`):

```bash
pip install git+https://github.com/Aditya-Dawadikar/FastAgent.git
```

**Pin to a specific commit** (recommended for production use before a stable release):

```bash
pip install git+https://github.com/Aditya-Dawadikar/FastAgent.git@<commit-sha>
```

**Editable install from a local clone** (for development or making local changes):

```bash
git clone https://github.com/Aditya-Dawadikar/FastAgent.git
cd FastAgent
pip install -e .
```

Requires Python 3.9+. FastAgent has **zero runtime dependencies** — LangGraph itself is optional.

---

## The problem

Most LangGraph applications end up reimplementing the same failure-handling patterns over and over:

```python
# Without FastAgent
def planner(state):
    for attempt in range(3):
        try:
            result = llm.invoke(state["messages"])
            return result
        except Exception:
            if attempt == 2:
                try:
                    return backup_llm.invoke(state["messages"])
                except Exception:
                    raise
```

This logic is noisy, easy to get wrong, and has to be repeated in every node.

FastAgent moves it into a decorator:

```python
# With FastAgent
@node(retry=3, fallback=backup_planner)
def planner(state):
    return llm.invoke(state["messages"])
```

---

## Features

### Retries

Automatically retry a failing node before giving up.

```python
@node(retry=3)
def planner(state):
    return llm.invoke(state["messages"])
```

`retry=3` means up to **4 total attempts** (1 original + 3 retries). If all attempts fail and no fallback is configured, the original exception is re-raised on a single attempt, or `AllRetriesExhausted` is raised when `retry > 0`.

---

### Timeouts

Prevent nodes from hanging indefinitely.

```python
@node(timeout=10)
def planner(state):
    return llm.invoke(state["messages"])
```

Raises `NodeTimeoutError` if execution exceeds the limit. Works on all platforms (implemented via `concurrent.futures`, not `signal.alarm`).

---

### Fallbacks

Route to a backup node when the primary exhausts all retries.

```python
def backup_planner(state):
    return cheap_llm.invoke(state["messages"])

@node(retry=2, fallback=backup_planner)
def planner(state):
    return expensive_llm.invoke(state["messages"])
```

The fallback receives the original state and its return value is used as-is.

---

### Loop protection

Stop runaway execution paths before they consume excessive resources.

```python
@node(max_iterations=5)
def planner(state):
    return llm.invoke(state["messages"])
```

Raises `MaxIterationsExceeded` when the node is called more than `max_iterations` times within a single graph run. Requires `wrap_graph()` or a manual `new_run_context()` call — see [LangGraph integration](#langgraph-integration) below.

---

### Combining primitives

All parameters compose freely:

```python
@node(
    retry=2,
    timeout=10,
    fallback=backup_planner,
    max_iterations=5,
)
def planner(state):
    return llm.invoke(state["messages"])
```

---

## LangGraph integration

Wrap your compiled graph with `wrap_graph()` to automatically reset iteration counters between runs:

```python
import fastagent
from langgraph.graph import StateGraph

builder = StateGraph(State)
builder.add_node("planner", planner)
# ... build your graph ...

graph = fastagent.wrap_graph(builder.compile())

# Each invoke() gets a fresh execution context
result = graph.invoke({"messages": [...]})
```

`wrap_graph()` patches `invoke`, `stream`, `ainvoke`, and `astream` — whichever the graph supports. If you prefer to manage the context yourself:

```python
token = fastagent.new_run_context()
try:
    result = graph.invoke(state)
finally:
    fastagent.reset_run_context(token)
```

---

## Error reference

| Exception | Raised when |
|---|---|
| `FastAgentError` | Base class for all FastAgent errors |
| `AllRetriesExhausted` | All retry attempts failed and no fallback is configured (`retry > 0`) |
| `NodeTimeoutError` | Node execution exceeded the configured `timeout` |
| `MaxIterationsExceeded` | Node was called more than `max_iterations` times in one run |

All exceptions are importable directly from `fastagent`:

```python
from fastagent import AllRetriesExhausted, NodeTimeoutError, MaxIterationsExceeded
```

---

## Design principles

**Simple** — FastAgent feels like adding decorators to existing LangGraph nodes. There is no new graph abstraction, no custom runtime, and no DSL.

**Lightweight** — Zero runtime dependencies. FastAgent sits between your application and LangGraph:

```
Your application
      │
      ▼
  FastAgent
      │
      ▼
  LangGraph
      │
      ▼
 LLMs / Tools
```

**Focused** — FastAgent handles production reliability concerns: retries, timeouts, fallbacks, and execution guards. Memory systems, vector databases, orchestration, and prompt management are out of scope.

---

## Roadmap

| Version | Features |
|---|---|
| **v0.1** | Retries, fallbacks, timeouts, loop protection |
| **v0.2** | Exponential backoff, retry policies, conditional fallbacks, failure hooks |
| **v0.3** | Cost budgets, token budgets, circuit breakers |
| **v0.4** | OpenTelemetry integration, execution traces, metrics export |

---

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for setup instructions, coding conventions, and the release process.

---

## License

MIT — see [LICENSE](LICENSE).
