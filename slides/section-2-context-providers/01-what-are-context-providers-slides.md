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

## Hallucination: Confident But Wrong

LLMs generate responses based on statistical likelihood, not factual verification.

- Produces the most *probable* continuation, not the most *accurate*
- Never says "I don't know," generates plausible-sounding text instead
- Fabricates details and citations

**Real Example:** In 2023, US lawyers were sanctioned for submitting an LLM-generated brief with six fictitious case citations.

---

## Knowledge Cutoff: No Access to Your Data

LLMs are trained at a specific point in time on publicly available data.

**They don't know:**
- Recent events after their training cutoff
- Your company's documents, databases, or internal knowledge
- Real-time data: current prices, live statistics, changing conditions

**The Risk:** Ask about your Q3 results or last week's board meeting, and the LLM may still generate a confident (and wrong) response.

---

## Relationship Blindness: Can't Connect the Dots

LLMs process text sequentially and treat each piece in isolation.

**Questions they struggle with:**
- "Which asset managers own companies facing cybersecurity risks?"
- "What products are mentioned by companies that share risk factors?"
- "How are these two companies connected through their executives?"

These questions require *reasoning over relationships*, connecting entities across documents and traversing chains of connections.

---

## The Solution: Providing Context

All three limitations have a common solution: **providing context**.

When you give an LLM relevant information in its prompt:
- It has facts to work with (reduces hallucination)
- It can access your specific data (overcomes knowledge cutoff)
- You can structure that information to show relationships (enables reasoning)

But how do you provide that context? One approach is **tools**, but they have limits.

---

## The Problem with Tools Alone

Tools are **reactive**: the agent must recognize a tool is relevant and choose to call it.

- The agent may not realize the tool is relevant to a general question
- The agent may skip the tool to answer faster
- For every query, the agent has to reason about whether each tool applies

**Example:** "Recommend something good." The agent has no reason to call a movie lookup tool and answers from training data alone.

---

## Context Providers: The Solution

Context providers **inject relevant knowledge before every LLM call**, regardless of the query.

As you saw earlier: tools are on-demand and agent-managed, while context providers run automatically on every invocation.

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

- **`context.extend_instructions()`**: Adds text to the agent's system prompt
  - Use for behavioral guidance: "The user's name is Alice"

- **`context.extend_messages()`**: Adds messages to the conversation
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

## Summary

- **Tools are reactive**: the agent must decide to call them
- **Context providers run automatically** before and after every LLM invocation
- **`before_run()`** injects instructions or messages into the context
- **`after_run()`** extracts data and updates session state
- **`state` dictionary** stores session-scoped data that persists across turns
- Register providers via the `context_providers` parameter on the agent

**Next:** Build a context provider from scratch.
