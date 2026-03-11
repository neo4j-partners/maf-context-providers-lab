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

- Each trace gets a **vector embedding** of the task description, enabling semantic search

---

## Recording Traces

The `record_agent_trace()` function captures a completed agent execution. You provide:

- **Task**: what the agent was trying to accomplish
- **Tool calls**: each tool invocation with its name, arguments, result, status, and duration
- **Outcome**: a description of what the agent concluded
- **Success**: whether the task completed successfully

- Stores the full trace in Neo4j as connected nodes (trace → steps → tool calls)
- Adds a vector embedding of the task description for later semantic search

---

## How Traces Are Stored in Neo4j

The trace is stored as a hierarchy of connected nodes:

- A **ReasoningTrace** node holds the task description, outcome, and success status
- It links to individual **ReasoningStep** nodes via `HAS_STEP` relationships
- Each step links to its **ToolCall** nodes via `USES_TOOL` relationships
- The entire structure connects to the **Session** where it occurred
- Each trace gets a **vector embedding** of its task description, enabling semantic search for similar past tasks

---

## Streaming Trace Recording

For real-time agent execution, the `StreamingTraceRecorder` records traces **as they happen** rather than after completion:

- Use it as an async context manager that opens a trace on entry and finalizes it on exit
- Call `start_step()` to begin a reasoning step with a thought and planned action
- Call `record_tool_call()` each time the agent invokes a tool
- Call `add_observation()` to record what the agent learned from the result

This is useful when you want to capture the agent's reasoning process step by step, rather than reconstructing it after the fact.

---

## Finding Similar Traces

When the agent encounters a new task, it can search for traces from similar past tasks using `get_similar_traces()`.

- The function embeds the new task description and performs a **vector similarity search** against stored traces
- Returns matching traces with their task, outcome, success status, and steps
- The agent can review what worked (or failed) before deciding on an approach

- Agents **learn from experience** by retrieving relevant past executions at inference time — no retraining needed

---

## Tool Statistics

Reasoning memory tracks **aggregate statistics** about tool usage across all recorded traces. Calling `get_tool_stats()` reveals:

- Which tools work **reliably** (high success rate)
- Which tools are **slow** (high average duration)
- Which tools **fail often** (low success rate)

The agent can use this information to prefer tools with higher success rates or to flag unreliable tools for investigation. Over time, this builds a performance profile of every tool in the agent's toolkit.

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

- **Session 1:** *"Find sci-fi movies about time travel."*
  — Agent uses `search_knowledge`, finds 3 movies, recommends Interstellar; trace is stored with a vector embedding
- **Session 2:** *"Find action movies with good ratings."*
  — `before_run()` finds the similar trace from Session 1; agent reuses the `search_knowledge` approach that worked before

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
