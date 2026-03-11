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


# Fulltext Search with Neo4j Context Provider

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

**Fulltext search:** Uses Neo4j's built-in **Lucene-based fulltext indexing** with **BM25 ranking**

1. The user's query is preprocessed: common stop words ("what", "the", "is") are filtered out
2. Remaining terms are tokenized and matched against the fulltext index
3. Results are ranked by BM25 score, weighing term frequency, rarity, and document length
4. Top results are injected as context for the LLM

---

## BM25 Ranking

BM25 (Best Matching 25) scores documents based on:

- **Term frequency**: how often the search terms appear in the text
- **Inverse document frequency**: how rare the terms are across all documents
- **Document length normalization**: shorter documents with matches rank higher

- A movie plot mentioning "space" and "exploration" multiple times ranks higher than one that mentions them once

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

Setting up a fulltext provider differs from vector search in two ways:

- **Set `index_type` to `"fulltext"`** and point `index_name` to your fulltext index
- **No `embedder` parameter**: fulltext search works directly on text, so there's no embedding step

Everything else (`top_k`, `context_prompt`, connection settings) works the same as vector search. The simpler setup also means lower latency since no embedding API call is needed.

---

## Stop Word Filtering

By default, the provider filters common stop words before searching.

| Original Query | After Filtering |
|----------------|-----------------|
| "What movies are about time travel?" | "movies time travel" |
| "Tell me about Christopher Nolan" | "Christopher Nolan" |
| "What is the best action movie?" | "best action movie" |

- Words like "what," "the," "is," and "about" add noise to fulltext queries

---

## Disabling Stop Word Filtering

By default, the provider removes common words like "the", "is", and "about" before searching. This improves results for most queries.

To disable this, set `filter_stop_words=False` on the provider. This passes the raw query directly to the index.

**When you'd want this:** domains where stop words carry meaning, for example searching for a band name like "The Who" or a movie titled "It".

---

## Using the Provider with an Agent

Once configured, the fulltext provider plugs into an agent the same way as any other context provider:

- Pass it in the `context_providers` list when creating the agent
- The agent automatically retrieves fulltext results before each LLM call
- No changes to agent setup, instructions, or session handling are needed

- The provider is interchangeable — swap between vector, fulltext, and hybrid without changing agent code

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

- Add the same `retrieval_query` parameter you'd use with vector search
- The query receives `node` and `score` from the fulltext results, then traverses relationships the same way
- The exact same Cypher works regardless of search mode. The only difference is how the initial `node` and `score` are produced.

---

## Summary

In this lesson, you learned:

- **Fulltext search** uses `index_type="fulltext"` with BM25 ranking
- **No embedder required**: simpler setup, lower latency
- **Stop word filtering** removes noise words by default
- **Best for** keyword-based queries with specific names or terms
- **Supports graph enrichment** via `retrieval_query`
- **Complementary to vector search**: different strengths for different query types

**Next:** Hybrid search to combine both approaches.
