# Course vs Companion Repo — Alignment Decisions

Each section describes a mismatch between the course lessons and the companion repo solutions, with a recommendation.

---

## 1. First Agent — Domain Mismatch

**Module 1: Introduction / Lesson 3: Creating Your First Agent with Tools**
**Files:** `simple_agent.py` / `solutions/simple_agent.py`

**Lesson:** Neo4j movie-query tool using `neo4j` driver with Cypher
**Solution:** Hardcoded company dictionary with no database

**Recommendation: Update solution to match lesson.**
The course uses the `recommendations` sandbox throughout. The first agent lesson should establish the Neo4j connection pattern that every subsequent lesson builds on. A hardcoded dictionary doesn't prepare students for the rest of the course. Update `simple_agent.py` (exercise + solution) to use Neo4j with the movie query tool from the lesson.

---

## 2. Embedder Class — Different Import/Class

**Lesson:** `OpenAIEmbedder` from `agent_framework_neo4j`
**Solution:** `OpenAIEmbeddings` from `neo4j_graphrag.embeddings.openai`

**Recommendation: Check which is the current API, then align both.**
`agent_framework_neo4j` may have added `OpenAIEmbedder` as a convenience wrapper, or the lesson may reference a class that doesn't exist yet. Need to verify:
- Does `from agent_framework_neo4j import OpenAIEmbedder` actually work?
- If yes, use it — it's simpler (one package to import from).
- If no, update the lesson to use `OpenAIEmbeddings` from `neo4j_graphrag`.

The best practice is to use whatever the `agent_framework_neo4j` package recommends in its docs. If both work, prefer the one with fewer imports.

---

## 3. Neo4j Configuration — os.environ vs Neo4jSettings

**Lesson:** `os.environ["NEO4J_URI"]`, `os.environ["NEO4J_USERNAME"]`, etc.
**Solution:** `Neo4jSettings()` which reads env vars automatically

**Recommendation: Use Neo4jSettings in both.**
`Neo4jSettings` is the pattern provided by `agent_framework_neo4j` specifically for this purpose. It's cleaner, validates configuration, and stores index names alongside connection details. Introducing it early avoids repeating `os.environ` boilerplate in every lesson. Update lessons to teach `Neo4jSettings()` — it's one extra import but removes 3+ lines of `os.environ` calls per file.

The first-agent lesson (before `agent_framework_neo4j` is introduced) should still use `os.environ` since students haven't installed the neo4j provider package yet. Starting from the vector-provider lesson, switch to `Neo4jSettings`.

---

## 4. Simple Context Provider — Name Only vs Name + Age

**Lesson:** Extracts name only
**Solution:** Extracts name AND age

**Recommendation: Use name + age in both.**
The name+age example better demonstrates the power of structured extraction with Pydantic models. Name-only is too simple — it doesn't show why you'd use a `BaseModel` instead of a plain string. The lesson should be expanded slightly to include age extraction. The additional code is minimal (a few extra lines in `before_run` and `after_run`) and makes the example more convincing.

---

## 5. Context Manager — async with vs explicit __aenter__/__aexit__

**Lesson:** `async with provider:`
**Solution:** `provider.__aenter__()` / `provider.__aexit__(None, None, None)`

**Recommendation: Use `async with` in both.**
`async with` is standard Python and what the MAF documentation uses. Explicit dunder calls are an anti-pattern — they bypass exception handling that context managers provide and look unidiomatic. Update all solutions to use `async with provider:`.

---

## 6. Graph-Enriched Cypher — Director Limit Difference

**Lesson:** `collect(DISTINCT d.name) AS directors` (no limit on directors, `[0..5]` on actors)
**Solution:** `collect(DISTINCT p.name)[0..3] AS directors` (limit 3 on directors)

**Recommendation: Align on the lesson's version.**
The lesson's Cypher is more intentional — it limits actors (which can be many) but keeps all directors (typically few per movie). The solution's `[0..3]` on directors is unnecessarily restrictive. Also fix the solution's named relationship variable `[r:ACTED_IN]` to `[:ACTED_IN]` since `r` is never used.

---

## 7. Memory Tools — Missing Verification Section

**Lesson:** Ends after the conversation loop
**Solution:** Includes a `# tag::verify[]` section that inspects stored memories

**Recommendation: Add verification to the lesson.**
Showing students how to inspect what was stored is valuable — it proves the memory system works and helps debugging. Add a short "Verify Stored Memories" section to the lesson that matches the solution's `verify` tag. This also means the lesson and solution will have matching tags for the eventual `include::` directives.

---

## 8. Fulltext Provider — top_k Difference

**Lesson:** `top_k=5`
**Solution:** `top_k=3`

**Recommendation: Use `top_k=5` in both.**
Consistency across all provider lessons (vector, fulltext, graph-enriched) is more important than the specific value. The lesson already uses 5 everywhere. Update the solution to match.

---

## Summary of Actions

| # | Mismatch | Action | Where |
|---|----------|--------|-------|
| 1 | First agent domain | Update solution to use Neo4j movie query | Companion repo |
| 2 | Embedder class | Verify API, then align both | Check packages first |
| 3 | Neo4j config pattern | Use `Neo4jSettings` from vector lesson onward | Lessons (vector+) + verify solutions |
| 4 | Context provider scope | Use name + age in both | Lesson |
| 5 | Context manager | Use `async with` in all solutions | Companion repo |
| 6 | Graph-enriched Cypher | Use lesson's Cypher (no director limit) | Companion repo |
| 7 | Memory verification | Add verify section to lesson | Lesson |
| 8 | Fulltext top_k | Use top_k=5 | Companion repo |
