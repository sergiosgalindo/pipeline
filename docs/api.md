# HTTP API

The canonical machine-readable contract is [`openapi.yaml`](openapi.yaml). The running FastAPI app also generates Swagger UI at `/docs`, ReDoc at `/redoc`, and OpenAPI JSON at `/openapi.json`.

Base URL for local development: `http://127.0.0.1:8000`.

## `GET /api/health`

Returns basic process/configuration status. `configured` only indicates whether `GROQ_API_KEY` is present; it does not verify that Groq accepts the key or that the embedding model can load.

Example response:

```json
{"ok": true, "configured": true}
```

## `POST /api/chat`

Retrieves relevant policy entries, then generates a grounded answer with Groq when relevant context is available.

Request:

```json
{
  "message": "How long can I borrow a book?",
  "history": [
    {"role": "user", "content": "I am a library member."},
    {"role": "assistant", "content": "I can help with library policies."}
  ]
}
```

Constraints:

- `message`: required string, 1–2000 characters.
- `history`: optional array (defaults to `[]`), up to 12 messages.
- Each history `role` must be `user` or `assistant`; `content` is limited to 2000 characters.
- Only the most recent six history entries are included in the Groq prompt.

Success response (`200`):

```json
{
  "answer": "Books may be borrowed for the period stated in the applicable policy.",
  "sources": ["Loan and renewal"]
}
```

`answer` is plain text. `sources` contains the titles of retrieved policy entries. For a question with no policy above the similarity threshold, the app returns its fixed out-of-scope answer and an empty sources array without calling Groq.

### Error responses

| Status | Meaning |
| --- | --- |
| `422` | Request body does not satisfy the schema constraints. |
| `500` | Knowledge base or retrieval configuration is invalid. |
| `502` | Groq returned an HTTP error or could not be reached. Provider detail may be included in `detail`. |
| `503` | Embedding model/dependency is unavailable or the Groq key is missing. |

Error body format:

```json
{"detail": "Provider or application error description"}
```

### cURL example

```bash
curl -X POST http://127.0.0.1:8000/api/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"How long can I borrow a book?","history":[]}'
```

For an executable API contract, use `docs/openapi.yaml` in Swagger Editor or import `http://127.0.0.1:8000/openapi.json` into an API client.
