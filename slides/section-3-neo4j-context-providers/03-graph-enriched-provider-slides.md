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

```
Step 1: Index Search
    Query → find matching movies → ranked by relevance
        ↓
    Returns: node (matched movie) + score

Step 2: Graph Traversal (retrieval_query)
    For each matched node, execute Cypher
        ↓
    Traverse relationships: movie → genres, actors, directors
        ↓
    Returns: enriched context with structured metadata
```

The movie is the **anchor** -- you traverse outward from what search found.

---

## The retrieval_query Parameter

Adding a `retrieval_query` enables graph enrichment:

```python
provider = Neo4jContextProvider(
    index_name="moviePlots",
    index_type="vector",
    embedder=embedder,
    retrieval_query=RETRIEVAL_QUERY,  # Cypher for traversal
    top_k=5,
)
```

When set, the provider uses `VectorCypherRetriever` instead of `VectorRetriever`.

---

## Example Retrieval Query

```cypher
MATCH (node)-[:IN_GENRE]->(g:Genre)
WITH node, score, collect(DISTINCT g.name) AS genres
OPTIONAL MATCH (p:Person)-[:ACTED_IN]->(node)
WITH node, score, genres, collect(DISTINCT p.name)[0..5] AS actors
OPTIONAL MATCH (d:Person)-[:DIRECTED]->(node)
WITH node, score, genres, actors, collect(DISTINCT d.name) AS directors
WHERE score IS NOT NULL
RETURN
    node.plot AS text,
    score,
    node.title AS title,
    node.released AS released,
    genres,
    actors,
    directors
ORDER BY score DESC
```

`node` and `score` come from the index search. The rest is graph traversal.

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

**Without OPTIONAL MATCH:**
```cypher
MATCH (p:Person)-[:ACTED_IN]->(node)
```
Only returns movies that have actors in the graph. Movies without actor data are dropped.

**With OPTIONAL MATCH:**
```cypher
OPTIONAL MATCH (p:Person)-[:ACTED_IN]->(node)
```
Returns all matched movies; actor list is empty if none exist.

**Use OPTIONAL MATCH** for complete results.

---

## Configure the Provider

```python
provider = Neo4jContextProvider(
    uri=neo4j_settings.uri,
    username=neo4j_settings.username,
    password=neo4j_settings.get_password(),
    index_name=neo4j_settings.vector_index_name,
    index_type="vector",
    retrieval_query=RETRIEVAL_QUERY,
    embedder=embedder,
    top_k=5,
    context_prompt=(
        "## Graph-Enriched Movie Context\n"
        "The following combines semantic search with graph traversal "
        "to provide movie, actor, genre, and director context:"
    ),
)
```

The only difference from basic vector search is `retrieval_query`.

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
