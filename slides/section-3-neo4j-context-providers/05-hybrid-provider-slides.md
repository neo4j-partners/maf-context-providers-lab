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


# Hybrid Search with Neo4jContextProvider

---

## The Problem with One Search Mode

**Vector search** understands concepts but can miss exact terms:
- "Christopher Nolan" might return movies with similar themes, not Nolan's films

**Fulltext search** matches keywords but misses semantic connections:
- "feel-good movies about unlikely friendships" only matches those exact words

**Hybrid search runs both and combines the results.**

---

## How Hybrid Search Works

```
1. User: "Christopher Nolan sci-fi movies about dreams"
       ↓
2. Vector search: embed query → find semantically similar plots
       ↓
3. Fulltext search: tokenize query → find keyword matches
       ↓
4. Combine scores from both searches
       ↓
5. Single ranked result set injected as context
```

A movie can rank highly on semantics, keywords, or both. Results scoring well on both dimensions rise to the top.

---

## Why Inception Ranks #1

Query: "Christopher Nolan sci-fi movies about dreams"

| Search Mode | What It Finds |
|------------|---------------|
| **Vector** | Movies semantically related to "sci-fi about dreams" |
| **Fulltext** | Plots containing "Christopher Nolan" and "dreams" |
| **Hybrid** | Inception matches on **both** dimensions |

Hybrid catches what either mode alone might miss.

---

## Requirements

Hybrid search requires three things:

| Requirement | Parameter | Purpose |
|-------------|-----------|---------|
| Vector index | `index_name` | For semantic similarity search |
| Fulltext index | `fulltext_index_name` | For keyword matching |
| Embedder | `embedder` | To generate query vectors |

Both indexes must exist in Neo4j before the provider can use them.

---

## Configure the Provider

```python
from agent_framework_neo4j import Neo4jContextProvider, Neo4jSettings
from neo4j_graphrag.embeddings.openai import OpenAIEmbeddings

neo4j_settings = Neo4jSettings()
embedder = OpenAIEmbeddings(model="text-embedding-ada-002")

provider = Neo4jContextProvider(
    uri=neo4j_settings.uri,
    username=neo4j_settings.username,
    password=neo4j_settings.get_password(),
    index_name=neo4j_settings.vector_index_name,
    index_type="hybrid",
    fulltext_index_name=neo4j_settings.fulltext_index_name,
    embedder=embedder,
    top_k=5,
)
```

The key addition: `fulltext_index_name` alongside the vector `index_name`.

---

## Run the Agent

```python
async def main():
    async with provider:
        client = OpenAIResponsesClient()

        agent = client.as_agent(
            name="movie-hybrid-agent",
            instructions=(
                "You are a movie recommendation assistant. "
                "Answer questions using the movie data "
                "provided in your context."
            ),
            context_providers=[provider],
        )

        session = agent.create_session()
        response = await agent.run(
            "Christopher Nolan sci-fi movies about dreams",
            session=session,
        )
        print(response.text)
```

---

## Trade-offs

| Aspect | Vector Only | Fulltext Only | Hybrid |
|--------|------------|---------------|--------|
| Semantic matching | Yes | No | Yes |
| Keyword precision | No | Yes | Yes |
| Embedder required | Yes | No | Yes |
| Indexes needed | 1 | 1 | 2 |
| Latency | Medium | Low | Higher |
| Setup complexity | Medium | Simple | Most |

---

## When to Use Each Mode

| User Behavior | Recommended Mode |
|---------------|-----------------|
| Conceptual, exploratory queries | **Vector** |
| Keyword-based, specific terms | **Fulltext** |
| Mix of both styles | **Hybrid** |
| You're unsure how users will query | **Hybrid** |

Hybrid is the most versatile but uses more resources than either mode alone.

---

## Graph Enrichment with Hybrid

Hybrid search supports `retrieval_query` for graph enrichment:

```python
provider = Neo4jContextProvider(
    index_name=neo4j_settings.vector_index_name,
    index_type="hybrid",
    fulltext_index_name=neo4j_settings.fulltext_index_name,
    embedder=embedder,
    retrieval_query=RETRIEVAL_QUERY,  # Cypher traversal
    top_k=5,
)
```

When provided, the provider uses `HybridCypherRetriever` instead of `HybridRetriever`. The retrieval query receives `node` and `score` from the combined results.

---

## Choosing Your Search Strategy

```
Do you need semantic understanding?
├── No  → Fulltext (simplest setup)
├── Yes → Do you also need keyword precision?
│   ├── No  → Vector (semantic only)
│   └── Yes → Hybrid (both combined)
```

All three modes support graph enrichment via `retrieval_query`.

---

## Summary

In this lesson, you learned:

- **Hybrid search** combines vector and fulltext by running both and merging results
- **Requires** a vector index, a fulltext index, and an embedder
- **Catches both** semantic and keyword matches in one query
- **Most versatile** option when users mix conceptual and specific queries
- **Supports graph enrichment** via `HybridCypherRetriever`
- **Trade-off:** more resources and higher latency than single-mode search

**Next module:** Give agents persistent memory with Neo4j Agent Memory.
