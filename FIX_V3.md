# FIX_V3 — Sync Status Report

**Date:** 2026-02-28

This document compares the **Antora lab site** (`maf-context-providers-lab/site/`) with the **companion exercise repo** (`genai-maf-context-providers/`) and the **course source files** (in `courses/` repo).

---

## TL;DR

1. **Course source → Antora site: OUT OF SYNC.** All fixes from FIX.md and FIXES_V2.md were applied to the course source files but `sync_course.py` was never re-run. Every Antora page still has the old anti-patterns.
2. **Course source → Companion repo solutions: MOSTLY IN SYNC** on code patterns, but diverge on domain content (movie-themed lessons vs generic/tech-themed solutions), agent names, instructions, and queries.
3. **Companion repo exercise stubs → Solutions: IN SYNC.** Stubs align with solutions (same imports, same classes).
4. **Companion repo exercise stubs → Antora lessons: OUT OF SYNC.** Stubs use the correct patterns (e.g., `OpenAIEmbeddings`, `Neo4jSettings`) but the Antora pages still show the old patterns.

---

## Issue 1: Antora Site Not Regenerated

**Priority: HIGH — Blocking**

The `sync_course.py` script needs to be re-run to regenerate all Antora pages from the updated course source files. Every page is stale.

| Antora Page | Anti-Patterns Still Present |
|---|---|
| `1-3-first-agent.adoc` | `neo4j.GraphDatabase.driver`, `import neo4j`, `OpenAIResponsesClient(api_key=..., model=...)`, agent name `"movie-agent"` |
| `2-2-simple-context-provider.adoc` | Name-only `before_run()`/`after_run()`, `Agent(client=...)`, `OpenAIResponsesClient(api_key=..., model=...)` |
| `3-2-vector-provider.adoc` | `OpenAIEmbedder` (nonexistent class), `os.environ` for Neo4j config |
| `3-3-fulltext-provider.adoc` | `OpenAIResponsesClient(api_key=..., model=...)`, `os.environ` for Neo4j config |
| `3-5-graph-enriched-provider.adoc` | `OpenAIEmbedder` (nonexistent class), `os.environ` for Neo4j config |
| `4-3-memory-context-provider.adoc` | `__aenter__()`, `__aexit__()`, `OpenAIResponsesClient(api_key=..., model=...)` |
| `4-4-memory-tools.adoc` | `__aexit__()`, missing verification section |

**Fix:** Run `uv run sync_course.py` from `maf-context-providers-lab/` to regenerate all pages.

---

## Issue 2: Lesson–Solution Domain Content Mismatch

**Priority: MEDIUM — Cosmetic but confusing for students**

The course lessons use movie-themed examples throughout (consistent with the Neo4j Recommendations sandbox). The companion repo solutions use different domain content for the memory lessons. This means students reading the lesson will see movie queries, but when they open the solution file they'll see tech company queries.

| Lesson | Lesson Domain | Solution Domain |
|---|---|---|
| M1/L3 First Agent | Movies (dict) | Movies (dict) — **MATCH** |
| M2/L2 Simple CP | "Alice", name-only → name+age | "Alex", name+age — **partial match** (name differs) |
| M3/L2 Vector | "time travel" movies | "time travel" movies — **MATCH** |
| M3/L3 Fulltext | "Keanu Reeves" movies | "space exploration" — **MISMATCH** |
| M3/L5 Graph-Enriched | "sci-fi + AI" movies | "science fiction" movies — **close match** |
| M4/L3 Memory CP | Movie preferences, session `"movie-chat-session"` | Apple products, session `"course-demo"` — **MISMATCH** |
| M4/L4 Memory Tools | Christopher Nolan preferences, session `"movie-tools-session"` | Tech preferences, session `"course-tools-demo"` — **MISMATCH** |

**Recommendation:** Update solution files for M3/L3, M4/L3, and M4/L4 to use movie-themed queries/sessions matching the lessons. This keeps the companion repo consistent with the course content students are reading.

---

## Issue 3: Response Handling Inconsistency

**Priority: LOW — May cause student confusion**

Lessons use `print(response)` (treating the response as a string), while solutions use `print(response.text)` (accessing `.text` attribute). This depends on how the MAF `agent.run()` return type works — if it returns a string directly, `print(response)` is fine; if it returns a response object, `.text` is needed.

| File | Lesson Pattern | Solution Pattern |
|---|---|---|
| M3/L2 Vector | `print(response)` | `print(response.text)` |
| M3/L3 Fulltext | `print(response)` | `print(response.text)` |
| M3/L5 Graph-Enriched | `print(response)` | `print(response.text)` |
| M4/L3 Memory CP | `print(f"Assistant: {response}")` | `print(response.text)` |

**Recommendation:** Verify which pattern is correct for the current MAF SDK version and align both lesson and solution on the same approach.

---

## Issue 4: Streaming API Inconsistency (M1/L3)

**Priority: LOW**

The lesson (Antora page) uses `agent.run_stream("...")` while the solution uses `agent.run("...", stream=True)`. These may be aliases, but students will see different APIs.

**Recommendation:** Verify which API is current and align both.

---

## Issue 5: `3-4-hybrid-provider.adoc` Has No Exercise/Solution

**Priority: INFO — Expected**

The hybrid provider lesson exists in the Antora site but has no corresponding exercise stub or solution file in the companion repo. This appears intentional (conceptual/optional lesson), but worth confirming.

---

## Issue 6: AsciiDoc Tags Unused

**Priority: INFO — Future enhancement tracked in MAF_EXERCISES_SYNC.md**

Solution files have `tag::` / `end::` markers (e.g., `tag::provider[]`, `tag::agent[]`, `tag::run[]`) but lesson pages use inline code blocks and never reference these tags via `include::` directives. The `MAF_EXERCISES_SYNC.md` document describes a plan to integrate these tags using `include::{repository-raw}/{branch}/file.py[tag=**]` directives, but this has not been implemented yet.

---

## Action Items

| # | Action | Priority | Where |
|---|---|---|---|
| 1 | Re-run `sync_course.py` to regenerate Antora pages | HIGH | `maf-context-providers-lab/` |
| 2 | Rebuild Antora site (`npm run build` in `site/`) | HIGH | `maf-context-providers-lab/site/` |
| 3 | Update M3/L3 solution queries to movie theme | MEDIUM | `genai-maf-context-providers/` |
| 4 | Update M4/L3 solution to movie theme | MEDIUM | `genai-maf-context-providers/` |
| 5 | Update M4/L4 solution to movie theme | MEDIUM | `genai-maf-context-providers/` |
| 6 | Verify `response` vs `response.text` and align | LOW | Both repos |
| 7 | Verify `run_stream()` vs `run(stream=True)` and align | LOW | Both repos |
| 8 | Implement `include::` tag integration (per MAF_EXERCISES_SYNC.md) | LOW | `maf-context-providers-lab/` |

---

## Previously Completed (from FIX.md + FIXES_V2.md)

These fixes were applied to the **course source files** (in `courses/` repo) and/or the **companion repo solutions**. They are confirmed done but the Antora site pages have not been regenerated to reflect them.

| Fix | Description | Applied To |
|---|---|---|
| FIX #1 | First agent: hardcoded movie dict (no Neo4j) | Course source + companion repo |
| FIX #2 | `OpenAIEmbedder` → `OpenAIEmbeddings` | Course source |
| FIX #3 | `os.environ` → `Neo4jSettings` | Course source |
| FIX #4 | Simple CP: name + age | Course source |
| FIX #5 | `async with` pattern (no `__aenter__`/`__aexit__`) | Companion repo solutions |
| FIX #6 | Graph-enriched Cypher alignment | Companion repo solution |
| FIX #7 | Memory verification section added | Course source |
| FIX #8 | Fulltext `top_k=5` | Companion repo solution |
| FIXES_V2 F1-F7 | All lesson anti-patterns fixed | Course source |
