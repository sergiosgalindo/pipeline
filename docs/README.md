# Library Assistant Documentation

This directory contains the project guide, architecture diagrams, API reference, setup instructions, retrieval notes, and verification guidance. The documentation describes the current implementation in this repository.

## Contents

Open [index.html](index.html) to read this guide in the browser, including the Mermaid diagrams.

- [Project overview and architecture](architecture.md)
- [HTTP API reference](api.md)
- [OpenAPI specification](openapi.yaml)
- [Local and Docker setup](setup-and-deployment.md)
- [Knowledge base and RAG](rag-and-knowledge-base.md)
- [Testing, troubleshooting, and security](testing-and-troubleshooting.md)
- [MVC implementation map](implementation-map.md)

## Interactive API explorer

When the application is running, FastAPI serves Swagger UI at `http://127.0.0.1:8000/docs`, ReDoc at `http://127.0.0.1:8000/redoc`, and its generated OpenAPI JSON at `http://127.0.0.1:8000/openapi.json`. The checked-in [OpenAPI YAML](openapi.yaml) provides a readable API contract for clients and tools.

## Project summary

The application is a responsive Bootstrap 5 web chat served by FastAPI. It retrieves the most relevant library policies using multilingual Sentence Transformers embeddings, then asks Groq to produce a concise grounded answer. Policy data is stored in `knowledge_base.json`. The app uses an MVC-inspired structure: FastAPI routes are controllers, Pydantic schemas and RAG/provider logic are models, and `web/` contains the view and browser behavior.

The current web app uses RAG and Groq generation. It does not load or serve the LoRA adapter from the training notebook. The notebook is educational/reference material; the deployable web application is implemented separately.

## SDD records

The feature workspace contains the functional and technical specifications, task plan, progress, and implementation map: [`code/wip/20260924-biblioteca-chat-web/`](../code/wip/20260924-biblioteca-chat-web/).
