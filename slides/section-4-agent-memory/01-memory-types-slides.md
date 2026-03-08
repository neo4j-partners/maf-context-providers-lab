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

Context providers from Modules 2 and 3 inject knowledge from a **static** knowledge graph -- movie plots, genres, actors.

But the agent itself has no memory:
- It doesn't remember what you discussed last session
- It can't learn your preferences over time
- It forgets which approaches worked and which failed
- Every conversation starts from zero

**Agents need persistent, searchable memory.**

---

## A Conversation Without Memory

A user tells the agent they prefer Christopher Nolan films. Two turns later, they ask for a recommendation.

Without memory:
- The conversation history is gone
- The preference was never stored
- The agent suggests a random comedy

**The agent has no idea what the user said.**

---

## What Memory Needs to Capture

Three categories of information accumulate during agent conversations:

1. **What was said** -- the conversation itself. Messages, responses, follow-ups. This history needs to persist across turns and sessions.

2. **What was learned** -- facts and preferences extracted from conversation. "The user prefers sci-fi" is structured knowledge derived from messages.

3. **What was tried** -- the reasoning and tool calls the agent used. If an approach worked, the agent should reuse it. If it failed, avoid it.

---

## The neo4j-agent-memory Package

The `neo4j-agent-memory` library is a **graph-native memory system** for AI agents.

- Stores conversations, builds knowledge graphs, learns from reasoning
- All backed by Neo4j
- Framework integrations for **LangChain**, **Pydantic AI**, **OpenAI Agents**, and **MAF**
- The MAF integration wraps memory into context providers and callable tools

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

Extraction happens **automatically**. Over time, the agent builds a knowledge graph about each user.

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

```
(Conversation)--[:HAS_MESSAGE]-->(Message)
                                    |
                    +---------------+---------------+
                    v               v               v
              [:MENTIONS]    [:EXTRACTED_FROM]  [:INITIATED_BY]
                    v               v               v
               (Entity)         (Entity)    (ReasoningTrace)
                    |                           |
              [:RELATED_TO]              [:HAS_STEP]
                    v                           v
               (Entity)              (ReasoningStep)
                                            |
                                      [:USES_TOOL]
                                            v
                                        (ToolCall)
```

---

## Connected Memory

Because everything is in the same graph, memories connect to each other:

- An entity extracted from a conversation **links back** to the message it came from
- Messages link to the **session** they occurred in
- Entities link to **other entities** they relate to
- Reasoning traces connect to the **steps and tool calls** that compose them

This is more than storage -- it's a **connected knowledge structure** the agent can traverse.

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

Both use context providers -- but with different data and different goals.

---

## Summary

- **Agents are stateless by default** -- they forget everything between sessions
- **`neo4j-agent-memory`** provides graph-native persistent memory
- **Short-term memory**: conversation history with semantic search
- **Long-term memory**: entities, facts (SPO triples), and preferences via POLE+O
- **Reasoning memory**: traces of past tool usage and outcomes
- **All memory is stored in Neo4j** as a connected graph
- **Memory is dynamic** -- it grows with every conversation

**Next:** How the entity extraction pipeline works.
