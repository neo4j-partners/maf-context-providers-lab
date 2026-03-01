# FIXES_V2 — Comprehensive Lesson Fix Plan

All fixes target lesson `.adoc` files in:
`/Users/ryanknight/projects/graphacademy/courses/asciidoc/courses/genai-maf-context-providers/`

Companion repo exercises are clean (no anti-patterns). Companion repo solutions were fixed in FIX.md (items #1, #5, #6, #8 — all DONE).

---

## Completed (from FIX.md)

| Fix | Scope | Status |
|-----|-------|--------|
| R2: `OpenAIEmbedder` → `OpenAIEmbeddings` | M3/L2 vector, M3/L3 graph-enriched, M3/L4 hybrid | **DONE** |
| R3: `os.environ` → `Neo4jSettings` for Neo4j provider params | M3/L2, M3/L3, M3/L4, M3/L5 | **DONE** |
| R5: Add memory verification section | M4/L4 memory tools | **DONE** |

---

## Remaining Fixes

### F1. First-agent lesson — replace Neo4j driver with movie dictionary (M1/L3)

**File:** `modules/1-introduction/lessons/3-first-agent/lesson.adoc`

**Current (anti-patterns):**
- Lines 13–14: `import os` + line 17: `OpenAIResponsesClient(api_key=os.environ[...], model=os.environ[...])`
- Lines 29–52: `import neo4j`, `neo4j.GraphDatabase.driver(os.environ[...])`, Cypher query tool
- Line 63: agent name `"movie-agent"`

**Fix:**
1. Replace `OpenAIResponsesClient(api_key=..., model=...)` with `OpenAIResponsesClient()`
2. Replace Neo4j driver + Cypher tool with hardcoded `MOVIES` dictionary and `get_movie_info` from companion repo solution (`solutions/simple_agent.py`)
3. Update agent name to `"movie-info-agent"`
4. Update agent instructions to match companion repo
5. Update narrative text (line 55) — remove Neo4j references, explain movie dictionary tool
6. Keep the teaching points about tool invocation and limitations

**Companion repo reference:** `solutions/simple_agent.py` tags: `movies`, `tool`, `agent`, `run`

---

### F2. Simple context provider — add age handling (M2/L2)

**File:** `modules/2-context-providers/lessons/2-simple-context-provider/lesson.adoc`

**Current (anti-patterns):**
- Lines 110–113: `OpenAIResponsesClient(api_key=os.environ[...], model=os.environ[...])`
- Lines 116–120: `Agent(client=client, ...)` instead of `client.as_agent(...)`
- `before_run()` only handles name (not age)
- `after_run()` only extracts name (not age)
- Line 15: `UserInfo` already has `age` field but it's unused in the logic

**Fix:**
1. Replace `OpenAIResponsesClient(api_key=..., model=...)` with `OpenAIResponsesClient()`
2. Replace `Agent(client=client, ...)` with `client.as_agent(...)` to match all other lessons
3. Update `before_run()` to handle both name and age (add age instructions like companion repo)
4. Update `after_run()` to extract both name and age
5. Update example messages: `"My name is Alex and I am 30 years old"`
6. Add state inspection at end showing both name and age

**Companion repo reference:** `solutions/simple_context_provider.py` tags: `model`, `provider`, `agent`, `run`

---

### F3. Fulltext provider — simplify OpenAIResponsesClient (M3/L3)

**File:** `modules/3-neo4j-context-providers/lessons/3-fulltext-provider/lesson.adoc`

**Current (anti-pattern):**
- Lines 88–91: `OpenAIResponsesClient(api_key=os.environ["OPENAI_API_KEY"], model=os.environ["OPENAI_RESPONSES_MODEL_ID"])`

**Fix:**
Replace with `OpenAIResponsesClient()` (reads from env automatically).

---

### F4. Hybrid provider — simplify OpenAIResponsesClient (M3/L4)

**File:** `modules/3-neo4j-context-providers/lessons/4-hybrid-provider/lesson.adoc`

**Current (anti-pattern):**
- Lines 65–68: `OpenAIResponsesClient(api_key=os.environ["OPENAI_API_KEY"], model=os.environ["OPENAI_RESPONSES_MODEL_ID"])`

**Fix:**
Replace with `OpenAIResponsesClient()`.

---

### F5. Entity extraction — replace os.environ with MemorySettings env auto-loading (M4/L2)

**File:** `modules/4-agent-memory/lessons/2-entity-extraction/lesson.adoc`

**Current (anti-pattern):**
- Lines 27–29: `os.environ["NEO4J_URI"]`, `os.environ["NEO4J_USERNAME"]`, `SecretStr(os.environ["NEO4J_PASSWORD"])`

**Best practice from neo4j-agent-memory:**
`MemorySettings` is a Pydantic `BaseSettings` class with `env_prefix="NAM_"` and `env_file=".env"`. It reads environment variables automatically:
- `NAM_NEO4J__URI` → `neo4j.uri`
- `NAM_NEO4J__USERNAME` → `neo4j.username`
- `NAM_NEO4J__PASSWORD` → `neo4j.password`

**However:** The companion repo solutions (`memory_context_provider.py`, `memory_tools_agent.py`) explicitly pass `os.environ` values to `MemorySettings(neo4j={...})`. This is because the course `.env` uses `NEO4J_URI` (not `NAM_NEO4J__URI`), shared with the Neo4j provider lessons.

**Decision:** Keep the explicit `os.environ` pattern in memory lessons to match the companion repo and share `.env` variables with Neo4j provider lessons. Add a note explaining that `MemorySettings` supports auto-loading from `NAM_`-prefixed env vars.

**Note to add:** After the code block, add:
> `MemorySettings` also supports automatic environment variable loading with the `NAM_` prefix (e.g., `NAM_NEO4J__URI`). The explicit configuration shown here reuses the same `NEO4J_URI`, `NEO4J_USERNAME`, and `NEO4J_PASSWORD` environment variables used by the Neo4j context provider lessons.

---

### F6. Memory context provider — fix `__aenter__`/`__aexit__` and OpenAIResponsesClient (M4/L3)

**File:** `modules/4-agent-memory/lessons/3-memory-context-provider/lesson.adoc`

**Current (anti-patterns):**
- Line 28: `await memory_client.__aenter__()` — should use `async with`
- Lines 71–74: `OpenAIResponsesClient(api_key=os.environ[...], model=os.environ[...])` — should be `OpenAIResponsesClient()`
- Line 118: `await memory_client.__aexit__(None, None, None)` — should use `async with`

**Fix:**
1. Restructure the "Configure Memory Settings" section to use `async with MemoryClient(settings) as memory_client:` pattern
2. Replace `OpenAIResponsesClient(api_key=..., model=...)` with `OpenAIResponsesClient()`
3. Remove explicit `__aexit__` call — the `async with` block handles cleanup
4. Since the lesson shows code in separate sections (settings → memory → agent → run), restructure the "Run a Multi-Turn Conversation" code to show the full `async with` structure

**Best practice from neo4j-agent-memory:**
```python
async with MemoryClient(settings) as memory_client:
    memory = Neo4jMicrosoftMemory.from_memory_client(
        memory_client=memory_client,
        session_id=session_id,
        ...
    )
    # ... use memory ...
```
Source: `examples/basic_usage.py` line 136, `__init__.py` lines 314–321

**Companion repo reference:** `solutions/memory_context_provider.py` (already fixed to use `async with`)

---

### F7. Memory tools — fix `__aexit__` (M4/L4)

**File:** `modules/4-agent-memory/lessons/4-memory-tools/lesson.adoc`

**Current (anti-pattern):**
- Line 102: `await memory_client.__aexit__(None, None, None)`

**Fix:**
Remove the `__aexit__` line. The "Run a Conversation" code block should be wrapped in the `async with MemoryClient(settings) as memory_client:` context manager (or reference that it runs inside one from the setup shown in the previous lesson).

**Companion repo reference:** `solutions/memory_tools_agent.py` (already fixed to use `async with`)

---

## Companion Repo Exercise Notes

The exercise skeleton files are clean — no anti-patterns found. They use TODO comments to guide students. No changes needed.

The companion repo solutions were previously fixed:
- `simple_agent.py` — movie dictionary (FIX.md #1 DONE)
- All 5 solution files — `async with` pattern (FIX.md #5 DONE)
- `graph_enriched_provider.py` — Cypher fix (FIX.md #6 DONE)
- `fulltext_context_provider.py` — `top_k=5` (FIX.md #8 DONE)

---

## Summary

| Fix | File | Anti-patterns | Status |
|-----|------|---------------|--------|
| F1 | M1/L3 first-agent | `os.environ`, neo4j driver, wrong agent name | **DONE** |
| F2 | M2/L2 simple-context-provider | `os.environ`, `Agent(client=...)`, name-only logic | **DONE** |
| F3 | M3/L3 fulltext-provider | `OpenAIResponsesClient(api_key=..., model=...)` | **DONE** |
| F4 | M3/L4 hybrid-provider | `OpenAIResponsesClient(api_key=..., model=...)` | **DONE** |
| F5 | M4/L2 entity-extraction | `os.environ` in MemorySettings — keep but add note | **DONE** |
| F6 | M4/L3 memory-context-provider | `__aenter__`, `__aexit__`, `OpenAIResponsesClient(api_key=...)` | **DONE** |
| F7 | M4/L4 memory-tools | `__aexit__` | **DONE** |
