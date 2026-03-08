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


# Combining Context Providers with Memory Tools

---

## Passive Memory Is Not Enough

The memory context provider handles memory **passively** -- it injects relevant memories before each turn and stores new ones after.

But sometimes the agent needs to take a **deliberate action**:

- User says "remember that I hate horror movies" -- expects explicit storage
- Agent needs to search for a specific entity before answering
- Agent wants to look up past reasoning traces for a similar task

**Passive injection alone can't handle targeted operations.**

---

## The Combined Pattern

The most effective setup uses **both mechanisms** together:

| Mechanism | Role | When It Runs |
|-----------|------|-------------|
| **Context Provider** | Background memory | Automatically every turn |
| **Memory Tools** | Targeted operations | When the agent decides |

- Passive context covers the **common case**
- Active tools handle the **specific case**

---

## The Six Memory Tools

`create_memory_tools()` generates callable `FunctionTool` instances:

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

```python
# Create callable memory tools
tools = create_memory_tools(memory)

agent = client.as_agent(
    name="movie-assistant",
    instructions=(
        "You are a movie recommendation assistant with persistent memory.\n\n"
        "When a user expresses a preference, save it with the "
        "remember_preference tool. When making recommendations, "
        "use recall_preferences to check what the user likes "
        "before suggesting something."
    ),
    tools=tools,
    context_providers=[memory.context_provider],
)
```

The agent can now both **passively recall** and **actively manage** its memory.

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

## How the Combined Pattern Works

```
Turn 1: "I love Christopher Nolan movies and anything about space."
    --> Context provider after_run(): saves message, extracts entities
    --> Agent calls: remember_preference("directors", "Christopher Nolan")
    --> Agent calls: remember_preference("themes", "space")

Turn 2: "What are my movie preferences?"
    --> Context provider before_run(): injects relevant past messages
    --> Agent calls: recall_preferences("movies")
    --> Reports both passive context and explicit preferences

Turn 3: "Based on what you know about me, what should I watch next?"
    --> Context provider before_run(): injects memories as background
    --> Agent calls: search_knowledge("Christopher Nolan movies")
    --> Agent calls: recall_preferences("themes")
    --> Generates grounded recommendation
```

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

## Verifying Stored Memories

After the conversation, inspect what the memory system has stored:

```python
results = await memory.search_memory(
    query="user preferences and interests",
    include_messages=True,
    include_entities=True,
    include_preferences=True,
    limit=5,
)

print("Preferences:", results.get("preferences", []))
print("Entities:", results.get("entities", []))
print(f"Messages stored: {len(results.get('messages', []))}")
```

Confirms that both the context provider and tools have persisted data in Neo4j.

---

## Experiment Ideas

Test the interaction between passive and active memory:

- Tell the agent you **dislike** a genre, then ask for recommendations. Does it avoid that genre?
- Ask the agent to **remember a fact** ("The Matrix was released in 1999") and verify it later
- **End the session**, create a new one with the same `session_id`, and check whether long-term memories persist
- Ask the agent a question it **struggled with before** -- does it approach it differently with reasoning traces?

---

## Summary

- **Memory tools** give the agent explicit control over search, save, and recall
- **Context provider** continues to handle background memory injection automatically
- The **combined pattern** covers both passive context (always available) and active operations (agent-directed)
- Six tools: `search_memory`, `remember_preference`, `recall_preferences`, `search_knowledge`, `remember_fact`, `find_similar_tasks`
- Both mechanisms persist data in the same Neo4j graph

**Next:** Reasoning memory for learning from past executions.
