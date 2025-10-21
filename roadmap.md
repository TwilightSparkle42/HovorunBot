# AskBro Improvement Roadmap

## 1. Handler Orchestration & Extensibility
- [ ] Build a handler pipeline coordinator that resolves dependencies once, supports multiple handler executions per
  update, and removes the per-module tuple management.
- [ ] Replace ad-hoc `print` diagnostics with structured logging hooked into the existing logger to keep telemetry
  consistent across environments.
- [ ] Introduce handler auto-discovery (entry points or module scanning) so adding a handler only requires defining the
  class.

## 2. Chat-Level AI Configuration
- [ ] Extend chat persistence to store system prompts, default model, and sampling parameters so each chat can tune
  behaviour.
- [ ] Update AI-facing handlers to hydrate prompts/settings from chat config instead of relying on hard-coded strings.
- [ ] Add validation/admin tooling (commands or control panel) for managing chat-specific AI profiles.
- [ ] Expose commands or other self-service flows so chats can update configuration without direct database access.

## 3. Async-Safe Infrastructure
- [x] Move synchronous SQLAlchemy calls off the event loop (use `async_session` or run blocking I/O in a thread executor)
  to keep message processing responsive. (resolved: repository now uses SQLAlchemy's async engine + session factory)
- [x] Swap blocking HTTP clients (e.g., `requests` in `InfermaticAiClient`) for async equivalents to avoid stalling the
  bot during provider calls. (resolved: `InfermaticAiClient` now uses `httpx.AsyncClient`)
- [ ] Add timeouts/retry policies around external I/O so the runtime can degrade gracefully.

## 4. Observability & Testing
- [ ] Standardize logging levels/format and surface handler metrics (latency, invocation counts) for easier production
  troubleshooting.
- [ ] Backfill unit tests around the new handler pipeline and AI client selection logic.
- [ ] Wire existing linting/type-checking (ruff, mypy) into CI so regressions are caught automatically.

## 5. Future Enhancements
- [ ] Allow per-chat command configuration (e.g., opt-in summary keywords, localized triggers).
- [ ] Capture conversation snapshots for analytics once handler orchestration supports side-channel processing.
- [ ] Explore queueing or rate-limiting per provider to manage API budget and avoid hitting rate limits.
- [ ] Build a lightweight web admin panel for managing chat access records and AI configuration.
- [ ] Evaluate long-term database options so the service can migrate away from SQLite when requirements evolve.
