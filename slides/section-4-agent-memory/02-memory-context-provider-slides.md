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


# Memory as a Context Provider

---

## Memory Follows the Same Pattern

The memory context provider works like `Neo4jContextProvider` from Module 3, but for **memories the agent has accumulated**:

- **Before each turn**: retrieves relevant past messages, entities, and preferences
- **After each turn**: stores new messages and extracts entities
- **Interface**: `Neo4jMicrosoftMemory` wraps the memory client into a context provider

---

## Configure Memory Settings

Setting up memory requires two steps:

1. **Create `MemorySettings`**: provide Neo4j connection details (URI, username, password), plus any extraction or resolution configuration
2. **Create a `MemoryClient`**: use it as an async context manager (`async with`) which automatically connects on entry and closes the connection on exit

The `MemoryClient` is the entry point to all three memory types (short-term, long-term, reasoning) and is passed to the higher-level components you'll use next.

---

## Create the Unified Memory

- `Neo4jMicrosoftMemory.from_memory_client()` wraps the client into a unified interface

- **`session_id`**: scopes the conversation; messages and entities are grouped by session
- **`include_short_term`** / **`include_long_term`** / **`include_reasoning`**: toggle which memory types are injected before each turn
- **`extract_entities`**: whether to automatically extract entities after each turn

---

## Configuration Parameters

| Parameter | Purpose |
|-----------|---------|
| **`session_id`** | Scopes the conversation. Messages and entities are grouped by session. |
| **`include_short_term`** | Injects recent and semantically relevant past messages before each turn |
| **`include_long_term`** | Injects extracted entities and preferences before each turn |
| **`include_reasoning`** | Injects similar past reasoning traces before each turn |
| **`extract_entities`** | Pulls entities out of messages after each turn |

---

## Attach the Context Provider

- **Configuration**: same as any other context provider
- **Transparent**: the agent doesn't need to know it's using memory
- **Composable**: combine with other context providers (e.g., knowledge graph + memory together)
- **Instructions**: tell the agent it has memory so the LLM references past context in responses

---

## The Memory Lifecycle

The provider follows the same `before_run()` / `after_run()` lifecycle from Module 3:

**`before_run()` retrieves:**
1. Recent conversation history (short-term)
2. Semantically relevant past messages (short-term)
3. Matching user preferences (long-term)
4. Related entities and facts (long-term)
5. Similar past reasoning traces (reasoning)

**`after_run()` stores:**
1. New messages with vector embeddings (user input + agent response)
2. Automatically extracted entities from the conversation

---

## No Tool Calls Required

- The context provider runs **automatically on every turn** — the agent never decides to look something up or save a preference

1. User query arrives
2. `before_run()` searches memory and injects relevant context
3. The LLM generates a response with that memory context available
4. `after_run()` stores the new messages and extracts entities

- This is **passive memory** — always working in the background, no agent decision needed

---

## Multi-Turn Conversation Example

- **Turn 1:** *"I really enjoy sci-fi movies, especially ones about time travel."*
  — `after_run()` saves the message and extracts "sci-fi" and "time travel" as entities
- **Turn 2:** *"What did I say my favorite genre was?"*
  — `before_run()` retrieves the previous message via semantic search; agent answers accurately
- **Turn 3:** *"Can you recommend something I might like?"*
  — Agent has conversation history and extracted preferences; recommends based on what the user said

---

## Inspecting Stored Memories

- Call `search_memory()` with a query string to verify what the provider stored

The search returns results across all memory types you request:
- **Messages**: past conversation turns that match semantically
- **Entities**: extracted people, objects, locations, etc.
- **Preferences**: user preferences the system captured

- Use this to confirm `after_run()` is extracting and storing data correctly in Neo4j

---

## Summary

- **`Neo4jMicrosoftMemory`** provides a context provider for automatic memory
- **`before_run()`** retrieves relevant memories from all three memory types
- **`after_run()`** stores new messages and extracts entities
- The agent gets **persistent memory across turns and sessions** without calling any tools
- Configuration controls which memory types are included and whether entities are extracted
- Uses the same `before_run()`/`after_run()` lifecycle as Module 3 context providers

**Next:** Adding memory tools for explicit agent control.
