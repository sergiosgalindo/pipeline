# RAG and Knowledge Base

## Retrieval and generation

The assistant uses retrieval-augmented generation (RAG):

1. Load entries from `knowledge_base.json`.
2. Construct embedding text from each entry's `title` and `text`.
3. Encode policy text and the user question with the configured Sentence Transformers model. Vectors are normalized; cosine similarity is computed as their dot product.
4. Keep up to three policies whose score is at least `EMBEDDING_MIN_SIMILARITY` (default `0.4`), in descending order.
5. If policies were retrieved, send their text with the question and recent conversation context to Groq. The system prompt instructs the model to answer from the supplied policy context only.
6. Return the answer and retrieved policy titles in `sources`.

If no policy clears the threshold, the app returns a fixed answer that says the information is not available in the library policies; it does not call Groq for that request.

## Knowledge base format

`knowledge_base.json` is a JSON array. Each item must contain string fields `title` and `text`.

```json
[
  {
    "title": "Loan and renewal",
    "text": "Describe the borrowing period, renewal conditions, and exceptions here."
  }
]
```

Keep each entry focused on one policy topic. Use clear language and include the actual rules, exceptions, and relevant terms users may mention. Do not put secrets or personal data in this file; its content is sent to the configured generation provider when retrieved.

## Embedding cache behavior

The embedding model instance is cached in-process. Corpus vectors are cached in process memory, keyed by the model name and the complete ordered `(title, text)` content. Editing policy content causes vectors to be recomputed on a later query. Restarting the server clears these in-memory vectors; downloaded model files persist in the configured Hugging Face cache.

`EMBEDDING_MIN_SIMILARITY` must parse as a number between `-1` and `1`. Raising it makes retrieval stricter; lowering it admits more policy entries and may add irrelevant context. Evaluate paraphrases and out-of-scope questions when changing the threshold.

## Model choice and credentials

The default multilingual embedding model is public and does not require `HF_TOKEN`. A token does not grant access to Groq; `GROQ_API_KEY` is a separate credential. The app currently uses Groq for text generation and does not use the LoRA adapter from the educational notebook.
