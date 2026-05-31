# FastAgent

**Build reliable LangGraph agents without writing reliability code.**

FastAgent is a lightweight reliability layer for LangGraph that provides production-ready execution primitives such as retries, fallbacks, timeouts, and loop protection.

Instead of repeatedly implementing error handling and recovery logic inside every node, developers can focus on agent behavior while FastAgent handles common failure scenarios.

---

## Why FastAgent?

Building an agent is easy.

Keeping an agent running reliably in production is not.

Common failure modes include:

* LLMs returning malformed outputs
* Tool execution failures
* API rate limits
* Network interruptions
* Infinite agent loops
* Long-running or stalled operations
* Temporary model provider outages

Most LangGraph applications end up reimplementing the same reliability patterns over and over again.

FastAgent provides these patterns out of the box.

---

## Features

### Retries

Automatically retry failed node executions.

```python
@node(
    retry=3
)
def planner(state):
    ...
```

---

### Fallbacks

Route execution to backup nodes when primary execution fails.

```python
@node(
    fallback=backup_planner
)
def planner(state):
    ...
```

---

### Timeouts

Prevent agents from hanging indefinitely.

```python
@node(
    timeout=10
)
def planner(state):
    ...
```

---

### Loop Protection

Terminate runaway execution paths before they consume excessive resources.

```python
@node(
    max_iterations=5
)
def planner(state):
    ...
```

---

## Example

Without FastAgent:

```python
def planner(state):
    try:
        result = llm.invoke(...)
        return result
    except Exception:
        try:
            result = backup_llm.invoke(...)
            return result
        except Exception:
            raise
```

With FastAgent:

```python
@node(
    retry=3,
    timeout=10,
    fallback=backup_planner
)
def planner(state):
    return llm.invoke(...)
```

---

## Design Principles

### Simple

FastAgent should feel like adding decorators to existing LangGraph nodes.

No new graph abstraction.

No custom runtime.

No DSL.

---

### Lightweight

FastAgent sits on top of LangGraph.

```text
Application
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

Developers continue using LangGraph exactly as they do today.

---

### Reliability First

FastAgent focuses on production concerns:

* Retry policies
* Fallback strategies
* Timeouts
* Execution safeguards

Not:

* Memory systems
* Vector databases
* Agent orchestration
* Prompt management

Those problems are already being solved elsewhere.

---

## Roadmap

### v0.1

* Node retries
* Fallback execution
* Timeouts
* Loop protection

### v0.2

* Exponential backoff
* Retry policies
* Conditional fallbacks
* Failure hooks

### v0.3

* Cost budgets
* Token budgets
* Execution guards
* Circuit breakers

### v0.4

* OpenTelemetry integration
* Execution traces
* Metrics export

---

## Motivation

React Query simplified data fetching by moving common engineering concerns into a reusable abstraction.

FastAgent aims to do the same for agent reliability.

Instead of spending time writing boilerplate retry loops, fallback handlers, timeout management, and execution guards, developers can focus on building agent workflows.

---

## Status

🚧 Early Development

FastAgent is currently focused on validating a minimal set of reliability primitives for LangGraph applications.

Feedback and contributions are welcome.
