# Architecture

## Components

```mermaid
flowchart LR
    Browser[Browser: Bootstrap UI]
    JS[web/app.js]
    Routes[FastAPI controllers]
    Schemas[Pydantic request/response models]
    Assistant[Assistant model: orchestration]
    KB[(knowledge_base.json)]
    Embeddings[Sentence Transformers model]
    Groq[Groq Chat Completions API]

    Browser --> JS
    JS -->|POST /api/chat| Routes
    Routes --> Schemas
    Routes --> Assistant
    Assistant --> KB
    Assistant --> Embeddings
    Assistant -->|question + retrieved context| Groq
    Groq --> Assistant
    Assistant --> Routes
    Routes -->|answer + source titles| JS
```

## MVC mapping

| MVC concern | Project location | Responsibility |
| --- | --- | --- |
| Model | `app/models/` | Pydantic API schemas and assistant behavior: load policies, retrieve by embeddings, call Groq, format sources. |
| Controller | `app/controllers/` | Validate and route health/chat HTTP requests, translate assistant failures to HTTP errors. |
| View | `web/` | Responsive chat page, Bootstrap-based layout, styling, browser-side conversation and API calls. |
| Application composition | `app/main.py` | Creates FastAPI app, mounts static assets, includes routes, serves the home page. |

## Chat request sequence

```mermaid
sequenceDiagram
    actor User
    participant UI as Browser UI (web/app.js)
    participant API as FastAPI chat controller
    participant Assistant as Assistant model
    participant KB as knowledge_base.json
    participant Embed as Sentence Transformers
    participant Groq as Groq API

    User->>UI: Submit question
    UI->>UI: Show "Searching policies" status
    UI->>API: POST /api/chat (message, history)
    API->>API: Validate ChatRequest
    API->>Assistant: answer_question(payload)
    Assistant->>KB: Load policy entries
    KB-->>Assistant: Policy titles and text
    Assistant->>Embed: Encode policies (cached) and question
    Embed-->>Assistant: Normalized vectors
    Assistant->>Assistant: Rank cosine similarity; keep up to 3 above threshold
    alt Relevant policies found
        Assistant->>Groq: Prompt + relevant policy context + recent history
        Groq-->>Assistant: Grounded answer
    else No relevant policies found
        Assistant->>Assistant: Return fixed out-of-scope answer
    end
    Assistant-->>API: Answer and source titles
    API-->>UI: JSON response
    UI->>UI: Replace pending status with answer and sources
```

## Request flow

```mermaid
flowchart TD
    A[User submits a question] --> B[Browser sends POST /api/chat]
    B --> C{Valid request?}
    C -- No --> D[FastAPI returns 422 validation detail]
    C -- Yes --> E[Read knowledge_base.json]
    E --> F[Load cached embedding model]
    F --> G[Embed corpus if cache is stale]
    G --> H[Embed question and rank by cosine similarity]
    H --> I{Any policy meets threshold?}
    I -- No --> J[Return out-of-scope answer and empty sources]
    I -- Yes --> K[Build grounded prompt with context and history]
    K --> L[Call Groq]
    L --> M{Provider response}
    M -- Success --> N[Return answer and source titles]
    M -- Error --> O[Return HTTP 502 with provider failure detail]
    J --> P[Browser renders answer]
    N --> P
    D --> Q[Browser renders request error]
    O --> Q
```

## Runtime and caching

- Sentence Transformer weights are loaded lazily and the model object is cached in the process.
- Policy vectors are cached in memory and rebuilt when the embedding model name or policy corpus changes.
- The first use needs the model files locally or outbound access to the Hugging Face Hub. The public default model does not require `HF_TOKEN`.
- Generation uses Groq's OpenAI-compatible Chat Completions endpoint. The secret key stays on the server and is not passed to browser JavaScript.
- Docker sets `HF_HOME=/model-cache`; mount a named volume at that path to persist model files.
