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

The `Neo4jContextProvider` from Module 3 injected knowledge graph data before every agent turn.

The memory context provider does the same thing, but for **memories the agent has accumulated**:

- **Before each turn:** retrieves relevant past messages, extracted entities, and user preferences
- **After each turn:** stores new messages and extracts entities

The interface is `Neo4jMicrosoftMemory`, which wraps the memory client into a context provider.

---

## Configure Memory Settings

Connect to Neo4j and create a memory client:

```python
settings = MemorySettings(
    neo4j={
        "uri": os.environ["NEO4J_URI"],
        "username": os.environ["NEO4J_USERNAME"],
        "password": SecretStr(os.environ["NEO4J_PASSWORD"]),
    },
)

async with MemoryClient(settings) as memory_client:
    # memory_client is now connected to Neo4j
    ...
```

The `async with` block automatically connects on entry and closes the connection on exit.

---

## Create the Unified Memory

`Neo4jMicrosoftMemory.from_memory_client()` returns an object that provides both a context provider and a chat message store:

```python
memory = Neo4jMicrosoftMemory.from_memory_client(
    memory_client=memory_client,
    session_id=session_id,
    include_short_term=True,
    include_long_term=True,
    include_reasoning=True,
    extract_entities=True,
)
```

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

Pass `memory.context_provider` to the agent the same way you passed `Neo4jContextProvider` in Module 3:

```python
agent = client.as_agent(
    name="movie-memory-agent",
    instructions=(
        "You are a movie recommendation assistant with persistent "
        "memory. You remember what users have told you about their "
        "preferences, which movies you have discussed, and what "
        "you recommended in past sessions."
    ),
    context_providers=[memory.context_provider],
)
```

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

The context provider runs **automatically on every turn**.

The agent never decides to look something up or save a preference. The framework does it.

```
User query arrives
    --> before_run() searches memory, injects context
        --> LLM generates response with memory context
            --> after_run() stores messages, extracts entities
```

This is **passive memory** -- always working in the background.

---

## Multi-Turn Conversation Example

```python
queries = [
    "I really enjoy sci-fi movies, especially ones about time travel.",
    "What did I say my favorite genre was?",
    "Can you recommend something I might like?",
]
```

**Turn 1:** User states a preference. `after_run()` saves the message and extracts "sci-fi" and "time travel" as entities.

**Turn 2:** User asks what they said. `before_run()` retrieves the previous message via semantic search and injects it as context. The agent answers accurately.

**Turn 3:** The agent has both conversation history and extracted preferences. It recommends based on what the user actually said.

---

## Inspecting Stored Memories

After the conversation, verify what the provider stored:

```python
results = await memory.search_memory(
    query="sci-fi movies",
    include_messages=True,
    include_entities=True,
    include_preferences=True,
    limit=5,
)

print("Messages:", results.get("messages", []))
print("Entities:", results.get("entities", []))
print("Preferences:", results.get("preferences", []))
```

This returns messages, entity nodes, and preferences that `after_run()` extracted and stored in Neo4j.

---

## Summary

- **`Neo4jMicrosoftMemory`** provides a context provider for automatic memory
- **`before_run()`** retrieves relevant memories from all three memory types
- **`after_run()`** stores new messages and extracts entities
- The agent gets **persistent memory across turns and sessions** without calling any tools
- Configuration controls which memory types are included and whether entities are extracted
- Uses the same `before_run()`/`after_run()` lifecycle as Module 3 context providers

**Next:** Adding memory tools for explicit agent control.
