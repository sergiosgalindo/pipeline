# Functional Specification

Status: aligned with the current 27-policy corpus and embedding retrieval

## Problem

Library users need a simple conversational way to ask about library policies. The assistant must ground its answers in configured information and acknowledge when it lacks enough information.

## Users

- **Visitor:** asks about the configured library policies on desktop or mobile, including loans, fines, hours, rooms, access, and the other topics in the knowledge base.
- **Content owner:** updates the knowledge base policies.
- **Operator/developer:** configures the Groq API key and starts the service.

## User Stories

- As a visitor, I want to ask a question in chat and receive a concise answer in Spanish.
- As a visitor, I want to see which policy was used to answer.
- As a visitor, I want to start a new conversation and use suggested questions.
- As a visitor, I want the assistant to abstain when the available knowledge base does not cover my question.
- As a content owner, I want to add or edit policies without changing the interface code.
- As an operator, I want to configure the Groq key on the server without exposing it to the browser.

## Acceptance Criteria

- The root route serves a Spanish chat interface.
- The chat shows suggestions, supports sending with the button or Enter, retains recent context during the browser session, and can be reset.
- The interface adapts to desktop and mobile; mobile provides access to conversation reset.
- The backend accepts messages at `POST /api/chat`, retrieves policy context, and returns an answer with the titles of retrieved sources.
- Policy retrieval uses multilingual text embeddings and semantic similarity so relevant policies can be found from paraphrased Spanish questions.
- Requests outside the available knowledge receive an abstention response.
- The Groq key is read from the server environment and is not included in normal HTTP responses or client assets.
- Message and history lengths are validated; configuration and provider errors produce understandable HTTP errors.
- The browser sends no more than the latest 12 history messages accepted by the API. The on-screen conversation can be longer; only the request payload is capped.
- The application can be built and run as a container, with the provider key supplied at runtime and excluded from the image.
- `GET /api/health` reports basic service status and whether the key is configured.

## Edge Cases

- Empty, whitespace-only, oversized, or invalid-JSON requests.
- A question with no relevant terms in the current corpus.
- An embedding similarity score below the configured relevance threshold.
- The embedding model cannot be loaded or returns invalid vectors.
- Missing `GROQ_API_KEY`, an HTTP error from Groq, or a provider timeout.
- Missing history or a reset conversation.
- Missing or invalid JSON knowledge file.

## Out Of Scope

- Authentication, authorization, user profiles, persistent conversation storage, and an administration panel.
- Public deployment, domain, HTTPS, production observability, and per-user rate limits.
- Container orchestration and production deployment configuration.
- Policy generation or legal/financial advice.
- Using the TinyLlama LoRA adapter in the current web request path.
- News browsing or external web search.
