---
marp: true
theme: default
paginate: true
---

<style>
section {
  --marp-auto-scaling-code: false;
}

li {
  opacity: 1 !important;
  animation: none !important;
  visibility: visible !important;
}

/* Disable all fragment animations */
.marp-fragment {
  opacity: 1 !important;
  visibility: visible !important;
}

ul > li,
ol > li {
  opacity: 1 !important;
}
</style>


# Vector Search with Neo4j Context Provider

---

## What is Vector Search?

**Vectors:** Numerical representations of text encoded as high-dimensional arrays

**Key property:** Similar meanings produce similar vectors

- "time travel adventure" and "journey through time" → vectors close together
- "time travel adventure" and "cooking recipes" → vectors far apart

- This enables **semantic search**: finding content by meaning, not keywords

---

## How Vector Search Works

```
1. User asks: "Find me movies about time travel"
       ↓
2. Embedder converts query to a 1536-dimensional vector
       ↓
3. Neo4j vector index compares against stored plot embeddings
       ↓
4. Returns movies ranked by cosine similarity
       ↓
5. Results injected as context before LLM call
```

"Time travel" finds movies about temporal paradoxes, wormholes, and alternate timelines, even without those exact words.

---

## Embeddings Must Match

**Critical:** The query embedder must use the **same model and dimensions** as the stored embeddings — different models produce incompatible vectors

**Supported embedders in neo4j-graphrag:**
- OpenAI, Azure OpenAI, Cohere, Mistral AI, Google Vertex AI, Ollama, Sentence Transformers

---

## Create an Embedder

Configures the embedding model the provider will use to convert query text into vectors:

```python
from neo4j_graphrag.embeddings.openai import OpenAIEmbeddings

# Uses OPENAI_API_KEY from environment automatically
embedder = OpenAIEmbeddings(model="text-embedding-ada-002")
```

---

## Configure the Provider

`Neo4jContextProvider` is configured with:

- **Connection details**: URI, username, and password for your Neo4j instance (read from environment variables via `Neo4jSettings`)
- **`index_name`**: The Neo4j vector index to search (e.g., `"moviePlots"`)
- **`index_type`**: Set to `"vector"` for semantic search via cosine similarity
- **`embedder`**: The same embedding model used to create the stored vectors
- **`top_k`**: Number of results to retrieve
- **`context_prompt`**: Text prepended to results that guides the LLM on how to use the injected data

---

## Configure and Run the Agent

**Registration:** Pass the provider in `context_providers` so `before_run()` runs on every turn

**Automatic:** The provider embeds the query, searches the index, and injects results before the LLM responds — no explicit tool calls needed

---

## What Happens on Each Turn

```
1. User: "Find me movies about time travel"
       ↓
2. provider.before_run() is called automatically
       ↓
3. Query embedded → vector index searched → top 5 results found
       ↓
4. Results injected as context messages
       ↓
5. LLM generates response grounded in actual movie data
```

**No tool call happened.** The context was injected automatically.

---

## With vs Without Context

**Without the context provider:** Agent answers from training data. Mentions well-known movies but has no access to your specific database.

**With the context provider:** Agent response is grounded in movies that actually exist in your Neo4j graph. Can reference specific plots and less obvious films that match semantically.

**Core value:** Consistent, automatic knowledge retrieval on every turn

---

## Summary

In this lesson, you learned:

- **Vector search** embeds the query and finds semantically similar content via cosine similarity
- **Embedder models must match** between stored vectors and query vectors
- **`Neo4jContextProvider`** with `index_type="vector"` handles embedding, search, and injection
- **Automatic context**: no tool calls, grounded in real graph data

**Next:** Graph-enriched retrieval to add structured metadata.
