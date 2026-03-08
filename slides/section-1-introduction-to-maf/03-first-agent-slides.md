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


# Creating Your First Agent with Tools

---

## What You Will Build

A movie information agent that:

1. Connects to OpenAI using the `OpenAIResponsesClient`
2. Has a **tool** that looks up movie details
3. Streams responses in real-time
4. Demonstrates the **limitation** of tools for general queries

> **Hands-on:** Follow along in `labs/lab-1-first-agent.ipynb`

---

## Step 1: Create the Client

The `OpenAIResponsesClient` connects to the OpenAI API. It reads credentials from your environment automatically:

```python
from agent_framework.openai import OpenAIResponsesClient

client = OpenAIResponsesClient()
```

No API key or model name in code -- it reads `OPENAI_API_KEY` and `OPENAI_RESPONSES_MODEL_ID` from your `.env` file.

---

## Step 2: Define a Tool

In MAF, tools are **plain Python functions** with docstrings. No decorators or registration required.

```python
from typing import Annotated
from pydantic import Field

def get_movie_info(
    movie_title: Annotated[str, Field(description="The movie title to look up")]
) -> str:
    """Look up information about a movie including its director,
    year, genres, and plot summary."""
    key = movie_title.upper().strip()
    info = MOVIES.get(key)
    if info:
        return f"Title: {info['title']}\nDirector: {info['director']}..."
    return f"Movie '{movie_title}' not found."
```

---

## How Tool Selection Works

The agent reads the function **name** and **docstring** to decide when to call the tool:

```
User: "Tell me about Inception"
    |
Agent sees tools:
  - get_movie_info: "Look up information about a movie..."
    |
Agent reasons: "User asks about a movie -> get_movie_info"
    |
Agent calls: get_movie_info(movie_title="Inception")
    |
Agent responds with the movie data
```

**Better docstrings lead to better tool selection.**

---

## Why Annotations Matter

Compare these two definitions:

**Vague (poor selection):**
```python
def search(query):
    """Search the database."""
```

**Specific (accurate selection):**
```python
def get_movie_info(
    movie_title: Annotated[str, Field(description="The movie title to look up")]
) -> str:
    """Look up information about a movie including its director,
    year, genres, and plot summary."""
```

`Annotated` + `Field` tells the agent exactly what each parameter expects.

---

## Step 3: Create the Agent

Use `client.as_agent()` with a name, instructions, and tools:

```python
agent = client.as_agent(
    name="movie-info-agent",
    instructions=(
        "You are a helpful movie assistant. Use your tool to look up "
        "movie information when asked about a specific movie. If the "
        "user asks about a movie not in your database, let them know "
        "which movies are available."
    ),
    tools=[get_movie_info],
)
```

**Key elements:** `instructions` define behavior, `tools` list available functions.

---

## Step 4: Run with Streaming

Execute the agent and stream the response:

```python
query = "Tell me about Inception"
async for update in agent.run(query, stream=True):
    if update.text:
        print(update.text, end="", flush=True)
```

The agent will:
1. Receive the query
2. Recognize `get_movie_info` is relevant
3. Call the tool with `movie_title="Inception"`
4. Stream a response using the returned movie data

---

## The Limitation of Tools

Try a general question that does not name a specific movie:

```python
await agent.run("What are some good sci-fi movies about time travel?")
```

The agent **may or may not** call `get_movie_info`:

- Tools are **reactive** -- the agent must choose to call them
- For broad or exploratory queries, the agent often does not realize it should ask
- This works for explicit lookups, but fails for background knowledge

---

## Tools: When They Work, When They Don't

| Query Type | Tool Behavior | Result |
|------------|--------------|--------|
| "Tell me about Inception" | Agent calls `get_movie_info` | Accurate, grounded response |
| "Who directed The Matrix?" | Agent calls `get_movie_info` | Accurate, grounded response |
| "What are good sci-fi movies?" | Agent may skip the tool | Ungrounded, generic response |
| "Recommend something like Pulp Fiction" | Agent may skip the tool | Misses available data |

---

## The Gap: Background Knowledge

What if you want the agent to **always** have relevant movie data, regardless of how the question is phrased?

- Tools require the agent to **decide** to call them
- Background knowledge should be available **automatically**
- The agent should not need to "ask" for context it always needs

**This is where context providers come in** -- which you will explore in the next module.

---

## Summary

- The `OpenAIResponsesClient` connects to OpenAI with credentials from environment variables
- **Tools** are plain Python functions with docstrings -- no decorators needed
- The agent uses the function **name** and **docstring** to decide when to call a tool
- `Annotated` type hints and `Field` descriptions improve tool selection
- Tools are **reactive**: the agent must choose to call them
- For general queries, the agent may skip relevant tools entirely

**Next:** Introduction to context providers -- MAF's mechanism for automatic context injection.
