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


# Memory Tools

---

## Passive Memory

The memory context provider handles memory **passively** — it injects relevant memories before each turn and stores new ones after.

This covers the common case: the agent automatically has context from prior conversations without any explicit action.

But sometimes the agent needs to take a **deliberate action**:

- User says "remember that I hate horror movies" and expects explicit storage
- Agent needs to search for a specific entity before answering
- Agent wants to look up past reasoning traces for a similar task

**Passive injection alone can't handle targeted operations.**

---

## Agent Memory Also Provides Tools

In addition to the context provider, the agent memory module provides **tools** — functions the agent can call on demand to actively manage its memory.

The context provider runs automatically every turn. Tools run only when the agent **decides** to use them.

This means the agent gets two complementary mechanisms:

- **Context provider**: background memory that just works
- **Memory tools**: targeted operations the agent controls

---

## What Are Tools?

In the Microsoft Agent Framework, a **tool** is a callable function exposed to the LLM. When the agent decides it needs to perform an action — search a database, save a preference, look up an entity — it calls a tool.

Tools are defined as `FunctionTool` instances and passed to the agent's `tools` list. The LLM sees the tool's name, description, and parameters, and can invoke it during a conversation turn.

Memory tools work the same way as any other agent tool — the only difference is they operate on the agent's memory store.

---

## The Six Memory Tools

`create_memory_tools()` generates six callable `FunctionTool` instances:

| Tool | Purpose |
|------|---------|
| **`search_memory`** | Search across all memory types for a query |
| **`remember_preference`** | Save a user preference (category + preference) |
| **`recall_preferences`** | Retrieve saved preferences matching a topic |
| **`search_knowledge`** | Search the entity graph for people, movies, genres |
| **`remember_fact`** | Store a factual statement as a subject-predicate-object triple |
| **`find_similar_tasks`** | Retrieve past reasoning traces for similar tasks |

---

## Creating Memory Tools

Call `create_memory_tools(memory)` to generate the six tool instances, then pass them to the agent's `tools` list alongside the context provider.

- The agent's **instructions** should tell it when to use the tools (e.g., "When a user expresses a preference, save it with `remember_preference`")
- The tools operate on the **same memory store** as the context provider
- The agent can now both **passively recall** and **actively manage** its memory

---

## Context Provider vs Memory Tools

| Aspect | Context Provider | Memory Tools |
|--------|-----------------|--------------|
| **Invocation** | Automatic every turn | Agent decides when |
| **Direction** | Recall and store | Search, save, recall on demand |
| **User visibility** | Transparent | Visible in agent reasoning |
| **Control** | Framework-managed | Agent-managed |

**Context provider**: "I automatically remember relevant things."
**Memory tools**: "I can explicitly search, save, and recall."

---

## The Combined Pattern

The most effective setup uses **both mechanisms** together.

**Turn 1:** *"I love Christopher Nolan movies and anything about space."*
The context provider saves the message and extracts entities in the background. The agent **also** explicitly calls `remember_preference` to store "Christopher Nolan" under directors and "space" under themes.

**Turn 2:** *"What are my movie preferences?"*
The context provider injects relevant past messages automatically. The agent **also** calls `recall_preferences` to retrieve the explicit preferences it saved.

**Turn 3:** *"Based on what you know about me, what should I watch next?"*
The context provider injects memories as background context. The agent calls `search_knowledge` and `recall_preferences` to gather targeted information, then generates a grounded recommendation.

---

## Two Levels of Memory Operation

The agent now operates on two levels simultaneously:

**Background level (Context Provider):**
- `before_run()` injects relevant memories as context
- `after_run()` stores messages and extracts entities
- Runs every turn, no agent decision needed

**Active level (Memory Tools):**
- Agent explicitly saves preferences when user states them
- Agent searches entity graph for targeted lookups
- Agent recalls preferences before making recommendations

---

## Summary

- The memory context provider handles **passive** memory automatically
- In addition, agent memory provides **tools** for targeted operations
- Tools are callable functions the agent invokes on demand
- Six tools: `search_memory`, `remember_preference`, `recall_preferences`, `search_knowledge`, `remember_fact`, `find_similar_tasks`
- The **combined pattern** uses both: passive context for the common case, active tools for specific operations
- Both mechanisms persist data in the same Neo4j graph

**Next:** Reasoning memory for learning from past executions.
