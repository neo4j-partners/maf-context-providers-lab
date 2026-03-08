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


# What is the Microsoft Agent Framework?

---

## History

MAF is the direct successor to both **Semantic Kernel** and **AutoGen**, created by the same teams at Microsoft.

| Predecessor | What MAF Takes From It |
|-------------|----------------------|
| **AutoGen** | Straightforward agent abstractions |
| **Semantic Kernel** | Session-based state management, type safety, middleware, telemetry |

Developers migrating from either framework have a clear upgrade path. The core patterns are familiar; the execution model is more structured.

---

## What is the Microsoft Agent Framework?

The [Microsoft Agent Framework](https://github.com/microsoft/agent-framework) orchestrates a lifecycle around each LLM call, turning a bare model into an agent that can retrieve, reason, and act.

- Multi-language: **Python** and **.NET**
- Multi-provider: **Azure OpenAI**, **OpenAI**, **Anthropic**, **Ollama**
- Open source on GitHub

---

<!-- _class: small -->
<style scoped>section { font-size: 95%; }</style>

## Core Concepts

The core concept in MAF is the **agent**. An agent follows the **ReAct** (Reasoning and Acting) pattern — it reasons about input, decides which actions to take, observes the results, and repeats until it can provide a final response.

The framework builds on this with four supporting concepts:

| Concept | Description |
|---------|-------------|
| **Tools** | Plain Python functions the agent can decide to call |
| **Context Providers** | Components that can run automatically before, after, or both before and after each invocation to inject or extract context |
| **Sessions** | State containers that persist data across conversation turns |
| **Workflows** | Graph-based orchestration connecting agents and functions for multi-step tasks |

---

## What Are Tools?

Tools are plain Python functions that an agent can decide to call. The agent uses the function name and docstring to determine relevance, and chooses when to invoke them.

- "Tell me about Inception" --> agent calls `get_movie_info`
- "Run this Cypher query" --> agent calls `query_database`

This works well for specific actions, but poorly for background knowledge — the agent may not realize it should ask.

---

## What Are Context Providers?

Context providers are components that can run automatically before, after, or both before and after each agent invocation.

- **Before** every LLM call: `before_run()` injects relevant data
- **After** every LLM response: `after_run()` extracts and stores information
- The agent never decides whether to use the provider -- it just receives the context

---

## Why Context Providers?

This course focuses on context providers, the concept that sets MAF apart. The distinction from tools is central to everything that follows.

| | Tools | Context Providers |
|---|---|---|
| **When** | Agent decides to call | Runs automatically every invocation |
| **How** | Agent reads function name + docstring | `before_run()` injects into context |
| **Use case** | On-demand actions (lookups, queries) | Always-available background knowledge |
| **Control** | Agent-managed | Framework-managed |

---

## The Agent Lifecycle

Now that you understand both tools and context providers, here is how they fit into each agent invocation:

```
Agent.run(query)
    |
    +-- 1. Context Providers: before_run()
    |       +-- Inject instructions, messages, and tools
    |
    +-- 2. LLM Invocation
    |       +-- Process instructions + context + query
    |       +-- Decide which tools to call (if any)
    |       +-- Generate response
    |
    +-- 3. Context Providers: after_run()
            +-- Extract data, store messages, update state
```

---

## Self-Grounding Agents with Neo4j

Context providers enable a powerful pattern: **self-grounding agents**.

A self-grounding agent automatically receives relevant knowledge from a data source on every interaction, without relying on tools or custom orchestration code.

**Example:** Ask about a movie, and the Neo4j context provider has already searched the graph for relevant movies, actors, and genres **before** the LLM generates its answer.

---

## What You Will Build in This Course

Self-grounding agents that:

- Search Neo4j **vector indexes** for semantically relevant content
- Traverse **graph relationships** for enriched context
- Store and recall **agent memories** in Neo4j

All powered by context providers that run automatically on every turn.

---

## Summary

- **MAF** succeeds Semantic Kernel and AutoGen, combining both into a single framework
- Supports **Python and .NET** with multiple LLM providers
- Built around **agents** using the **ReAct** pattern, with Tools, Context Providers, Sessions, and Workflows
- **Tools** are reactive -- the agent decides when to call them
- **Context providers** are proactive -- they inject knowledge on every turn automatically
- This enables **self-grounding agents** that are always informed by relevant data

**Next:** Set up your development environment.
