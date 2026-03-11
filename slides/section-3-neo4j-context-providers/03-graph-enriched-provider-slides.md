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


# Graph-Enriched Retrieval

---

## Why Search Alone Isn't Enough

- Index search returns text ranked by relevance
- Graph-enriched retrieval adds a Cypher traversal step after the index search
- The provider finds matching movies, then walks the graph to collect genres, cast, and directors for each match

---

## The Two-Step Process

**Step 1: Index Search**
- Your query is matched against the index (vector, fulltext, or hybrid)
- Returns matched nodes ranked by relevance, each with a similarity `score`

**Step 2: Graph Traversal (retrieval_query)**
- For each matched node, the provider runs your Cypher `retrieval_query`
- Traverses outward from the matched node, following relationships to collect genres, actors, and directors
- Returns enriched context combining the original text with structured metadata

- The matched node is the **anchor**; you traverse outward from what search found

---

## Works with All Search Modes

Graph enrichment is not limited to vector search:

| index_type | Without retrieval_query | With retrieval_query |
|------------|------------------------|---------------------|
| `vector` | `VectorRetriever` | `VectorCypherRetriever` |
| `hybrid` | `HybridRetriever` | `HybridCypherRetriever` |
| `fulltext` | Fulltext retriever | Fulltext retriever |

The same `retrieval_query` Cypher works across modes. It always receives `node` and `score`.

---

## The retrieval_query: Cypher Query to Enhance Search

- Receives each matched `node` and its similarity `score` from the search step
- Defines what graph data to traverse and return (relationships, properties, aggregated lists)
- Transforms raw search hits into enriched context before the LLM sees them
- With it: provider switches to a Cypher-aware retriever (`VectorCypherRetriever` or `HybridCypherRetriever`)

---

## Writing Retrieval Queries

- Use `node` and `score` (provided by the index search)
- Must return at least `text` and `score` columns
- Use `OPTIONAL MATCH` for relationships that may not exist
- Use `ORDER BY score DESC` to maintain relevance ranking
- Limit collected lists (e.g., `[0..5]`) to control context size

---

## Example Retrieval Query

```cypher
MATCH (node)-[:IN_GENRE]->(g:Genre)
WITH node, score, collect(DISTINCT g.name) AS genres
OPTIONAL MATCH (p:Person)-[:ACTED_IN]->(node)
WITH node, score, genres,
     collect(DISTINCT p.name)[0..5] AS actors
OPTIONAL MATCH (d:Person)-[:DIRECTED]->(node)
WITH node, score, genres, actors,
     collect(DISTINCT d.name) AS directors
RETURN node.plot AS text, score,
       node.title AS title, genres, actors, directors
ORDER BY score DESC
```

<!--
High-level flow of this query:
- Start from the matched movie node (provided by the index search along with its score)
- First MATCH walks IN_GENRE relationships to collect genre names
- OPTIONAL MATCH finds Person nodes that ACTED_IN this movie — OPTIONAL because not every movie may have actor data in the graph
- collect(DISTINCT p.name)[0..5] gathers actor names into a list, then slices to the first 5 — the [0..5] is Cypher list slicing (start index inclusive, end index exclusive), which caps context size so you don't send 50 actors to the LLM
- Second OPTIONAL MATCH does the same for directors
- RETURN produces the columns the retriever expects: text and score are required, the rest are extra metadata
- ORDER BY score DESC keeps the most relevant matches first
-->

---

## What the Query Collects

Starting from each matched movie node:

| Traversal | Pattern | Result |
|-----------|---------|--------|
| Genres | `Movie` → `IN_GENRE` → `Genre` | Genre names |
| Actors | `Person` → `ACTED_IN` → `Movie` | Up to 5 actor names |
| Directors | `Person` → `DIRECTED` → `Movie` | Director names |

Plus: plot text, similarity score, movie title.

---

## Before and After

**Without graph enrichment (plain vector search):**
```
A young man discovers he can travel through time and tries
to change the past to improve his future...
```

**With graph enrichment:**
```
Title: About Time (2013)
Genres: [Comedy, Drama, Romance]
Actors: [Domhnall Gleeson, Rachel McAdams, Bill Nighy]
Directors: [Richard Curtis]
A young man discovers he can travel through time and tries
to change the past to improve his future...
```

---

## Why OPTIONAL MATCH Matters

- **`MATCH`** requires the relationship to exist; missing relationship drops the node entirely
- **`OPTIONAL MATCH`** keeps every matched node; missing relationships return empty lists

- Index search already found relevant results, so graph traversal should never silently remove them
- **Rule of thumb:** use `OPTIONAL MATCH` for any relationship that might not exist on every node

---

## Configure the Provider

To add graph enrichment to an existing provider, you only change one thing:

- **Add `retrieval_query`**: pass your Cypher query as a string parameter
- Everything else (`index_name`, `index_type`, `embedder`, `top_k`, `context_prompt`) stays the same as basic vector search

The provider detects that `retrieval_query` is set and automatically switches to the Cypher-aware retriever under the hood. No other configuration changes are needed.

---

## Summary

In this lesson, you learned:

- **`retrieval_query`** adds Cypher graph traversal after index search
- **Two-step process:** search finds nodes, Cypher enriches with relationships
- **`node` and `score`** are provided by the search; your query traverses from there
- **`OPTIONAL MATCH`** and list limits keep queries robust and context manageable
- **Works with all search modes**: vector, fulltext, and hybrid
- **Result:** the LLM sees titles, genres, actors, directors alongside plot text

**Next:** Fulltext search for keyword matching.
