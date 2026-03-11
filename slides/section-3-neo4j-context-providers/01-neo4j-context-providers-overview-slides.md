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


# Neo4j Context Providers Overview

---

## Neo4j Context Providers for MAF

Neo4j provides two context provider packages for the Microsoft Agent Framework:

- **`agent-framework-neo4j`**: Retrieves knowledge from Neo4j indexes (vector, fulltext, or hybrid search) and injects it before every LLM call
- **`neo4j-agent-memory`**: Gives agents persistent memory across conversations, capturing user preferences and entity mentions in Neo4j

- This module focuses on `agent-framework-neo4j`
- The next module covers `neo4j-agent-memory`

---

## Beyond Retrieval: Building Knowledge Graphs

The `neo4j-graphrag-python` library also provides a pipeline for **building** knowledge graphs from unstructured text:

- **`SimpleKGPipeline`** automates splitting, entity extraction, embedding, and storage
- Takes raw documents (PDFs, articles) and creates structured graph data
- The same library used to **query** your graph can also **construct** it

---

## Neo4j Context Provider

`Neo4jContextProvider` from the `agent-framework-neo4j` package:

- Connects to a Neo4j database and searches an index (vector, fulltext, or hybrid)
- Injects matching results before every LLM call via `before_run()`
- Delegates all search to `neo4j-graphrag-python` retriever classes (`VectorRetriever`, `HybridRetriever`, etc.)

- You configure the provider; `neo4j-graphrag` runs the search

---

## Three Search Modes

`Neo4jContextProvider` supports three search modes via the `index_type` parameter:

| Mode | How It Works | Key Strength |
|------|-------------|--------------|
| **`vector`** | Cosine similarity on embeddings | Understands meaning |
| **`fulltext`** | BM25 ranking on tokenized text | Matches keywords |
| **`hybrid`** | Runs both, combines scores | Combines both |

**Graph-enhanced** enriches any mode with related knowledge from the graph.

---

## Graph-Enhanced Search

Any search mode can be **graph-enhanced** by adding a `retrieval_query`:

- **Initial search**: Performs vector, fulltext, or hybrid search as configured
- **Graph traversal**: Executes a Cypher query from each result to follow connections
- **Richer context**: Returns related entities, relationships, and metadata alongside the matched text

**Without graph enrichment**: isolated text chunks
**With graph enrichment**: text chunks + structured knowledge from the graph

- Graph enrichment is what separates GraphRAG from standard vector RAG

---

## How before_run() Works

Each time the agent receives a query, the provider's `before_run()` executes:

```
1. Filter messages to user and assistant roles
       ↓
2. Take the most recent messages (message_history_count)
       ↓
3. Concatenate message text into a search query
       ↓
4. Execute search against Neo4j index (vector/fulltext/hybrid)
       ↓
5. Format results and inject via context.extend_messages()
```

- The LLM sees this context alongside the user's question

---

## Context Provider Retriever Selection

The provider selects the retriever based on your `index_type` and `retrieval_query` configuration:

| index_type | retrieval_query | Retriever Used |
|------------|-----------------|----------------|
| `vector` | Not set | `VectorRetriever` |
| `vector` | Set | `VectorCypherRetriever` |
| `fulltext` | Any | Fulltext retriever |
| `hybrid` | Not set | `HybridRetriever` |
| `hybrid` | Set | `HybridCypherRetriever` |

Adding a `retrieval_query` upgrades to a Cypher-capable retriever.

---

## Key Parameters

| Parameter | Modes | Purpose |
|-----------|-------|---------|
| `top_k` | all | Number of results to retrieve |
| `message_history_count` | all | Recent messages used to build the search query |
| `context_prompt` | all | Text prepended to results to guide the LLM |
| `embedder` | vector, hybrid | Converts query text to vectors |
| `fulltext_index_name` | hybrid | Fulltext index for keyword search |
| `filter_stop_words` | fulltext | Remove common words before search |
| `retrieval_query` | all | Cypher for graph enrichment |

- Each provider instance supports a **single** `index_type`
- Use multiple providers for multiple strategies

---

## Multiple Providers

Each provider instance supports a single `index_type`. For multiple search strategies, create separate instances:

```python
vector_provider = Neo4jContextProvider(
    index_name="moviePlots", index_type="vector", embedder=embedder, ...
)
fulltext_provider = Neo4jContextProvider(
    index_name="moviePlotsFulltext", index_type="fulltext", ...
)

agent = client.as_agent(
    context_providers=[vector_provider, fulltext_provider],
)
```

The agent merges context from every provider before calling the LLM.

---

## Summary

In this lesson, you learned:

- **`Neo4jContextProvider`** extends `BaseContextProvider` with production-grade search
- **Powered by `neo4j-graphrag-python`** retriever classes
- **`before_run()`** takes recent messages, searches the index, and injects results
- **Three search modes**: vector (semantic), fulltext (keyword), hybrid (combined)
- **Retriever selection** is automatic based on `index_type` and `retrieval_query`

**Next:** Vector search for semantic similarity.
