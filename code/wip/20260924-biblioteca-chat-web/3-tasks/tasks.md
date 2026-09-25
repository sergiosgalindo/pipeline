# Development Plan

Status: multilingual embedding retrieval implemented and evaluated; provider-backed and browser verification pending

This plan was written in brownfield mode after the first version had been built. Completed tasks describe what is already present in the working tree; pending tasks are work that remains unverified or unimplemented.

## Tasks

- [x] TASK-001: Define the MVC structure and FastAPI entry point.
  - Depends on: none
  - Deliverable: `app/main.py`, controllers, models, and Pydantic schemas.
  - Validate: Python modules compile successfully.
- [x] TASK-002: Implement policy retrieval and answer generation.
  - Depends on: TASK-001
  - Deliverable: `knowledge_base.json` loading, semantic embedding ranking, abstention without context, and server-side Groq integration.
  - Validate: flow and syntax reviewed; a live provider walkthrough remains pending.
- [x] TASK-003: Build the responsive chat view.
  - Depends on: TASK-001
  - Deliverable: Bootstrap view, futuristic theme, suggestions, message sending, sources, and desktop/mobile reset controls.
  - Validate: `node --check` passed; visual browser inspection remains pending.
- [x] TASK-004: Document configuration and local execution.
  - Depends on: TASK-001, TASK-002, TASK-003
  - Deliverable: `requirements.txt`, README, and SDD package with specifications, tasks, progress, and implementation map.
  - Validate: installation and startup instructions documented.
- [ ] TASK-005: Install dependencies and verify startup/API contracts.
  - Depends on: TASK-004
  - Deliverable: run Uvicorn and check `/`, `/api/health`, and `/api/chat` with a valid key.
  - Validate: expected HTTP responses and a demo query returns a source.
- [ ] TASK-006: Inspect the interface on desktop and mobile viewports.
  - Depends on: TASK-005
  - Deliverable: render evidence and review of overflow, composer, and scrolling.
  - Validate: both viewport sizes work, and chat can be used with keyboard and touch.
- [x] TASK-007: Replace lexical policy search with multilingual embedding retrieval.
  - Depends on: TASK-001, TASK-002
  - Deliverable: configurable Sentence Transformers embeddings, cached policy vectors, cosine similarity ranking, and a relevance threshold.
  - Validate: deterministic integration tests pass; representative Spanish paraphrases retrieve the expected policy and an out-of-corpus question is declined with the configured model.
- [ ] TASK-008: Cap the browser-submitted chat history at the API limit.
  - Depends on: TASK-003
  - Deliverable: send no more than the latest 12 history messages from `web/app.js`, matching `ChatRequest` validation.
  - Validate: continue a conversation past seven exchanges; requests remain accepted and the newest context is retained.
- [ ] TASK-009: Package the web app as a Docker container.
  - Depends on: TASK-001, TASK-002, TASK-003
  - Deliverable: root `Dockerfile`, `.dockerignore`, and English run instructions using runtime environment configuration.
  - Validate: build the image, run it with `.env` supplied at runtime, and check the root and health endpoints.
- [x] TASK-010: Add HTTP integration tests for the web and assistant request flow.
  - Depends on: TASK-001, TASK-002, TASK-003
  - Deliverable: development test dependencies and tests for page/static assets, health configuration, request validation, RAG source selection, abstention, and provider failures.
  - Validate: `python -m pytest` passes without making a live Groq request.
