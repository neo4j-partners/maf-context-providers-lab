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


# Fulltext Search with Neo4jContextProvider

---

## Vector vs Fulltext

**Vector search** finds content by meaning:
- "stories about machines becoming conscious" matches movies about artificial intelligence

**Fulltext search** matches on actual words:
- "Christopher Nolan" finds plots containing those exact terms

Different tools for different jobs.

---

## When to Use Fulltext Search

Fulltext search is the better choice when:

- The user mentions **specific names, titles, or terms**
- You want **keyword precision** rather than semantic interpretation
- You **don't have or need** vector embeddings on your nodes
- You want **lower latency** (no embedding API call required)

**No embedder needed.** Simpler setup, faster execution.

---

## How It Works

Fulltext search uses Neo4j's built-in **Lucene-based fulltext indexing** with **BM25 ranking**.

```
1. User: "Find movies about space exploration"
       ↓
2. Stop words filtered: "movies space exploration"
       ↓
3. Remaining terms tokenized and searched against fulltext index
       ↓
4. Results ranked by BM25 score (term frequency + document length)
       ↓
5. Top results injected as context
```

---

## BM25 Ranking

BM25 (Best Matching 25) scores documents based on:

- **Term frequency** -- how often the search terms appear in the text
- **Inverse document frequency** -- how rare the terms are across all documents
- **Document length normalization** -- shorter documents with matches rank higher

A movie plot mentioning "space" and "exploration" multiple times ranks higher than one that mentions them once.

---

## Create a Fulltext Index

If one doesn't already exist:

```cypher
CREATE FULLTEXT INDEX moviePlotsFulltext IF NOT EXISTS
FOR (m:Movie)
ON EACH [m.plot]
```

This indexes the `plot` property of `Movie` nodes for fulltext search.

---

## Configure the Provider

```python
from agent_framework_neo4j import Neo4jContextProvider, Neo4jSettings

neo4j_settings = Neo4jSettings()

provider = Neo4jContextProvider(
    uri=neo4j_settings.uri,
    username=neo4j_settings.username,
    password=neo4j_settings.get_password(),
    index_name=neo4j_settings.fulltext_index_name,
    index_type="fulltext",
    top_k=5,
    context_prompt=(
        "## Knowledge Graph Context\n"
        "Use the following information from the knowledge graph "
        "to answer questions about movies:"
    ),
)
```

**No embedder parameter.** That's the key difference from vector search.

---

## Stop Word Filtering

By default, the provider filters common stop words before searching.

| Original Query | After Filtering |
|----------------|-----------------|
| "What movies are about time travel?" | "movies time travel" |
| "Tell me about Christopher Nolan" | "Christopher Nolan" |
| "What is the best action movie?" | "best action movie" |

Words like "what," "the," "is," and "about" add noise to fulltext queries.

---

## Disabling Stop Word Filtering

If you need the raw query passed through:

```python
provider = Neo4jContextProvider(
    uri=neo4j_settings.uri,
    username=neo4j_settings.username,
    password=neo4j_settings.get_password(),
    index_name=neo4j_settings.fulltext_index_name,
    index_type="fulltext",
    filter_stop_words=False,  # Pass raw query to index
    top_k=5,
)
```

Useful when stop words are meaningful in your domain.

---

## Run the Agent

```python
async def main():
    async with provider:
        client = OpenAIResponsesClient()

        agent = client.as_agent(
            name="fulltext-agent",
            instructions=(
                "You are a helpful assistant that answers questions "
                "about movies using the provided knowledge graph context."
            ),
            context_providers=[provider],
        )

        session = agent.create_session()
        response = await agent.run(
            "Find movies about space exploration", session=session
        )
        print(response.text)
```

---

## Vector vs Fulltext: Side by Side

| Query | Vector Search | Fulltext Search |
|-------|--------------|-----------------|
| "movies about finding meaning in life" | Excels (abstract concept) | Looks for literal words |
| "Christopher Nolan Batman" | May find similar themes | Excels (exact name match) |
| "feel-good stories about friendship" | Understands the concept | Matches "friendship" literally |
| "Quentin Tarantino crime films" | Finds crime themes broadly | Finds "Tarantino" precisely |

**Neither mode is universally better.** The right choice depends on how your users query.

---

## Graph Enrichment with Fulltext

Fulltext search also supports `retrieval_query` for graph enrichment:

```python
provider = Neo4jContextProvider(
    index_name="moviePlotsFulltext",
    index_type="fulltext",
    retrieval_query=RETRIEVAL_QUERY,  # Same Cypher as vector mode
    top_k=5,
)
```

The retrieval query receives `node` and `score` from the fulltext search, then traverses relationships the same way.

---

## Summary

In this lesson, you learned:

- **Fulltext search** uses `index_type="fulltext"` with BM25 ranking
- **No embedder required** -- simpler setup, lower latency
- **Stop word filtering** removes noise words by default
- **Best for** keyword-based queries with specific names or terms
- **Supports graph enrichment** via `retrieval_query`
- **Complementary to vector search** -- different strengths for different query types

**Next:** Hybrid search to combine both approaches.
