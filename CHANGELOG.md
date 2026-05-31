# Changelog

All notable changes to FastAgent will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
FastAgent uses [Semantic Versioning](https://semver.org/).

---

## [Unreleased]

---

## [0.1.0] — 2026-05-30

### Added

- `@node` decorator with `retry`, `timeout`, `fallback`, and `max_iterations` parameters
- Cross-platform timeout implementation via `concurrent.futures`
- `wrap_graph()` helper for automatic execution context management with LangGraph
- `new_run_context()` / `reset_run_context()` for manual context control
- `FastAgentError`, `AllRetriesExhausted`, `NodeTimeoutError`, `MaxIterationsExceeded` exceptions
- Full type annotations and `py.typed` marker (PEP 561)
- 90%+ test coverage across all reliability primitives

[Unreleased]: https://github.com/aditya-dawadikar/FastAgent/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/aditya-dawadikar/FastAgent/releases/tag/v0.1.0
