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


# Memory Types

---

## The Problem: Agents Forget

Context providers from Modules 2 and 3 inject knowledge from a **static** knowledge graph (movie plots, genres, actors).

But the agent itself has no memory:
- It doesn't remember what you discussed last session
- It can't learn your preferences over time
- It forgets which approaches worked and which failed
- Every conversation starts from zero

**Agents need persistent, searchable memory.**

---

## What Memory Needs to Capture

Three categories of information accumulate during agent conversations:

1. **What was said**: messages, responses, and follow-ups that persist across turns and sessions
2. **What was learned**: facts and preferences extracted from conversation into structured knowledge
3. **What was tried**: reasoning steps and tool calls the agent used, including what worked and what failed

---

## The neo4j-agent-memory Package

The `neo4j-agent-memory` library is a **graph-native memory system** for AI agents.

- **Storage**: conversations, knowledge graphs, and reasoning traces, all backed by Neo4j
- **Three memory types**: short-term (conversation history), long-term (extracted knowledge), and reasoning (agent execution traces)
- **Framework integrations**: LangChain, Pydantic AI, OpenAI Agents, and MAF
- **MAF integration**: wraps memory into context providers and callable tools

---

## Short-Term Memory

Stores **conversation history** as linked Message nodes with embeddings.

**What it stores:**
- Messages with role (user/assistant/system) and content
- Vector embeddings for each message
- Conversation grouping by session ID

**What it enables:**
- Semantic search over past messages (not just replay in order)
- Find the most relevant past exchanges for the current question
- Maintain conversation context across turns and sessions

---

## Long-Term Memory

Stores **structured knowledge** extracted from conversations using the POLE+O data model.

| Type | What It Stores | Example |
|------|---------------|---------|
| **Entities** | People, organizations, locations, events, objects | "Christopher Nolan", "Inception" |
| **Facts** | Subject-Predicate-Object triples | "Nolan -> directed -> Inception" |
| **Preferences** | User-specific information with category | "Prefers sci-fi over comedy" |

- Extraction happens **automatically** — the agent builds a knowledge graph about each user over time

---

## The ReAct Pattern: Reason + Act

Agents don't execute a single action — they loop through a cycle known as ReAct (Reason + Act):

- **Reason**: observe the current state (user input, tool results, conversation history) and decide what to do next
- **Act**: execute an action — call a tool, query an API, or generate a response
- **Observe**: examine the result and feed it back into the next reasoning step

The agent repeats this loop until the task is complete. Each pass produces a trace — what the agent reasoned, what it did, and what came back.

<!--
The next slide — reasoning memory — captures exactly these traces. Each time an agent loops through reason, act, and observe, it records which tools it called, what parameters it used, what came back, and whether the task succeeded or failed. Storing these traces means the agent can look up what it tried last time it encountered a similar task and learn from past experience rather than starting from scratch.
-->

---

## Reasoning Memory

Stores **traces of past agent behavior** for learning.

**What it captures:**
- Task description and outcome (success/failure)
- Each reasoning step the agent took
- Tool calls with parameters, results, and duration
- Timing information for performance tracking

**What it enables:**
- Retrieve past traces when encountering a similar task
- Learn from what worked and what failed
- Track tool reliability and performance over time

<!--
This maps directly to the agent lifecycle, often called the ReAct (Reason + Act) pattern:

1. **Reason** — the agent observes the current state (user input, environment, tool results) and decides what to do next
2. **Act** — the agent executes an action (calls a tool, makes an API request, generates a response)
3. **Observe** — the agent sees the result of that action and feeds it back into the next reasoning step

The agent loops through Reason → Act → Observe until it decides the task is complete.

Reasoning memory captures this entire loop: the task that triggered it, each reasoning step the agent took, which tools it called (with parameters and results), and whether the overall task succeeded or failed. It's essentially a recording of the ReAct cycle so the agent can replay and learn from past attempts when it encounters a similar task later.
-->

---

## Three Memory Types Compared

| Memory Type | What It Stores | How It Helps |
|-------------|---------------|--------------|
| **Short-Term** | Messages and conversation chains | Maintains conversation context |
| **Long-Term** | Entities, facts, preferences | Personalizes responses over time |
| **Reasoning** | Past task traces and tool usage | Learns from previous experience |

**Short-term** is what was said. **Long-term** is what was learned. **Reasoning** is what was tried.

---

## How Neo4j Stores It

All three memory types live in the same Neo4j database as graph structures:

- **Conversations → Messages**: linked message nodes store short-term memory
- **Messages → Entities**: extracted or mentioned entities form long-term memory
- **Entities → Entities**: related entities connect to each other, forming a knowledge graph
- **ReasoningTrace → Steps → ToolCalls**: reasoning memory captures execution paths
- **All nodes → Session**: everything connects back to the session where it occurred

---

## Connected Memory

Because everything is in the same graph, memories connect to each other:

- **Entities → Messages**: extracted entities link back to the message they came from
- **Messages → Sessions**: messages link to the session they occurred in
- **Entities → Entities**: entities link to other entities they relate to
- **Traces → Steps**: reasoning traces connect to the steps and tool calls that compose them

- This is more than storage — it's a **connected knowledge structure** the agent can traverse

---

## The MAF Integration Components

The MAF integration provides four components:

| Component | Purpose |
|-----------|---------|
| **`MemoryClient`** | Connects to Neo4j, exposes all three memory types |
| **`Neo4jMicrosoftMemory`** | Wraps the client into a unified interface for MAF agents |
| **Context Provider** | Implements `before_run()`/`after_run()` for automatic memory |
| **`create_memory_tools()`** | Generates callable tools for explicit memory operations |

---

## Memory vs Static Knowledge

| Aspect | Modules 2-3: Knowledge Graph | Module 4: Agent Memory |
|--------|-------------------------------|----------------------|
| **Data source** | Pre-built knowledge graph | Dynamic, grows from conversations |
| **Content** | Movie data, document chunks | Messages, preferences, facts, traces |
| **Changes** | Static (updated by data pipeline) | Evolves with every interaction |
| **Purpose** | Ground answers in domain knowledge | Remember and personalize over time |

Both use context providers, but with different data and different goals.

---

## Summary

- **Agents are stateless by default**: they forget everything between sessions
- **`neo4j-agent-memory`** provides graph-native persistent memory
- **Short-term memory**: conversation history with semantic search
- **Long-term memory**: entities, facts (SPO triples), and preferences via POLE+O
- **Reasoning memory**: traces of past tool usage and outcomes
- **All memory is stored in Neo4j** as a connected graph
- **Memory is dynamic**: it grows with every conversation

**Next:** How the entity extraction pipeline works.
