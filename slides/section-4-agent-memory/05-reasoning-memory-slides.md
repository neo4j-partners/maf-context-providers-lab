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


# Reasoning Memory

---

## The Third Kind of Memory

- **Short-term** captures what was said
- **Long-term** captures what was learned
- **Reasoning memory** captures what the agent **did** and whether it **worked**

When the agent encounters a similar task later, it can retrieve past reasoning traces to:
- Reuse **successful strategies**
- Avoid approaches that **failed**

---

## What a Reasoning Trace Contains

A reasoning trace records the full execution path of an agent task:

| Component | Description |
|-----------|-------------|
| **Task** | What the agent was trying to accomplish |
| **Steps** | Individual reasoning steps (thought, action, observation) |
| **Tool Calls** | Specific tool invocations with arguments, results, status, and duration |
| **Outcome** | The final result of the task |
| **Success** | Whether the task completed successfully |

Each trace gets a **vector embedding** of the task description, enabling semantic search.

---

## Recording Traces

The `record_agent_trace()` function captures a completed agent execution:

```python
from neo4j_agent_memory.integrations.microsoft_agent import (
    record_agent_trace,
)

trace = await record_agent_trace(
    memory=memory,
    messages=[],
    task="Find sci-fi movies about time travel",
    tool_calls=[
        {
            "name": "search_knowledge",
            "arguments": {"query": "time travel sci-fi"},
            "result": ["Interstellar", "The Matrix", "Back to the Future"],
            "status": "success",
            "duration_ms": 150,
        }
    ],
    outcome="Recommended Interstellar based on user preference for Nolan films",
    success=True,
)
```

---

## How Traces Are Stored in Neo4j

The trace is stored as connected nodes:

```
(ReasoningTrace)
    |
    +--[:HAS_STEP]-->(ReasoningStep)
    |                     |
    |               [:USES_TOOL]-->(ToolCall)
    |
    +--[:IN_SESSION]-->(Session)
```

- The trace links to its steps
- Each step links to its tool calls
- The entire structure connects to the session where it occurred
- Each trace gets a vector embedding for semantic search

---

## Streaming Trace Recording

For real-time agent execution, the `StreamingTraceRecorder` context manager records traces as they happen:

```python
from neo4j_agent_memory.memory.reasoning import StreamingTraceRecorder

async with StreamingTraceRecorder(
    memory_client.reasoning,
    session_id="user-123",
    task="Recommend a movie for the user",
) as recorder:
    step = await recorder.start_step(
        thought="User likes Christopher Nolan. Check preferences.",
        action="recall_preferences",
    )
    await recorder.record_tool_call(
        "recall_preferences",
        {"topic": "movies"},
        result={"preferences": ["Christopher Nolan", "sci-fi"]},
    )
    await recorder.add_observation(
        "User prefers Christopher Nolan and sci-fi. Recommending Interstellar."
    )
```

---

## Finding Similar Traces

When the agent encounters a new task, it searches for traces from similar past tasks:

```python
from neo4j_agent_memory.integrations.microsoft_agent import (
    get_similar_traces,
)

traces = await get_similar_traces(
    memory=memory,
    task="Find action movies with good ratings",
    limit=3,
)

for trace in traces:
    print(f"Task: {trace.task}")
    print(f"Outcome: {trace.outcome}")
    print(f"Success: {trace.success}")
    print(f"Steps: {len(trace.steps)}")
```

Uses vector embedding of the task description to find **semantically similar** past traces.

---

## Tool Statistics

Reasoning memory tracks **aggregate statistics** about tool usage:

```python
stats = await memory_client.reasoning.get_tool_stats()

for tool in stats:
    print(f"{tool.name}: {tool.success_rate:.0%} success, "
          f"avg {tool.avg_duration_ms}ms")
```

This reveals:
- Which tools work **reliably**
- Which tools are **slow**
- Which tools **fail often**

The agent can use this information to prefer tools with higher success rates.

---

## How Reasoning Memory Integrates

**Passive (Context Provider):**
- When `include_reasoning=True` is set on `Neo4jMicrosoftMemory`
- `before_run()` injects relevant reasoning traces automatically
- If the current query is similar to a past task, the agent receives that trace as context

**Active (Memory Tools):**
- The `find_similar_tasks` tool from `create_memory_tools()`
- Agent explicitly looks up past approaches when it wants to

---

## Reasoning Memory in Action

```
Session 1:
    Task: "Find sci-fi movies about time travel"
    Steps: search_knowledge("time travel sci-fi") --> found 3 movies
    Outcome: Recommended Interstellar (SUCCESS)
    --> Trace stored with vector embedding

Session 2:
    Task: "Find action movies with good ratings"
    --> before_run() finds similar trace from Session 1
    --> Agent sees that search_knowledge worked well
    --> Uses same approach: search_knowledge("action movies ratings")
    --> Gets better results by learning from past success
```

---

## Summary

- **Reasoning memory** records agent execution traces: tasks, steps, tool calls, outcomes
- Traces are stored in Neo4j with **vector embeddings** for semantic search
- `record_agent_trace()` captures completed executions
- `StreamingTraceRecorder` records traces in real-time
- `get_similar_traces()` finds past traces for similar tasks
- **Tool statistics** track reliability and performance
- Integrates via both **context provider** (automatic) and **memory tools** (explicit)

**Next:** Graph algorithm integration with GDS.
