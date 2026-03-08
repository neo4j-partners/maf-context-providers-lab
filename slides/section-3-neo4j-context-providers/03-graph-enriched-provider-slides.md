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

Vector search returns **text** ranked by semantic similarity.

But your graph contains far more:

- `Movie` → `IN_GENRE` → `Genre`
- `Person` → `ACTED_IN` → `Movie`
- `Person` → `DIRECTED` → `Movie`

**Search finds the right movies. Graph enrichment collects the surrounding context.**

---

## The Two-Step Process

**Step 1 — Index Search**
- Your query is matched against the index (vector, fulltext, or hybrid)
- Returns matched nodes ranked by relevance, each with a similarity `score`

**Step 2 — Graph Traversal (retrieval_query)**
- For each matched node, the provider runs your Cypher `retrieval_query`
- The query traverses outward from the matched node — following relationships to collect genres, actors, directors, or whatever your graph contains
- Returns enriched context combining the original text with structured metadata

The matched node is the **anchor** — you traverse outward from what search found.

---

## The retrieval_query Parameter

The `retrieval_query` is a Cypher query that runs **after** the index search completes:

- It receives each matched `node` and its similarity `score` from the search step
- It defines what graph data to traverse and return — relationships, properties, aggregated lists
- It transforms raw search hits into enriched context before sending to the LLM
- Without it, the provider returns only the text property of matched nodes
- With it, the provider switches to a Cypher-aware retriever (`VectorCypherRetriever` or `HybridCypherRetriever`) that executes your query for each result

---

## How a Retrieval Query Works

Starting from each matched `node` (with its `score` from the index search), the query:

1. **Traverses relationships** — follows paths like `Movie → IN_GENRE → Genre` to collect connected data
2. **Aggregates results** — gathers related values into lists (e.g., all genre names, actor names)
3. **Controls size** — limits collected lists (e.g., top 5 actors) to keep context manageable
4. **Returns structured output** — must include at least `text` and `score`, plus any additional fields you want the LLM to see

You'll write the full Cypher for this in the lab.

---

## What the Query Collects

Starting from each matched movie node:

| Traversal | Pattern | Result |
|-----------|---------|--------|
| Genres | `Movie` → `IN_GENRE` → `Genre` | Genre names |
| Actors | `Person` → `ACTED_IN` → `Movie` | Up to 5 actor names |
| Directors | `Person` → `DIRECTED` → `Movie` | Director names |

Plus: plot text, similarity score, movie title, release year.

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

The LLM now has structured context alongside the text.

---

## Writing Retrieval Queries

**Rules:**
- Use `node` and `score` -- provided by the index search
- Must return at least `text` and `score` columns
- Use `OPTIONAL MATCH` for relationships that may not exist
- Use `ORDER BY score DESC` to maintain relevance ranking
- Limit collected lists (e.g., `[0..5]`) to control context size

**The query defines what "enriched context" means for your use case.**

---

## Why OPTIONAL MATCH Matters

When traversing relationships in your retrieval query:

- **`MATCH`** requires the relationship to exist — if a movie has no actors in the graph, that movie is **dropped entirely** from the results
- **`OPTIONAL MATCH`** keeps every matched node — if the relationship doesn't exist, the collected list is simply empty

This matters because your index search already found relevant results. You don't want the graph traversal step to silently remove them just because one relationship is missing.

**Rule of thumb:** use `OPTIONAL MATCH` for any relationship that might not exist on every node.

---

## Configure the Provider

To add graph enrichment to an existing provider, you only change one thing:

- **Add `retrieval_query`** — pass your Cypher query as a string parameter
- Everything else (`index_name`, `index_type`, `embedder`, `top_k`, `context_prompt`) stays the same as basic vector search

The provider detects that `retrieval_query` is set and automatically switches to the Cypher-aware retriever under the hood. No other configuration changes are needed.

---

## Works with All Search Modes

Graph enrichment is not limited to vector search:

| index_type | Without retrieval_query | With retrieval_query |
|------------|------------------------|---------------------|
| `vector` | `VectorRetriever` | `VectorCypherRetriever` |
| `hybrid` | `HybridRetriever` | `HybridCypherRetriever` |
| `fulltext` | Fulltext retriever | Fulltext retriever |

The same `retrieval_query` Cypher works across modes -- it always receives `node` and `score`.

---

## Experiment Ideas

- Add `node.imdbRating` to the RETURN clause to include ratings
- Change the actor limit from 5 to 3 or 10
- Modify `top_k` to retrieve more or fewer matches
- Update the `context_prompt` to prioritize higher-rated movies
- Add `node.revenue` or `node.budget` for financial context

---

## Summary

In this lesson, you learned:

- **`retrieval_query`** adds Cypher graph traversal after index search
- **Two-step process:** search finds nodes, Cypher enriches with relationships
- **`node` and `score`** are provided by the search; your query traverses from there
- **`OPTIONAL MATCH`** and list limits keep queries robust and context manageable
- **Works with all search modes** -- vector, fulltext, and hybrid
- **Result:** the LLM sees titles, genres, actors, directors alongside plot text

**Next:** Fulltext search for keyword matching.
