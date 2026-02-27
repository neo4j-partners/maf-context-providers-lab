# Plan: Add Companion Repo Includes to MAF Course + Sync Script Support

## Context

The `genai-maf-context-providers` course currently has all code examples **inline** in lesson files. The companion exercise repo at `https://github.com/neo4j-partners/genai-maf-context-providers` already exists with:
- Exercise skeleton files (with TODOs) in `genai-maf-context-providers/`
- Solution files (with AsciiDoc `# tag::...[]` markers) in `genai-maf-context-providers/solutions/`

The `genai-integration-langchain` course shows the best practice: declare `:repository:` in `course.adoc`, then use `include::{repository-raw}/{branch}/...` directives with tag filters in lessons. This works in the `courses/` build system automatically.

The `maf-context-providers-lab/` Antora site needs its `sync_course.py` updated to resolve these remote includes when transforming lessons.

---

## Part 1: Update Course Lessons (in courses/ repo)

### 1a. Add `:repository:` to `course.adoc`

**File:** `asciidoc/courses/genai-maf-context-providers/course.adoc`

Add after the `:usecase:` line:
```
:repository: neo4j-partners/genai-maf-context-providers
```

The build system auto-generates `{repository-raw}`, `{repository-blob}`, `{repository-link}`.

### 1b. Update 7 hands-on lessons to use include directives

Each lesson gets `:branch: main` in its header, then replaces inline code blocks with `include::` directives following the langchain pattern:

1. Show exercise skeleton: `include::{repository-raw}/{branch}/genai-maf-context-providers/FILENAME.py[tag=**]`
2. Walk through solution steps using specific tags
3. End with collapsible full solution: `[%collapsible]` block with `tags="**"`

| Lesson | Exercise File | Solution File | Tags |
|--------|--------------|---------------|------|
| `1-introduction/3-first-agent` | `simple_agent.py` | `solutions/simple_agent.py` | `companies`, `tool`, `agent`, `run` |
| `2-context-providers/2-simple-context-provider` | `simple_context_provider.py` | `solutions/simple_context_provider.py` | `model`, `provider`, `agent`, `run` |
| `3-neo4j-context-providers/2-vector-provider` | `vector_context_provider.py` | `solutions/vector_context_provider.py` | `settings`, `embedder`, `provider`, `agent`, `run` |
| `3-neo4j-context-providers/3-fulltext-provider` | `fulltext_context_provider.py` | `solutions/fulltext_context_provider.py` | `settings`, `provider`, `agent`, `run` |
| `3-neo4j-context-providers/5-graph-enriched-provider` | `graph_enriched_provider.py` | `solutions/graph_enriched_provider.py` | `retrieval_query`, `provider`, `agent`, `run` |
| `4-agent-memory/3-memory-context-provider` | `memory_context_provider.py` | `solutions/memory_context_provider.py` | `settings`, `memory`, `agent`, `run`, `search` |
| `4-agent-memory/4-memory-tools` | `memory_tools_agent.py` | `solutions/memory_tools_agent.py` | `settings`, `tools`, `agent`, `run`, `verify` |

**9 conceptual lessons stay unchanged** (no matching exercise files): `1-what-is-maf`, `2-setup`, `1-what-are-context-providers`, `1-neo4j-context-providers-overview`, `4-hybrid-provider`, `1-memory-types`, `2-entity-extraction`, `5-reasoning-memory`, `6-gds-integration`.

### 1c. Update companion repo's `simple_agent.py` to match lesson

The lesson uses a Neo4j movie-query tool example, but the companion repo's `simple_agent.py` uses hardcoded company data. Update the companion repo (both exercise and solution files) to use the movie-query example from the lesson, then add appropriate `# tag::...[]` markers to the solution.

---

## Part 2: Update maf-context-providers-lab sync script

### 2a. Add to `.env`

```
REPOSITORY_LOCAL_PATH=/Users/ryanknight/projects/graphacademy/genai-maf-context-providers
```

### 2b. Update `sync_course.py`

**File:** `/Users/ryanknight/projects/graphacademy/maf-context-providers-lab/sync_course.py`

Changes:

1. **Add `"repository"` and `"branch"` to `STRIP_ATTRIBUTES`** (line 20)

2. **Add fields to `Course` dataclass** (line 59):
   ```python
   repository_raw: str | None = None
   branch: str = "main"
   ```

3. **Extract repository in `discover_course()`** (after line 285):
   ```python
   repository = extract_attribute(course_content, "repository")
   repository_raw = f"https://raw.githubusercontent.com/{repository}" if repository else None
   branch = extract_attribute(course_content, "branch") or "main"
   ```
   Pass to `Course()` constructor.

4. **Add tag-aware include resolution function** `resolve_repository_includes(content, course)`:
   - Match `include::{repository-raw}/{branch}/path[attrs]` patterns
   - Resolve file from `REPOSITORY_LOCAL_PATH` env var (local-first), fallback to HTTP fetch from GitHub raw URL
   - Parse tag specifications: `tag=name`, `tag=**`, `tags="**;!excluded"`
   - Extract matching lines between `# tag::name[]` / `# end::name[]` markers
   - Cache fetched files in a dict to avoid re-reads

5. **Add to `transform_lesson()` pipeline** (line 231):
   - Update signature to accept `course` parameter
   - Call `resolve_repository_includes(content, course)` before `resolve_includes()`
   - Update the call site in `main()` (line 496) to pass `course`

6. **Also resolve per-lesson `:branch:` attribute**: Per-lesson `:branch:` should override the course-level default. Extract it from lesson content before resolving includes.

---

## How the Best Practice Pattern Works (Reference)

### In the courses/ build system

The `genai-integration-langchain` course demonstrates the pattern:

1. **`course.adoc`** declares `:repository: neo4j-graphacademy/genai-integration-langchain`
2. **Build system** (`src/services/build/build.utils.ts`) auto-generates:
   - `{repository-raw}` → `https://raw.githubusercontent.com/neo4j-graphacademy/genai-integration-langchain`
   - `{repository-blob}` → `https://github.com/neo4j-graphacademy/genai-integration-langchain/blob`
   - `{repository-link}` → `https://github.com/neo4j-graphacademy/genai-integration-langchain`
3. **Lessons** declare `:branch: main` and use includes like:

```asciidoc
Open the `genai-integration-langchain/neo4j_query.py` file:

.neo4j_query.py
[source,python]
----
include::{repository-raw}/{branch}/genai-integration-langchain/neo4j_query.py[tag=**]
----

Update the code to connect to Neo4j:

[source,python]
----
include::{repository-raw}/{branch}/genai-integration-langchain/solutions/neo4j_query.py[tag=import_neo4j]

include::{repository-raw}/{branch}/genai-integration-langchain/solutions/neo4j_query.py[tag=neo4jgraph]
----

[%collapsible]
.Click to see the complete code
====
[source,python]
----
include::{repository-raw}/{branch}/genai-integration-langchain/solutions/neo4j_query.py[tags="**;!examples"]
----
====
```

### Tag syntax in companion repo files

Solution files use Python comment markers:
```python
# tag::import_neo4j[]
from langchain_neo4j import Neo4jGraph
# end::import_neo4j[]

# tag::neo4jgraph[]
graph = Neo4jGraph(
    url=os.environ["NEO4J_URI"],
    username=os.environ["NEO4J_USERNAME"],
    password=os.environ["NEO4J_PASSWORD"],
)
# end::neo4jgraph[]
```

### Tag filter syntax

- `[tag=**]` — include all content
- `[tag=name]` — include only lines between `# tag::name[]` and `# end::name[]`
- `[tags="**;!excluded"]` — include all except the excluded tag

---

## Verification

### courses/ repo
```bash
cd /Users/ryanknight/projects/graphacademy/courses
SKIP_LINK_CHECKS=true SKIP_CYPHER_CHECKS=true COURSES=genai-maf-context-providers npm run test:qa
```

### maf-context-providers-lab/
```bash
cd /Users/ryanknight/projects/graphacademy/maf-context-providers-lab
uv run sync_course.py
cd site && npm run build && npm run serve
# Browse http://localhost:8080 and verify code blocks render in lesson pages
```
