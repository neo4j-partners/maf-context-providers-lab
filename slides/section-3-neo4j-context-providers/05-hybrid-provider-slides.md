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


# Hybrid Search with Neo4j Context Provider

---

## The Problem with One Search Mode

**Vector search** understands concepts but can miss exact terms:
- "dream-sharing technology" might not surface if the model focuses on broader themes

**Fulltext search** matches keywords but misses semantic connections:
- "feel-good movies about unlikely friendships" only matches those exact words

- **Hybrid search** runs both and combines the results

---

## How Hybrid Search Works

Hybrid search runs **both** search modes in parallel on the same query:

1. **Vector search** embeds the query and finds semantically similar content
2. **Fulltext search** tokenizes the query and finds keyword matches
3. **Scores are combined** into a single ranked result set

A movie can rank highly on semantics, keywords, or both. Results that score well on **both** dimensions rise to the top.

---

## Why Inception Ranks #1

Query: "Find movies about dream-sharing technology"

| Search Mode | What It Finds |
|------------|---------------|
| **Fulltext** | Plots containing "dream-sharing" and "technology" as literal terms |
| **Vector** | Movies semantically related to dreams and technology concepts |
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

- Both indexes must exist in Neo4j before the provider can use them

---

## Configure the Provider

Hybrid search builds on the vector provider setup with one addition:

- **Set `index_type` to `"hybrid"`** instead of `"vector"`
- **Add `fulltext_index_name`**: points to your fulltext index for keyword matching
- **Keep `index_name` and `embedder`**: still needed for the vector search half

The provider runs both searches internally and merges the results before returning them. Everything else (`top_k`, `context_prompt`, connection settings) works the same.

---

## Using the Provider with an Agent

The hybrid provider plugs into an agent identically to vector or fulltext:

- Pass it in the `context_providers` list when creating the agent
- The agent automatically retrieves hybrid results before each LLM call
- No changes to agent setup, instructions, or session handling are needed

- All three search modes are interchangeable from the agent's perspective

---

## Trade-offs

| Aspect | Vector Only | Fulltext Only | Hybrid |
|--------|------------|---------------|--------|
| Semantic matching | Yes | No | Yes |
| Keyword precision | No | Yes | Yes |
| Embedder required | Yes | No | Yes |
| Indexes needed | 1 | 1 | 2 |
| Latency | Medium | Low | Higher |
| Setup complexity | Medium | Simple | Highest |

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

Hybrid search supports `retrieval_query` for graph enrichment, just like the other modes:

- Add the `retrieval_query` parameter with your Cypher traversal query
- The query receives `node` and `score` from the **combined** hybrid results
- The provider automatically switches to `HybridCypherRetriever` under the hood
- The same retrieval query Cypher works across all three search modes

---

## Choosing Your Search Strategy

- **Fulltext**: best when queries use specific names, titles, or keywords. Simplest setup, no embedder needed.
- **Vector**: best when queries are conceptual or exploratory ("movies about finding meaning in life"). Requires an embedder.
- **Hybrid**: best when you expect a mix of both styles, or you're unsure how users will query. Requires both indexes and an embedder.

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
