# Course vs Companion Repo — Alignment Decisions

Each section describes a mismatch between the course lessons and the companion repo solutions, with a recommendation, research findings, and final decision.

---

## 1. First Agent — Domain Mismatch

**Module 1: Introduction / Lesson 3: Creating Your First Agent with Tools**
**Files:** `simple_agent.py` / `solutions/simple_agent.py`

**Lesson:** Neo4j movie-query tool using `neo4j` driver with Cypher
**Solution:** Hardcoded company dictionary with no database

**Answer:** What could be an example agent that follows the movie/recommendations theme without requiring a Neo4j connection?

### Final Decision: Use a hardcoded movie dictionary

Since this is Lesson 3 (before Neo4j provider packages are introduced), the tool should NOT require a Neo4j connection. Replace the company dictionary with a movie dictionary that matches the course's recommendations theme. This gives thematic consistency while keeping the lesson focused on agent/tool basics.

Example tool:

```python
MOVIES = {
    "INCEPTION": {
        "title": "Inception",
        "director": "Christopher Nolan",
        "year": "2010",
        "genres": ["Science Fiction", "Thriller"],
        "plot_summary": "A skilled thief who steals corporate secrets through dream-sharing technology"
    },
    "THE MATRIX": {
        "title": "The Matrix",
        "director": "Lana Wachowski, Lilly Wachowski",
        "year": "1999",
        "genres": ["Science Fiction", "Action"],
        "plot_summary": "A computer hacker learns about the true nature of his reality"
    },
    "PULP FICTION": {
        "title": "Pulp Fiction",
        "director": "Quentin Tarantino",
        "year": "1994",
        "genres": ["Crime", "Drama"],
        "plot_summary": "The lives of two mob hitmen, a boxer, and a gangster intertwine"
    },
    "THE DARK KNIGHT": {
        "title": "The Dark Knight",
        "director": "Christopher Nolan",
        "year": "2008",
        "genres": ["Action", "Crime", "Drama"],
        "plot_summary": "Batman faces off against a criminal mastermind known as the Joker"
    },
}

def get_movie_info(movie_title: str) -> str:
    """Look up information about a movie including its director, year, genres, and plot summary."""
    key = movie_title.upper().strip()
    info = MOVIES.get(key)
    if not info:
        for k, v in MOVIES.items():
            if key in k or k in key:
                info = v
                break
    if info:
        return (
            f"Title: {info['title']}\n"
            f"Director: {info['director']}\n"
            f"Year: {info['year']}\n"
            f"Genres: {', '.join(info['genres'])}\n"
            f"Plot: {info['plot_summary']}"
        )
    available = ", ".join(m["title"] for m in MOVIES.values())
    return f"Movie '{movie_title}' not found. Available movies: {available}"
```

**Update:** Companion repo (both exercise + solution). Also update the lesson to use the same movie dictionary instead of the Neo4j driver example.

**Status: DONE** — Updated `simple_agent.py` (exercise + solution) with movie dictionary (Inception, The Matrix, Pulp Fiction, The Dark Knight). Renamed tag from `companies` to `movies`, tool from `get_company_info` to `get_movie_info`, agent name to `movie-info-agent`.

---

## 2. Embedder Class — Different Import/Class

**Module 3: Neo4j Context Providers / Lesson 2: Vector Search** and **Lesson 5: Graph-Enriched Retrieval**
**Files:** `vector_context_provider.py`, `graph_enriched_provider.py` + their solutions

**Lesson:** `OpenAIEmbedder` from `agent_framework_neo4j`
**Solution:** `OpenAIEmbeddings` from `neo4j_graphrag.embeddings.openai`

**Answer:** Reviewed `/Users/ryanknight/projects/azure/neo4j-maf-provider`

### Research Findings

The `agent_framework_neo4j` package exports these classes (from `__init__.py`):
- `AzureAIEmbedder` — uses Azure AI Inference SDK with credential-based auth
- `Neo4jContextProvider`
- `Neo4jSettings`
- `AzureAISettings`
- `FulltextRetriever`

**There is NO `OpenAIEmbedder` class.** The lesson references a class that does not exist in the package. The only embedder exported is `AzureAIEmbedder`, which requires Azure credentials.

The solution's approach (`OpenAIEmbeddings` from `neo4j_graphrag`) is correct for an OpenAI-key-based course. Since this course uses OpenAI (not Azure), `OpenAIEmbeddings` from `neo4j_graphrag` is the right choice.

### Final Decision: Use `OpenAIEmbeddings` from `neo4j_graphrag` in both

Update lessons to use:
```python
from neo4j_graphrag.embeddings.openai import OpenAIEmbeddings

embedder = OpenAIEmbeddings(model="text-embedding-ada-002")
```

This is what the solutions already use, and it's the correct API for an OpenAI-based course. The `AzureAIEmbedder` is for Azure-credential-based deployments.

**Update:** Lessons (vector + graph-enriched) — fix the import and class name.

---

## 3. Neo4j Configuration — os.environ vs Neo4jSettings

**Module 3: Neo4j Context Providers / Lessons 2–5** (Vector, Fulltext, Hybrid, Graph-Enriched)
**Files:** `vector_context_provider.py`, `fulltext_context_provider.py`, `graph_enriched_provider.py` + their solutions

**Lesson:** `os.environ["NEO4J_URI"]`, `os.environ["NEO4J_USERNAME"]`, etc.
**Solution:** `Neo4jSettings()` which reads env vars automatically

**Answer:** Use Neo4jSettings in all exercises.

### Research Findings

`Neo4jSettings` (from `agent_framework_neo4j`) has these fields:
- `uri: str | None` — Neo4j connection URI
- `username: str | None` — Neo4j username
- `password: SecretStr | None` — Neo4j password
- `vector_index_name: str` — default `"chunkEmbeddings"`
- `fulltext_index_name: str` — default `"chunkFulltext"`
- `get_password() -> str | None` — safely retrieve password value

The official samples in `neo4j-maf-provider` all use `Neo4jSettings()`. It reads from environment variables automatically, validates configuration, and keeps index names alongside connection details.

### Final Decision: Use `Neo4jSettings` in all Neo4j provider exercises

Update all lessons (M3/L2–L5) to use:
```python
from agent_framework_neo4j import Neo4jSettings

neo4j_settings = Neo4jSettings()

provider = Neo4jContextProvider(
    uri=neo4j_settings.uri,
    username=neo4j_settings.username,
    password=neo4j_settings.get_password(),
    index_name=neo4j_settings.vector_index_name,
    ...
)
```

**Note:** The `.env` file and setup instructions need to document the expected environment variable names that `Neo4jSettings` reads. Also update the default index names in the `.env.example` since `Neo4jSettings` defaults to `"chunkEmbeddings"` / `"chunkFulltext"` but the course sandbox uses `"moviePlots"` / `"moviePlotsFulltext"`.

**Update:** Lessons (M3/L2–L5) — replace `os.environ` with `Neo4jSettings`. Solutions already use it.

---

## 4. Simple Context Provider — Name Only vs Name + Age

**Module 2: Context Providers / Lesson 2: Building a Simple Context Provider**
**Files:** `simple_context_provider.py` / `solutions/simple_context_provider.py`

**Lesson:** Extracts name only
**Solution:** Extracts name AND age

**Answer:** Use name + age in both.

### Final Decision: Use name + age in both

The name+age example better demonstrates structured extraction with Pydantic models. Update the lesson to include age extraction in both `before_run()` and `after_run()`, matching the solution.

**Update:** Lesson — expand to include age extraction.

---

## 5. Context Manager — async with vs explicit __aenter__/__aexit__

**Module 3: Neo4j Context Providers / Lessons 2–5** (Vector, Fulltext, Hybrid, Graph-Enriched)
**Files:** `vector_context_provider.py`, `fulltext_context_provider.py`, `graph_enriched_provider.py` solutions

**Lesson:** `async with provider:`
**Solution:** `provider.__aenter__()` / `provider.__aexit__(None, None, None)`

**Answer:** Reviewed `/Users/ryanknight/projects/azure/agent-framework` for MAF best practices.

### Research Findings

All official MAF samples consistently use `async with` for both agents and providers. The recommended pattern from the official samples is:

```python
async with (
    search_provider,
    client.as_agent(
        name="SearchAgent",
        instructions="...",
        context_providers=[search_provider],
    ) as agent,
):
    async for chunk in agent.run(user_input, stream=True):
        ...
```

The MAF `Agent` class implements `__aenter__`/`__aexit__` to properly manage context provider lifecycle (entering all providers, closing MCP tools, etc.). Using explicit `__aenter__()`/`__aexit__()` calls bypasses this and risks resource leaks on exceptions.

The MAF framework decision document (0016-python-context-middleware.md) confirms `async with` as the intended pattern.

### Final Decision: Use `async with` in both

Update all solutions to use `async with provider:` (or nested `async with` for multiple resources). This matches MAF's official samples and is standard Python.

**Update:** Companion repo solutions (vector, fulltext, graph-enriched) — replace explicit dunder calls with `async with`.

**Status: DONE** — Updated all 5 solution files to use `async with`: `vector_context_provider.py`, `fulltext_context_provider.py`, `graph_enriched_provider.py` (use `async with provider:`), `memory_context_provider.py`, `memory_tools_agent.py` (use `async with MemoryClient(settings) as memory_client:`). Zero `__aenter__`/`__aexit__` calls remain.

---

## 6. Graph-Enriched Cypher — Director Limit Difference

**Module 3: Neo4j Context Providers / Lesson 5: Graph-Enriched Retrieval**
**Files:** `graph_enriched_provider.py` / `solutions/graph_enriched_provider.py`

**Lesson:** `collect(DISTINCT d.name) AS directors` (no limit on directors, `[0..5]` on actors)
**Solution:** `collect(DISTINCT p.name)[0..3] AS directors` (limit 3 on directors)

**Answer:** Align on the lesson's version.

### Final Decision: Use the lesson's Cypher

Update the solution to match the lesson:
- Remove `[0..3]` limit on directors (typically few per movie)
- Keep `[0..5]` limit on actors (can be many)
- Fix `[r:ACTED_IN]` to `[:ACTED_IN]` since `r` is never used

**Update:** Companion repo solution — fix retrieval query.

**Status: DONE** — Updated `solutions/graph_enriched_provider.py`: removed `[0..3]` limit on directors, changed `[r:ACTED_IN]` to `[:ACTED_IN]`, changed `p` to `d` for director variable name. Cypher now matches lesson.

---

## 7. Memory Tools — Missing Verification Section

**Module 4: Agent Memory / Lesson 4: Combining Context Providers with Memory Tools**
**Files:** `memory_tools_agent.py` / `solutions/memory_tools_agent.py`

**Lesson:** Ends after the conversation loop
**Solution:** Includes a `# tag::verify[]` section that inspects stored memories

**Answer:** Add verification to the lesson.

### Final Decision: Add verification to the lesson

Add a "Verify Stored Memories" section to the lesson showing how to inspect preferences, entities, and message count after the conversation. This matches the solution's `verify` tag and proves the memory system works.

**Update:** Lesson — add verification code section.

---

## 8. Fulltext Provider — top_k Difference

**Module 3: Neo4j Context Providers / Lesson 3: Fulltext Search**
**Files:** `fulltext_context_provider.py` / `solutions/fulltext_context_provider.py`

**Lesson:** `top_k=5`
**Solution:** `top_k=3`

**Answer:** Use `top_k=5` in both.

### Final Decision: Use `top_k=5` in both

Consistency across all provider lessons matters more than the specific value.

**Update:** Companion repo solution — change `top_k=3` to `top_k=5`.

**Status: DONE** — Updated `solutions/fulltext_context_provider.py`: changed `top_k=3` to `top_k=5`.

---

## Remaining Work — Lesson Changes (courses/ repo)

All remaining items require changes to lesson `.adoc` files in:
`/Users/ryanknight/projects/graphacademy/courses/asciidoc/courses/genai-maf-context-providers/`

### R1. Fix #1 — Update first-agent lesson to match companion repo (M1/L3)

**File:** `modules/1-introduction/lessons/3-first-agent/lesson.adoc`

The lesson currently uses a Neo4j driver with Cypher to query movies. The companion repo now uses a hardcoded movie dictionary (no Neo4j). Update the lesson to match:

- Remove `import neo4j` and the `neo4j.GraphDatabase.driver()` setup
- Replace the `get_movie_info` tool with the hardcoded `MOVIES` dictionary version from the companion repo solution
- Remove the `OpenAIResponsesClient(api_key=..., model=...)` explicit params — the solution uses `OpenAIResponsesClient()` which reads from env automatically
- Update agent name from `"movie-knowledge-agent"` to `"movie-info-agent"`
- Update the agent instructions to match the companion repo
- Keep the lesson's teaching narrative about how agents decide when to call tools

**Status: DONE** — R2 and R3 also applied to the hybrid lesson (M3/L4) which had the same `OpenAIEmbedder` and `os.environ` issues.

### R2. Fix #2 — Replace OpenAIEmbedder with OpenAIEmbeddings (M3/L2, M3/L5)

**File 1:** `modules/3-neo4j-context-providers/lessons/2-vector-provider/lesson.adoc`

Replace the "Create an Embedder" section:
```python
# BEFORE (wrong — class does not exist)
from agent_framework_neo4j import OpenAIEmbedder

embedder = OpenAIEmbedder(
    api_key=os.environ["OPENAI_API_KEY"],
    model="text-embedding-ada-002",
)

# AFTER (correct)
from neo4j_graphrag.embeddings.openai import OpenAIEmbeddings

embedder = OpenAIEmbeddings(model="text-embedding-ada-002")
```

Also update the paragraph above it: change "The `agent-framework-neo4j` package includes an `OpenAIEmbedder`" to explain that `neo4j_graphrag` provides `OpenAIEmbeddings`.

**File 2:** `modules/3-neo4j-context-providers/lessons/5-graph-enriched-provider/lesson.adoc`

In the "Create the Graph-Enriched Provider" code block:
- Change `from agent_framework_neo4j import Neo4jContextProvider, OpenAIEmbedder` to `from agent_framework_neo4j import Neo4jContextProvider` and add `from neo4j_graphrag.embeddings.openai import OpenAIEmbeddings`
- Change `OpenAIEmbedder(api_key=..., model=...)` to `OpenAIEmbeddings(model="text-embedding-ada-002")`

### R3. Fix #3 — Replace os.environ with Neo4jSettings (M3/L2, M3/L3, M3/L5)

Update three lesson files to use `Neo4jSettings` instead of raw `os.environ`:

**File 1:** `modules/3-neo4j-context-providers/lessons/2-vector-provider/lesson.adoc`

In "Create the Context Provider" section, replace:
```python
provider = Neo4jContextProvider(
    uri=os.environ["NEO4J_URI"],
    username=os.environ["NEO4J_USERNAME"],
    password=os.environ["NEO4J_PASSWORD"],
    index_name="moviePlots",
    ...
```
With:
```python
from agent_framework_neo4j import Neo4jContextProvider, Neo4jSettings

neo4j_settings = Neo4jSettings()

provider = Neo4jContextProvider(
    uri=neo4j_settings.uri,
    username=neo4j_settings.username,
    password=neo4j_settings.get_password(),
    index_name=neo4j_settings.vector_index_name,
    ...
```

Add a note explaining that `Neo4jSettings` reads `NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD`, and `NEO4J_VECTOR_INDEX_NAME` from environment variables.

**File 2:** `modules/3-neo4j-context-providers/lessons/3-fulltext-provider/lesson.adoc`
Same pattern — replace `os.environ` with `Neo4jSettings`, use `neo4j_settings.fulltext_index_name` instead of hardcoded `"moviePlotsFulltext"`.

**File 3:** `modules/3-neo4j-context-providers/lessons/5-graph-enriched-provider/lesson.adoc`
Same pattern — replace `os.environ` with `Neo4jSettings`, use `neo4j_settings.vector_index_name`.

Also check if `modules/3-neo4j-context-providers/lessons/4-hybrid-provider/lesson.adoc` uses `os.environ` and update if so.

### R4. Fix #4 — Expand simple context provider to name + age (M2/L2)

**File:** `modules/2-context-providers/lessons/2-simple-context-provider/lesson.adoc`

Expand the `UserInfo` model, `before_run()`, and `after_run()` to include age:

- `UserInfo` model: add `age: int | None = None`
- `before_run()`: add age-related instructions (ask for age if unknown, inject known age)
- `after_run()`: extract both name and age from conversation, update state for both
- Multi-turn demo: update example messages to include age (e.g., "My name is Alex and I am 30 years old")
- Add state inspection showing both name and age after conversation

Reference the companion repo solution (`solutions/simple_context_provider.py`) for the exact code.

**Status: DONE** — Updated vector (M3/L2), graph-enriched (M3/L5), and hybrid (M3/L4) lessons: `OpenAIEmbedder` → `OpenAIEmbeddings` from `neo4j_graphrag.embeddings.openai`.

### R3. Status

**Status: DONE** — Updated vector (M3/L2), fulltext (M3/L3), graph-enriched (M3/L5), and hybrid (M3/L4) lessons: replaced all `os.environ` with `Neo4jSettings()`. Fulltext stop-word example also updated.

### R5. Fix #7 — Add memory verification section (M4/L4)

**File:** `modules/4-agent-memory/lessons/4-memory-tools/lesson.adoc`

Add a "Verify Stored Memories" section after the conversation loop showing:
```python
results = await memory.search_memory(
    query="user preferences and interests",
    include_messages=True,
    include_entities=True,
    include_preferences=True,
    limit=5,
)
```

Then print preferences, entities, and message count. Match the companion repo solution's `# tag::verify[]` section.

**Status: DONE** — Added "Verify Stored Memories" section with `search_memory()` call and output for preferences, entities, and message count.

---

## Open Questions

### Q1. Memory tools lesson — `__aexit__` in lesson code (M4/L4)

The memory tools lesson (line 102) has:
```python
await memory_client.__aexit__(None, None, None)
```

The companion repo was fixed (item #5 DONE) but the lesson code still uses the explicit dunder call. Should this be changed to use `async with` as well? This would require restructuring the "Run a Conversation" code block since `memory_client` would need to wrap the entire block.

**Answer:**

### Q2. Simplify `OpenAIResponsesClient()` across lessons

Several lessons (fulltext M3/L3 line 88–91, hybrid M3/L4 lines 65–68) use:
```python
client = OpenAIResponsesClient(
    api_key=os.environ["OPENAI_API_KEY"],
    model=os.environ["OPENAI_RESPONSES_MODEL_ID"],
)
```

The companion repo uses `OpenAIResponsesClient()` with no arguments (reads from env automatically). Should all lessons be updated to match?

**Answer:**: everything should use Neo4jSettings and nothing should use os environment variables. 

### Q3. Simple context provider age behavior (M2/L2)

The lesson's `UserInfo` model already has `age: int | None = None` (line 17), but `before_run()` and `after_run()` only handle name. The companion repo solution asks for name AND age separately and declines questions until both are provided.

Should the lesson match the companion repo exactly (blocking until both name and age are provided), or keep it lighter (extract age when available but don't block on it)?

**Answer:**

---

## Summary of Final Decisions

| # | Mismatch | Lesson | Fix | Where to Update | Status |
|---|----------|--------|-----|-----------------|--------|
| 1 | First agent domain | M1/L3: First Agent | Use hardcoded movie dictionary (no Neo4j) | Lesson + companion repo | **DONE** (repo) |
| 2 | Embedder class | M3/L2: Vector + M3/L5: Graph-Enriched + M3/L4: Hybrid | Use `OpenAIEmbeddings` from `neo4j_graphrag` (`OpenAIEmbedder` does not exist) | Lessons | **DONE** |
| 3 | Neo4j config pattern | M3/L2–L5: All Neo4j provider lessons | Use `Neo4jSettings` everywhere | Lessons | **DONE** |
| 4 | Context provider scope | M2/L2: Simple Context Provider | Use name + age in both | Lesson | TODO (lesson change) |
| 5 | Context manager | M3/L2–L5: All Neo4j provider lessons | Use `async with` (MAF official pattern) | Companion repo solutions | **DONE** |
| 6 | Graph-enriched Cypher | M3/L5: Graph-Enriched Retrieval | Use lesson's Cypher (no director limit, fix `[:ACTED_IN]`) | Companion repo solution | **DONE** |
| 7 | Memory verification | M4/L4: Memory Tools | Add verify section to lesson | Lesson | **DONE** |
| 8 | Fulltext top_k | M3/L3: Fulltext Search | Use `top_k=5` | Companion repo solution | **DONE** |
