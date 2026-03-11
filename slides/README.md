# Workshop Slides

This folder contains presentation-ready slides for the **Self-Grounding Agents with MAF and Neo4j** course. All slides are formatted for [Marp](https://marp.app/), a markdown presentation tool.

## Quick Start

Requires Node.js 22 LTS (`brew install node@22`) and a one-time `npm install` in this directory.

```bash
cd slides
npm install
/opt/homebrew/opt/node@22/bin/node ./node_modules/.bin/marp section-1-introduction-to-maf --server
```

Opens at http://localhost:8080/. Replace `section-1-introduction-to-maf` with any slide deck directory name.

## Available Presentations

Slides are organized into 4 sections matching the course structure.

### Section 1: Introduction to Microsoft Agent Framework

| Slide | File | Topics |
|---|---|---|
| 01 | `section-1-introduction-to-maf/01-what-is-maf-slides.md` | MAF history (Semantic Kernel + AutoGen), five building blocks, agent lifecycle, multi-language/multi-LLM support |
| 02 | `section-1-introduction-to-maf/02-setup-slides.md` | Neo4j Sandbox creation, GitHub Codespaces launch, environment verification |
| 03 | `section-1-introduction-to-maf/03-first-agent-slides.md` | OpenAI client setup, defining tools with annotations, creating and running an agent |

### Section 2: Context Providers

| Slide | File | Topics |
|---|---|---|
| 01 | `section-2-context-providers/01-what-are-context-providers-slides.md` | Tools-only limitations, context provider lifecycle, before_run/after_run, injection methods |
| 02 | `section-2-context-providers/02-simple-context-provider-slides.md` | Pydantic data models, UserInfoMemory walkthrough, structured LLM extraction |

### Section 3: Neo4j Context Providers

| Slide | File | Topics |
|---|---|---|
| 01 | `section-3-neo4j-context-providers/01-neo4j-context-providers-overview-slides.md` | Neo4j Context Provider architecture, retriever classes, before_run workflow, configuration |
| 02 | `section-3-neo4j-context-providers/02-vector-provider-slides.md` | Vector search, embeddings, cosine similarity, embedder configuration |
| 03 | `section-3-neo4j-context-providers/03-graph-enriched-provider-slides.md` | retrieval_query parameter, Cypher traversal, graph-enriched context |
| 04 | `section-3-neo4j-context-providers/04-fulltext-provider-slides.md` | Fulltext search, BM25 ranking, keyword matching, no embedder required |
| 05 | `section-3-neo4j-context-providers/05-hybrid-provider-slides.md` | Hybrid search, combining vector + fulltext, combined ranking |

### Section 4: Agent Memory

| Slide | File | Topics |
|---|---|---|
| 01 | `section-4-agent-memory/01-memory-types-slides.md` | Three memory categories (said/learned/tried), short-term, long-term, reasoning |
| 02 | `section-4-agent-memory/02-entity-extraction-slides.md` | Three-stage pipeline (spaCy, GLiNER, LLM), POLE+O schema, MemorySettings |
| 03 | `section-4-agent-memory/03-memory-context-provider-slides.md` | Neo4jMicrosoftMemory setup, before/after turn lifecycle, multi-turn conversations |
| 04 | `section-4-agent-memory/04-memory-tools-slides.md` | Passive vs active memory, six memory tools, combined pattern |
| 05 | `section-4-agent-memory/05-reasoning-memory-slides.md` | Reasoning traces, task/steps/outcome, vector search for similar tasks |
| 06 | `section-4-agent-memory/06-gds-integration-slides.md` | GDS algorithms (PageRank, Shortest Path, Node Similarity), GDS tools |

## How to Use These Slides

### Option 1: Marp CLI (Recommended)

Requires Node.js 22 LTS (`brew install node@22`) and a one-time `npm install` in this directory.

**Present slides:**
```bash
cd slides
/opt/homebrew/opt/node@22/bin/node ./node_modules/.bin/marp section-1-introduction-to-maf --server
```

**Export to PDF:**
```bash
cd slides
/opt/homebrew/opt/node@22/bin/node ./node_modules/.bin/marp section-1-introduction-to-maf --pdf --allow-local-files
```

**Export all slides in a section:**
```bash
cd slides
/opt/homebrew/opt/node@22/bin/node ./node_modules/.bin/marp section-3-neo4j-context-providers --pdf --allow-local-files
```

### Option 2: VS Code with Marp Extension

1. Install the [Marp for VS Code](https://marketplace.visualstudio.com/items?itemName=marp-team.marp-vscode) extension
2. Open any slide file
3. Click "Open Preview" or press `Cmd+K V`

### Option 3: Marp Web

1. Visit [Marp Web](https://web.marp.app/)
2. Copy and paste slide content
3. Present directly in browser

## Slide Format

All slides use Marp markdown format:

```markdown
---
marp: true
theme: default
paginate: true
---

# Slide Title

Content here

---

# Next Slide

More content
```

## Presentation Order

### Full Workshop (~3 hours):

**Part 1: MAF Fundamentals (30 min)**
1. Section 1, Slide 01: What is MAF (10 min)
2. Section 1, Slide 02: Setup (10 min)
3. Section 1, Slide 03: First Agent (10 min)

**Part 2: Context Providers (20 min)**
4. Section 2, Slide 01: What Are Context Providers (10 min)
5. Section 2, Slide 02: Simple Context Provider (10 min)

**Part 3: Neo4j Context Providers (50 min)**
6. Section 3, Slide 01: Overview (10 min)
7. Section 3, Slide 02: Vector Provider (10 min)
8. Section 3, Slide 03: Graph-Enriched Provider (10 min)
9. Section 3, Slide 04: Fulltext Provider (10 min)
10. Section 3, Slide 05: Hybrid Provider (10 min)

**Part 4: Agent Memory (60 min)**
11. Section 4, Slide 01: Memory Types (10 min)
12. Section 4, Slide 02: Entity Extraction (10 min)
13. Section 4, Slide 03: Memory Context Provider (10 min)
14. Section 4, Slide 04: Memory Tools (10 min)
15. Section 4, Slide 05: Reasoning Memory (10 min)
16. Section 4, Slide 06: GDS Integration (10 min)

### Short Workshop (~1.5 hours):

**Essential Slides:**
1. Section 1, Slide 01: What is MAF (10 min)
2. Section 1, Slide 03: First Agent (10 min)
3. Section 2, Slide 01: What Are Context Providers (10 min)
4. Section 3, Slide 01: Neo4j Context Providers Overview (10 min)
5. Section 3, Slide 02: Vector Provider (10 min)
6. Section 3, Slide 03: Graph-Enriched Provider (10 min)
7. Section 4, Slide 01: Memory Types (10 min)
8. Section 4, Slide 03: Memory Context Provider (10 min)
9. Section 4, Slide 04: Memory Tools (10 min)

## Images

All slides reference images in the `../images/` directory. Ensure the images folder is at the same level as the slides folder.

## Troubleshooting

**`require is not defined in ES module scope` error?**
- Marp CLI is incompatible with Node.js 25+. Install Node 22 LTS: `brew install node@22`

**Images not showing?**
- Ensure `images/` folder is at correct location (`../images` from slides/)
- Use `--allow-local-files` flag with Marp CLI

**PDF export fails?**
- Install Chromium: `npx @marp-team/marp-cli --version`
- Use `--allow-local-files` flag

## Slide Statistics

**Total Presentations:** 16
**Format:** Marp Markdown
**Sections:** 4

| Section | Presentations |
|---|---|
| Section 1: Introduction to MAF | 3 |
| Section 2: Context Providers | 2 |
| Section 3: Neo4j Context Providers | 5 |
| Section 4: Agent Memory | 6 |
