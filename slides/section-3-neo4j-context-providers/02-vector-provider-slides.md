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


# Vector Search with Neo4jContextProvider

---

## What is Vector Search?

Vectors are numerical representations of text encoded as high-dimensional arrays (often 1,536 dimensions).

**The key property:** Similar meanings produce similar vectors.

- "time travel adventure" and "journey through time" → vectors close together
- "time travel adventure" and "cooking recipes" → vectors far apart

This enables **semantic search** -- finding content by meaning, not keywords.

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

"Time travel" finds movies about temporal paradoxes, wormholes, and alternate timelines -- even without those exact words.

---

## Embeddings Must Match

The query embedder must use the **same model and dimensions** as the stored embeddings.

| Stored Embeddings | Query Embedder | Result |
|-------------------|----------------|--------|
| `text-embedding-ada-002` (1536d) | `text-embedding-ada-002` (1536d) | Works |
| `text-embedding-ada-002` (1536d) | `text-embedding-3-small` (1536d) | Poor results |
| `text-embedding-ada-002` (1536d) | Any model (768d) | Fails |

**Supported embedders in neo4j-graphrag:** OpenAI, Azure OpenAI, Cohere, Mistral AI, Google Vertex AI, Ollama, Sentence Transformers.

---

## Create an Embedder

```python
from neo4j_graphrag.embeddings.openai import OpenAIEmbeddings

# Uses OPENAI_API_KEY from environment automatically
embedder = OpenAIEmbeddings(model="text-embedding-ada-002")
```

The embedder converts query text into a vector that can be compared against `plotEmbedding` vectors stored on Movie nodes.

---

## Configure the Provider

```python
from agent_framework_neo4j import Neo4jContextProvider, Neo4jSettings

neo4j_settings = Neo4jSettings()

provider = Neo4jContextProvider(
    uri=neo4j_settings.uri,
    username=neo4j_settings.username,
    password=neo4j_settings.get_password(),
    index_name=neo4j_settings.vector_index_name,
    index_type="vector",
    embedder=embedder,
    top_k=5,
    context_prompt=(
        "## Semantic Search Results\n"
        "Use the following semantically relevant movie plots "
        "from the knowledge graph to answer questions:"
    ),
)
```

---

## Key Parameters

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `index_name` | `"moviePlots"` | Neo4j vector index to search |
| `index_type` | `"vector"` | Semantic search via cosine similarity |
| `embedder` | `OpenAIEmbeddings` | Generates query vectors |
| `top_k` | `5` | Balance between context richness and token usage |
| `context_prompt` | Custom text | Guides the LLM on how to use injected data |

---

## Run the Agent

```python
async def main():
    async with provider:
        client = OpenAIResponsesClient()

        agent = client.as_agent(
            name="vector-agent",
            instructions=(
                "You are a helpful assistant that answers questions "
                "about movies using the provided semantic search context."
            ),
            context_providers=[provider],
        )

        session = agent.create_session()
        response = await agent.run(
            "Find me movies about time travel", session=session
        )
        print(response.text)
```

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

**Without the context provider:**
The agent answers from training data. It mentions well-known movies but has no access to your specific database.

**With the context provider:**
The agent's response is grounded in movies that actually exist in your Neo4j graph. It can reference specific plots and mention less obvious films that match semantically.

**This is the core value:** consistent, automatic knowledge retrieval on every turn.

---

## Understanding Similarity Scores

| Score Range | Interpretation |
|-------------|----------------|
| 0.95 - 1.0 | Extremely similar (near-exact match) |
| 0.90 - 0.95 | Highly relevant |
| 0.85 - 0.90 | Relevant |
| 0.80 - 0.85 | Moderately relevant |
| < 0.80 | Weak relevance |

Higher scores indicate stronger semantic matches between query and stored content.

---

## Limitations of Vector-Only Search

Vector search returns matching **text** and a similarity **score**.

It does **not** include:
- Movie title or release year
- Genres the movie belongs to
- Actors who appeared in it
- Directors

**That metadata lives in the graph.** Graph-enriched retrieval traverses these relationships after search.

---

## Summary

In this lesson, you learned:

- **Vector search** embeds the query and finds semantically similar content via cosine similarity
- **Embedder models must match** between stored vectors and query vectors
- **`Neo4jContextProvider`** with `index_type="vector"` handles embedding, search, and injection
- **Automatic context** -- no tool calls, grounded in real graph data
- **Limitation** -- returns text only, no structured metadata from relationships

**Next:** Graph-enriched retrieval to add structured metadata.
