# FIX_V4 — Course ↔ Companion Repo Sync Report

**Date:** 2026-02-28

Compares the **course source** (`courses/asciidoc/courses/genai-maf-context-providers/`) against the **companion repo** (`genai-maf-context-providers/`), validated against the **source-of-truth SDKs**:
- `agent-framework` (`/Users/ryanknight/projects/azure/agent-framework`)
- `neo4j-agent-memory` (`/Users/ryanknight/projects/neo4j-labs/agent-memory`)

---

## Summary

The course source and companion repo are **largely in sync on structural patterns** (imports, class names, lifecycle methods). However there are meaningful discrepancies in:
1. Domain content (movie-themed lessons vs generic/tech solutions)
2. Response handling (`print(response)` vs `print(response.text)`)
3. Context provider async lifecycle (`async with provider:` in lessons vs not in solutions for Neo4j providers)
4. Minor cosmetic differences (agent names, instructions, queries, context_prompt text)

---

## Best Practices Verified Against Source SDKs

### Agent Framework (`agent-framework`) — Canonical Patterns

| Pattern | Official Way | Course | Companion Repo |
|---|---|---|---|
| Agent creation | `client.as_agent(...)` or `Agent(client=...)` — both valid | `client.as_agent(...)` | `client.as_agent(...)` |
| Client construction | `OpenAIResponsesClient()` reads env vars; explicit params override | `OpenAIResponsesClient()` | `OpenAIResponsesClient()` |
| Streaming | `agent.run(query, stream=True)` — **no `run_stream()` method exists** | `agent.run(query, stream=True)` | `agent.run(query, stream=True)` |
| Response type | `AgentResponse` object with `.text` property — **NOT a raw string** | Mixed: some `print(response)`, some `print(response.text)` | `print(response.text)` |
| Tool definition | `Annotated[str, Field(description=...)]` with docstring | Matches | Matches |
| Context provider | `before_run()` / `after_run()` hooks, no `async with` on the provider itself | Uses `async with provider:` for Neo4j providers | Uses `async with provider:` for Neo4j providers |

### Neo4j Agent Memory (`neo4j-agent-memory`) — Canonical Patterns

| Pattern | Official Way | Course | Companion Repo |
|---|---|---|---|
| MemoryClient | `async with MemoryClient(settings) as client:` | `async with MemoryClient(settings) as memory_client:` | Same |
| MemorySettings | `MemorySettings(neo4j={...})` or env vars with `NAM_` prefix | `MemorySettings(neo4j={...})` with `os.environ` | Same |
| Neo4jMicrosoftMemory | `Neo4jMicrosoftMemory.from_memory_client(...)` | Matches | Matches |
| Context provider | `memory.context_provider` property | Matches | Matches |
| Memory tools | `create_memory_tools(memory)` returns `list[FunctionTool]` | Matches | Matches |
| search_memory | Returns `dict` with keys `messages`, `entities`, `preferences` | Matches | Matches |

---

## Issue 1: Response Handling — `print(response)` vs `print(response.text)`

**Priority: HIGH — Code won't display correctly**

Per the agent-framework source (`_types.py`), `agent.run()` returns an `AgentResponse` object, not a string. Printing it directly will print the object repr, not the response text. The `.text` property returns the concatenated text.

| Lesson | Course Source | Companion Repo Solution |
|---|---|---|
| M1/L3 First Agent | `agent.run(query, stream=True)` — iterates `update.text` | Same — **MATCH** |
| M2/L2 Simple CP | `print(f"Assistant: {response.text}")` | `print(response.text)` — **MATCH** |
| M3/L2 Vector | `print(response)` — **WRONG** | `print(response.text)` |
| M3/L3 Fulltext | `print(response)` — **WRONG** | `print(response.text)` |
| M3/L4 Hybrid | `print(response)` — **WRONG** | N/A (no solution file) |
| M3/L5 Graph-Enriched | `print(response)` — **WRONG** | `print(response.text)` |
| M4/L3 Memory CP | `print(f"Assistant: {response.text}")` | `print(response.text)` — **MATCH** |
| M4/L4 Memory Tools | `agent.run(query, stream=True, session=session)` — iterates `update.text` | Same — **MATCH** |

**Fix needed in course source:** Update M3/L2, M3/L3, M3/L4, M3/L5 lesson files to use `print(response.text)` instead of `print(response)`.

---

## Issue 2: Domain Content Mismatch (Memory Lessons)

**Priority: MEDIUM — Confusing for students**

The course lessons consistently use a **movie/recommendations** theme. The companion repo solutions for memory lessons use a **tech company** theme. Students reading the lesson will see movie queries, then open the solution and see Apple/Microsoft queries.

| Lesson | Course Queries | Solution Queries |
|---|---|---|
| M4/L3 Memory CP | `"I really enjoy sci-fi movies..."`, `"What did I say my favorite genre was?"`, `"Can you recommend something I might like?"` | `"Hi! I'm interested in learning about Apple's products."`, `"What about their risk factors?"`, `"Can you remind me what we discussed about Apple?"` |
| M4/L4 Memory Tools | `"I love Christopher Nolan movies and anything about space."`, `"What are my movie preferences?"`, `"Based on what you know about me, what should I watch next?"` | `"I prefer concise technical explanations..."`, `"What can you tell me about supply chain risks..."`, `"Remember that I'm particularly interested in Apple and Microsoft."` |
| M4/L3 session_id | `"movie-chat-session"` | `"course-demo"` |
| M4/L4 session_id | `"movie-tools-session"` | `"course-tools-demo"` |

Also affected:
| Lesson | Course Agent Name | Solution Agent Name |
|---|---|---|
| M4/L3 | `"movie-memory-agent"` | `"memory-agent"` |
| M4/L4 | `"movie-assistant"` | `"memory-tools-agent"` |

**Recommendation:** Update companion repo solutions to use movie-themed queries, session IDs, agent names, and instructions matching the course lessons.

---

## Issue 3: Fulltext Query Mismatch

**Priority: LOW — Cosmetic**

| | Course | Solution |
|---|---|---|
| M3/L3 Fulltext query | `"Tell me about movies with Keanu Reeves"` | `"Find movies about space exploration"` |
| M3/L3 Agent name | `"movie-fulltext-agent"` | `"fulltext-agent"` |

**Recommendation:** Align solution query and agent name with the course.

---

## Issue 4: Context Prompt Text Differences

**Priority: LOW — Cosmetic, doesn't affect functionality**

| Lesson | Course `context_prompt` | Solution `context_prompt` |
|---|---|---|
| M3/L2 Vector | `"## Movie Knowledge Graph Context\n..."` | `"## Semantic Search Results\n..."` |
| M3/L3 Fulltext | `"## Movie Knowledge Graph Context\n..."` | `"## Knowledge Graph Context\n..."` |
| M3/L5 Graph-Enriched | `"## Graph-Enriched Movie Context\n...genres, cast, and directors:"` | `"## Graph-Enriched Movie Context\n...movie, actor, genre, and director context:"` |

**Recommendation:** Pick one version and align both. The course versions are more descriptive.

---

## Issue 5: Agent Instructions Differences

**Priority: LOW — Cosmetic**

All Neo4j provider lessons use consistent, concise instructions in the course:
```python
"You are a movie recommendation assistant. Answer questions using the movie data provided in your context."
```

Solutions use longer, more detailed instructions with bullet points. Both are valid. For consistency between what students read and what they see in solutions, align on one style.

---

## Issue 6: `async with provider:` Pattern

**Priority: INFO — Verify correctness**

Both the course and companion repo use `async with provider:` for Neo4j context providers. The base `BaseContextProvider` class does NOT define `__aenter__`/`__aexit__` — these must be defined on `Neo4jContextProvider` from the `agent-framework-neo4j` package (which manages the Neo4j driver connection lifecycle). This is correct and appropriate for resource cleanup.

**Status:** Both repos agree. No fix needed.

---

## Issue 7: `course.adoc` Missing `:repository:` Attribute

**Priority: INFO — Blocks MAF_EXERCISES_SYNC.md integration**

The `course.adoc` does not define a `:repository:` attribute. This means the `include::{repository-raw}/...` pattern described in `MAF_EXERCISES_SYNC.md` cannot be implemented until this is added.

**When ready:** Add `:repository: neo4j-partners/genai-maf-context-providers` to `course.adoc`.

---

## Detailed File-by-File Comparison

### M1/L3: First Agent

| Aspect | Course Source | Solution | Match? |
|---|---|---|---|
| Data source | Hardcoded MOVIES dict | Hardcoded MOVIES dict | **YES** |
| MOVIES content | 4 movies (Inception, Matrix, Pulp Fiction, Dark Knight) | Identical 4 movies | **YES** |
| Tool function | `get_movie_info` with `Annotated[str, Field(...)]` | Identical | **YES** |
| Tool docstring | `"Look up information about a movie including its director, year, genres, and plot summary."` | Identical | **YES** |
| Client | `OpenAIResponsesClient()` | `OpenAIResponsesClient()` | **YES** |
| Agent name | `"movie-info-agent"` | `"movie-info-agent"` | **YES** |
| Agent instructions | Identical | Identical | **YES** |
| Run pattern | `agent.run(query, stream=True)` | `agent.run(query, stream=True)` | **YES** |
| Query | `"Tell me about Inception"` | `"Tell me about Inception"` | **YES** |
| dotenv | Not used (lesson context) | `from dotenv import load_dotenv; load_dotenv()` | Expected diff |

**Verdict: IN SYNC**

---

### M2/L2: Simple Context Provider

| Aspect | Course Source | Solution | Match? |
|---|---|---|---|
| UserInfo model | `name: str \| None = None`, `age: int \| None = None` | Identical | **YES** |
| Class name | `UserInfoMemory` | `UserInfoMemory` | **YES** |
| Base class | `BaseContextProvider` | `BaseContextProvider` | **YES** |
| `source_id` | `"user-info-memory"` | `"user-info-memory"` | **YES** |
| `before_run` handles | name AND age | name AND age | **YES** |
| `after_run` extracts | name AND age | name AND age | **YES** |
| `after_run` early return | `if user_info.name is not None and user_info.age is not None` | Same | **YES** |
| `after_run` message filtering | Uses `context.get_messages(...)` directly | Adds `user_messages` filter for role=="user" with early return | **DIFFERS** |
| `after_run` state update | Implicit (mutating `user_info` in place) | Explicit: `state.setdefault(self.source_id, {})["user_info"] = user_info` | **DIFFERS** |
| Agent name | `"context-provider-agent"` | `"context-provider-agent"` | **YES** |
| Agent instructions | `"You are a friendly assistant. Always address the user by their name when you know it."` | Identical | **YES** |
| Queries | `["Hello, what is the square root of 9?", "My name is Alex and I am 30 years old", "Now, what is the square root of 9?"]` | Identical | **YES** |
| Response handling | `print(f"Assistant: {response.text}")` | `print(response.text)` | Minor diff |
| State inspection | `session.state.get("user-info-memory", {}).get("user_info", UserInfo())` | Identical | **YES** |
| Class docstrings | None | Has docstrings on class and methods | Expected diff |

**Verdict: MOSTLY IN SYNC.** Two minor differences in `after_run()`:
1. Solution adds `user_messages` filter — harmless enhancement
2. Solution has explicit `state[...]["user_info"] = user_info` — redundant since `user_info` is the same object

Neither difference affects behavior. Course version is simpler and cleaner.

---

### M3/L2: Vector Provider

| Aspect | Course Source | Solution | Match? |
|---|---|---|---|
| Embedder import | `from neo4j_graphrag.embeddings.openai import OpenAIEmbeddings` | Same | **YES** |
| Embedder creation | `OpenAIEmbeddings(model="text-embedding-ada-002")` | Same | **YES** |
| Neo4j settings | `Neo4jSettings()` | Same | **YES** |
| Provider params | `uri`, `username`, `get_password()`, `vector_index_name` | Same | **YES** |
| `index_type` | `"vector"` | `"vector"` | **YES** |
| `top_k` | `5` | `5` | **YES** |
| `context_prompt` | `"## Movie Knowledge Graph Context\n..."` | `"## Semantic Search Results\n..."` | **DIFFERS** |
| Agent name | `"movie-knowledge-agent"` | `"vector-agent"` | **DIFFERS** |
| Agent instructions | Short, movie-focused | Longer, generic | **DIFFERS** |
| Query | `"What are some good movies about time travel?"` | `"Find me movies about time travel"` | **CLOSE** |
| Response handling | `print(response)` | `print(response.text)` | **DIFFERS — course is WRONG** |
| `async with provider:` | Yes | Yes | **YES** |

**Verdict: PARTIALLY IN SYNC.** Core setup matches. Cosmetic differences in prompt/name/instructions. Course has `print(response)` bug.

---

### M3/L3: Fulltext Provider

| Aspect | Course Source | Solution | Match? |
|---|---|---|---|
| Provider import | `Neo4jContextProvider, Neo4jSettings` | Same | **YES** |
| Index name | `neo4j_settings.fulltext_index_name` | Same | **YES** |
| `index_type` | `"fulltext"` | `"fulltext"` | **YES** |
| `top_k` | `5` | `5` | **YES** |
| `context_prompt` | `"## Movie Knowledge Graph Context\n..."` | `"## Knowledge Graph Context\n..."` | **DIFFERS** |
| Agent name | `"movie-fulltext-agent"` | `"fulltext-agent"` | **DIFFERS** |
| Query | `"Tell me about movies with Keanu Reeves"` | `"Find movies about space exploration"` | **DIFFERS** |
| Response handling | `print(response)` | `print(response.text)` | **DIFFERS — course is WRONG** |
| `async with provider:` | Yes | Yes | **YES** |

**Verdict: PARTIALLY IN SYNC.** Core setup matches. Query and cosmetic diffs. Course has `print(response)` bug.

---

### M3/L4: Hybrid Provider

No companion repo solution exists. Course-only lesson. The code patterns are consistent with the other M3 lessons (uses `Neo4jSettings`, `OpenAIEmbeddings`, `async with provider:`). Has the same `print(response)` bug.

---

### M3/L5: Graph-Enriched Provider

| Aspect | Course Source | Solution | Match? |
|---|---|---|---|
| RETRIEVAL_QUERY Cypher | Full query with IN_GENRE, ACTED_IN[0..5], DIRECTED | **Identical** | **YES** |
| Embedder | `OpenAIEmbeddings(model="text-embedding-ada-002")` | Same | **YES** |
| Provider params | Same settings pattern | Same | **YES** |
| `retrieval_query` param | `RETRIEVAL_QUERY` | Same | **YES** |
| `context_prompt` | `"...genres, cast, and directors:"` | `"...movie, actor, genre, and director context:"` | **DIFFERS** |
| Agent name | `"movie-enriched-agent"` | `"graph-enriched-agent"` | **DIFFERS** |
| Query | `"What sci-fi movies involve artificial intelligence?"` | `"What are some good science fiction movies and who stars in them?"` | **DIFFERS** |
| Response handling | `print(response)` | `print(response.text)` | **DIFFERS — course is WRONG** |

**Verdict: PARTIALLY IN SYNC.** Critical Cypher query matches perfectly. Cosmetic diffs. Course has `print(response)` bug.

---

### M4/L2: Entity Extraction

Conceptual/theory lesson — no companion repo file. Uses `os.environ` for `MemorySettings` configuration, which matches the companion repo pattern and is intentional (shares env vars with Neo4j provider lessons).

---

### M4/L3: Memory Context Provider

| Aspect | Course Source | Solution | Match? |
|---|---|---|---|
| MemorySettings | `MemorySettings(neo4j={...})` with `os.environ` | Same | **YES** |
| MemoryClient | `async with MemoryClient(settings) as memory_client:` | Same | **YES** |
| Memory creation | `Neo4jMicrosoftMemory.from_memory_client(...)` | Same | **YES** |
| `include_short_term` | `True` | `True` | **YES** |
| `include_long_term` | `True` | `True` | **YES** |
| `include_reasoning` | `True` | `True` | **YES** |
| `extract_entities` | `True` | `True` | **YES** |
| Context provider | `memory.context_provider` | Same | **YES** |
| Client | `OpenAIResponsesClient()` | `OpenAIResponsesClient()` | **YES** |
| Session ID | `"movie-chat-session"` | `"course-demo"` | **DIFFERS** |
| Agent name | `"movie-memory-agent"` | `"memory-agent"` | **DIFFERS** |
| Instructions | Movie-focused | Generic | **DIFFERS** |
| Queries | Movie preferences | Apple products | **DIFFERS** |
| Response handling | `print(f"Assistant: {response.text}")` | `print(response.text)` | Close match |
| search_memory | `query="sci-fi movies"` | `query="Apple products and risks"` | **DIFFERS** |

**Verdict: STRUCTURALLY IN SYNC.** All setup/config/patterns match. Domain content differs (movies vs tech).

---

### M4/L4: Memory Tools

| Aspect | Course Source | Solution | Match? |
|---|---|---|---|
| MemorySettings | Same pattern | Same | **YES** |
| MemoryClient | `async with MemoryClient(settings) as memory_client:` | Same | **YES** |
| Memory creation | `Neo4jMicrosoftMemory.from_memory_client(...)` | Same | **YES** |
| `include_reasoning` | Not included | Not included | **YES** |
| `create_memory_tools` | `create_memory_tools(memory)` | Same | **YES** |
| Combined pattern | `tools=tools, context_providers=[memory.context_provider]` | Same | **YES** |
| Session ID | `"movie-tools-session"` | `"course-tools-demo"` | **DIFFERS** |
| Agent name | `"movie-assistant"` | `"memory-tools-agent"` | **DIFFERS** |
| Instructions | Movie-focused with tool guidance | Generic with numbered capabilities | **DIFFERS** |
| Queries | Movie preferences (Christopher Nolan, space) | Tech preferences (Apple, Microsoft) | **DIFFERS** |
| Streaming | `agent.run(query, stream=True, session=session)` | `agent.run(query, session=session, stream=True)` | Param order diff only |
| Verify section | Yes — searches preferences, entities, message count | Yes — identical pattern | **YES** |

**Verdict: STRUCTURALLY IN SYNC.** All setup/config/patterns match. Domain content differs.

---

## Exercise Stubs Assessment

All exercise stubs are **correctly aligned with solutions**:

| Stub File | Imports Match Solution? | TODO Comments Align? | Provided Code Correct? |
|---|---|---|---|
| `simple_agent.py` | YES | YES | MOVIES dict + tool provided verbatim |
| `simple_context_provider.py` | YES | YES | UserInfo model provided |
| `vector_context_provider.py` | YES | YES | Neo4jSettings loaded |
| `fulltext_context_provider.py` | YES | YES | Neo4jSettings loaded |
| `graph_enriched_provider.py` | YES | YES | Neo4jSettings loaded |
| `memory_context_provider.py` | YES | YES | All imports present |
| `memory_tools_agent.py` | YES | YES | All imports including create_memory_tools |

**Verdict: Stubs are clean.** No changes needed.

---

## Action Items

| # | Action | Priority | Where to Fix |
|---|---|---|---|
| 1 | Fix `print(response)` → `print(response.text)` in M3/L2, M3/L3, M3/L4, M3/L5 | **HIGH** | Course source (4 lesson files) |
| 2 | Update M4/L3 solution to movie-themed queries, session_id, agent name | **MEDIUM** | Companion repo (`solutions/memory_context_provider.py`) |
| 3 | Update M4/L4 solution to movie-themed queries, session_id, agent name | **MEDIUM** | Companion repo (`solutions/memory_tools_agent.py`) |
| 4 | Update M3/L3 solution query to match course (`"Tell me about movies with Keanu Reeves"`) | **LOW** | Companion repo (`solutions/fulltext_context_provider.py`) |
| 5 | Align `context_prompt` text between course and solutions (M3/L2, M3/L3, M3/L5) | **LOW** | Pick one, update the other |
| 6 | Align agent names between course and solutions (M3/L2, M3/L3, M3/L5) | **LOW** | Pick one, update the other |
| 7 | Add `:repository: neo4j-partners/genai-maf-context-providers` to `course.adoc` | **LOW** | Course source (when ready for include:: integration) |
| 8 | Re-run `sync_course.py` after all fixes | **REQUIRED** | `maf-context-providers-lab/` |

---

## What's Already Correct (No Changes Needed)

- All imports (`agent_framework`, `agent_framework_neo4j`, `neo4j_graphrag`, `neo4j_agent_memory`)
- All class names (`OpenAIResponsesClient`, `Neo4jContextProvider`, `Neo4jSettings`, `OpenAIEmbeddings`, `MemoryClient`, `MemorySettings`, `Neo4jMicrosoftMemory`, `BaseContextProvider`)
- All factory/construction patterns (`client.as_agent()`, `Neo4jMicrosoftMemory.from_memory_client()`, `create_memory_tools()`)
- All lifecycle patterns (`async with MemoryClient(...)`, `async with provider:`)
- Streaming pattern (`agent.run(query, stream=True)`)
- Tool definition pattern (`Annotated[str, Field(description=...)]`)
- Context provider hooks (`before_run`, `after_run` signatures)
- Graph-enriched retrieval Cypher query (exact match)
- Exercise stub files (all clean)
- `requirements.txt` package versions
