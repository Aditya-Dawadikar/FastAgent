"""
Minimal example: FastAgent reliability decorators on LangGraph nodes.

Run this file directly — it does not require a real LLM.
"""
from __future__ import annotations

import fastagent
from fastagent import node
from fastagent.exceptions import AllRetriesExhausted, MaxIterationsExceeded


# --- Node definitions ---

@node(retry=2, timeout=5.0)
def planner(state: dict) -> dict:
    """Primary planning node. Retries up to 2 times, times out after 5s."""
    print(f"  planner called with: {state}")
    # In production this would call an LLM:
    # return llm.invoke(state["messages"])
    return {**state, "plan": "step-by-step plan"}


def backup_planner(state: dict) -> dict:
    """Fallback used when the primary planner exhausts all retries."""
    print("  backup_planner invoked (fallback)")
    return {**state, "plan": "simplified fallback plan"}


@node(retry=1, fallback=backup_planner)
def planner_with_fallback(state: dict) -> dict:
    raise RuntimeError("Simulated LLM failure")


@node(max_iterations=3)
def loop_guarded_node(state: dict) -> dict:
    print(f"  loop_guarded_node call #{state.get('count', 0) + 1}")
    return {**state, "count": state.get("count", 0) + 1}


# --- Demo ---

def main() -> None:
    print("\n=== Basic retry + timeout ===")
    token = fastagent.new_run_context()
    result = planner({"messages": ["hello"]})
    fastagent.reset_run_context(token)
    print(f"Result: {result}\n")

    print("=== Retry exhausted -> fallback ===")
    token = fastagent.new_run_context()
    result = planner_with_fallback({"messages": ["hello"]})
    fastagent.reset_run_context(token)
    print(f"Result: {result}\n")

    print("=== Loop protection ===")
    token = fastagent.new_run_context()
    state: dict = {}
    try:
        for _ in range(5):
            state = loop_guarded_node(state)
    except MaxIterationsExceeded as exc:
        print(f"Caught: {exc}")
    finally:
        fastagent.reset_run_context(token)
    print()

    print("=== Using wrap_graph() (LangGraph integration) ===")
    print("  (Skipped — requires langgraph installed)")
    print("  Install with: pip install fastagent[langgraph]")


if __name__ == "__main__":
    main()
