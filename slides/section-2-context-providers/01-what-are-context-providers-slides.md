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


# What Are Context Providers?

---

## The Problem with Tools Alone

Tools are **reactive** -- the agent must recognize a tool is relevant and choose to call it.

- The agent may not realize the tool is relevant to a general question
- The agent may skip the tool to answer faster
- For every query, the agent has to reason about whether each tool applies

**Example:** "Recommend something good" -- the agent has no reason to call a movie lookup tool and answers from training data alone.

---

## Context Providers: The Solution

Context providers **inject relevant knowledge before every LLM call**, regardless of the query.

| Mechanism | When It Runs | Who Decides |
|-----------|-------------|-------------|
| **Tools** | On demand | The agent decides |
| **Context Providers** | Every invocation | Automatic |

The agent does not decide whether to use a context provider. It always runs.

---

## The Context Provider Lifecycle

A context provider extends `BaseContextProvider` and implements two lifecycle methods:

| Hook | When It Runs | What It Does |
|------|-------------|--------------|
| **`before_run()`** | Before LLM invocation | Injects instructions, messages, or tools into the context |
| **`after_run()`** | After LLM responds | Extracts data, stores messages, updates session state |

---

## Lifecycle in Action

```
Agent.run(query)
    |
    +-- 1. Context Providers: before_run()
    |       +-- Inject instructions, messages, and tools
    |           into SessionContext
    |
    +-- 2. LLM Invocation
    |       +-- Process instructions + context + user query
    |       +-- Decide which tools to call (if any)
    |       +-- Generate response
    |
    +-- 3. Context Providers: after_run()
            +-- Extract data, store messages,
                update session state
```

---

## The BaseContextProvider Class

```python
from agent_framework import BaseContextProvider, AgentSession, SessionContext
from typing import Any

class MyProvider(BaseContextProvider):
    def __init__(self):
        super().__init__("my-provider")

    async def before_run(
        self, *, agent: Any, session: AgentSession | None,
        context: SessionContext, state: dict[str, Any],
    ) -> None:
        context.extend_instructions(
            self.source_id,
            "Additional instructions for the agent."
        )

    async def after_run(
        self, *, agent: Any, session: AgentSession | None,
        context: SessionContext, state: dict[str, Any],
    ) -> None:
        pass
```

---

## Two Ways to Inject Context

**`before_run()`** has two injection methods:

- **`context.extend_instructions()`** -- Adds text to the agent's system prompt
  - Use for behavioral guidance: "The user's name is Alice"

- **`context.extend_messages()`** -- Adds messages to the conversation
  - Use for data: search results from a knowledge graph

```python
async def before_run(self, *, context, **kwargs):
    context.extend_instructions(
        self.source_id,
        "Focus on sci-fi recommendations."
    )
```

---

## State Management

A single provider instance is shared across all sessions. Storing session-specific data in instance variables would mix state between users.

Use the **`state` dictionary** passed to `before_run()` and `after_run()`:

```python
async def before_run(self, *, state: dict[str, Any], **kwargs) -> None:
    # Initialize state on first call
    my_state = state.setdefault(self.source_id, {"count": 0})
    my_state["count"] += 1
```

- State is **scoped to the session**
- State **persists across conversation turns**
- All providers can read and write to `state`

---

## Registering Providers

Pass context providers when creating an agent:

```python
agent = client.as_agent(
    name="my-agent",
    instructions="You are a helpful assistant.",
    context_providers=[MyProvider()],
)
```

You can register **multiple providers**. Each runs in order before and after every invocation.

---

## Tools vs. Context Providers

| | Tools | Context Providers |
|---|-------|-------------------|
| **Trigger** | Agent chooses to call | Runs automatically every turn |
| **Best for** | Specific actions (lookup, calculate) | Background knowledge, personalization |
| **Risk** | Agent may skip the call | Always injects context |
| **Example** | "Search for movie X" | "User prefers sci-fi" |

Use **tools** for on-demand actions. Use **context providers** for knowledge that should always be present.

---

## Summary

- **Tools are reactive** -- the agent must decide to call them
- **Context providers run automatically** before and after every LLM invocation
- **`before_run()`** injects instructions or messages into the context
- **`after_run()`** extracts data and updates session state
- **`state` dictionary** stores session-scoped data that persists across turns
- Register providers via the `context_providers` parameter on the agent

**Next:** Build a context provider from scratch.
