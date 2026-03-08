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

## From Custom to Ready-Made

In Module 2, you built a context provider from scratch using `BaseContextProvider`.

`Neo4jContextProvider` from the `agent-framework-neo4j` package does the heavy lifting for you:
- Connects to a Neo4j database
- Searches an index (vector, fulltext, or hybrid)
- Formats and injects results before every LLM call

**Same `BaseContextProvider` base class. Production-grade search built in.**

---

## Powered by neo4j-graphrag-python

`Neo4jContextProvider` delegates all search to the `neo4j-graphrag-python` library.

**Retriever classes provided by neo4j-graphrag:**
- `VectorRetriever` / `VectorCypherRetriever`
- `HybridRetriever` / `HybridCypherRetriever`
- Fulltext retriever for Lucene-based indexes

You configure the provider; `neo4j-graphrag` runs the search.

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

The LLM sees this context alongside the user's question.

---

## Three Search Modes

The `index_type` parameter determines the search strategy:

| Mode | How It Works | Best For | Embedder? |
|------|-------------|----------|-----------|
| **`vector`** | Cosine similarity on embeddings | Semantic similarity | Yes |
| **`fulltext`** | BM25 ranking on tokenized text | Keyword matching | No |
| **`hybrid`** | Runs both, combines scores | Best of both worlds | Yes |

---

## When to Use Each Mode

| Mode | Best For | Example Query |
|------|----------|---------------|
| **Vector** | Conceptual, exploratory questions | "Movies about unlikely friendships" |
| **Fulltext** | Specific names, titles, exact terms | "Christopher Nolan Batman" |
| **Hybrid** | Mixed conceptual and keyword queries | "Christopher Nolan sci-fi movies about dreams" |

**Vector** understands meaning. **Fulltext** matches keywords. **Hybrid** combines both.

---

## Retriever Selection Logic

The provider automatically selects the right retriever based on your configuration:

| index_type | retrieval_query | Retriever Used |
|------------|-----------------|----------------|
| `vector` | Not set | `VectorRetriever` |
| `vector` | Set | `VectorCypherRetriever` |
| `fulltext` | Any | Fulltext retriever |
| `hybrid` | Not set | `HybridRetriever` |
| `hybrid` | Set | `HybridCypherRetriever` |

Adding a `retrieval_query` upgrades to a Cypher-capable retriever.

---

## Configuration Options

```python
provider = Neo4jContextProvider(
    uri=neo4j_settings.uri,              # Neo4j connection
    username=neo4j_settings.username,
    password=neo4j_settings.get_password(),
    index_name="moviePlots",             # Neo4j index to search
    index_type="vector",                 # vector | fulltext | hybrid
    embedder=embedder,                   # Required for vector/hybrid
    top_k=5,                             # Number of results
    message_history_count=10,            # Recent messages for query
    context_prompt="## Search Results\n"
                   "Use these to answer:",
)
```

---

## Mode-Specific Parameters

| Parameter | Modes | Purpose |
|-----------|-------|---------|
| `embedder` | vector, hybrid | Converts query text to vectors |
| `fulltext_index_name` | hybrid | Fulltext index for keyword search |
| `filter_stop_words` | fulltext | Remove common words before search |
| `retrieval_query` | all | Cypher for graph enrichment |

Each provider instance supports a **single** `index_type`. Use multiple providers for multiple strategies.

---

## Async Context Manager

The provider manages its Neo4j connection lifecycle:

```python
async with provider:
    agent = client.as_agent(
        name="my-agent",
        instructions="...",
        context_providers=[provider],
    )
    session = agent.create_session()
    response = await agent.run("query", session=session)
```

Connects on entry, verifies connectivity, initializes retriever, closes on exit.

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
- **Async context manager** handles connection lifecycle

**Next:** Vector search for semantic similarity.
