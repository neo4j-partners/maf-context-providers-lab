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


# Building a Simple Context Provider

---

## What We Are Building

A `UserInfoMemory` context provider that:

1. **Extracts** user information (name, age) from conversations
2. **Remembers** it across turns using session state
3. **Injects** personalized instructions based on what it knows

This demonstrates both lifecycle methods working together.

---

## Step 1: Define a Pydantic Data Model

Start with a structured model for the data the provider will extract:

```python
from pydantic import BaseModel

class UserInfo(BaseModel):
    name: str | None = None
    age: int | None = None
```

- All fields are **optional** (the provider learns them over time)
- The LLM will return **structured output** matching this schema
- Pydantic validates the extracted data automatically

---

## Step 2: Create the Provider Class

```python
class UserInfoMemory(BaseContextProvider):
    """Context provider that extracts and remembers user info."""

    def __init__(self, client: SupportsChatGetResponse):
        super().__init__("user-info-memory")
        self._chat_client = client

    async def before_run(self, *, context, state, **kwargs):
        # Inject instructions based on what we know
        ...

    async def after_run(self, *, context, state, **kwargs):
        # Extract user info from the conversation
        ...
```

The provider takes a **chat client** to use for structured extraction in `after_run()`.

---

## Step 3: before_run()

```python
async def before_run(self, *, context, state, **kwargs):
    my_state = state.setdefault(self.source_id, {})
    user_info = my_state.setdefault("user_info", UserInfo())

    instructions: list[str] = []

    if user_info.name is None:
        instructions.append(
            "Ask the user for their name and politely decline "
            "to answer any questions until they provide it."
        )
    else:
        instructions.append(f"The user's name is {user_info.name}.")

    if user_info.age is None:
        instructions.append(
            "Ask the user for their age and politely decline "
            "to answer any questions until they provide it."
        )
    else:
        instructions.append(f"The user's age is {user_info.age}.")

    context.extend_instructions(self.source_id, " ".join(instructions))
```

---

## How before_run() Changes Behavior

| State | Instructions Injected | Agent Behavior |
|-------|----------------------|----------------|
| Name unknown, age unknown | "Ask for name... Ask for age..." | Refuses to answer, asks for info |
| Name = "Alex", age unknown | "Name is Alex. Ask for age..." | Greets by name, asks for age |
| Name = "Alex", age = 30 | "Name is Alex. Age is 30." | Fully personalized responses |

The **same agent** behaves differently each turn based on accumulated knowledge.

---

## Step 4: after_run()

```python
async def after_run(self, *, context, state, **kwargs):
    my_state = state.setdefault(self.source_id, {})
    user_info = my_state.setdefault("user_info", UserInfo())
    if user_info.name is not None and user_info.age is not None:
        return  # Already have everything

    request_messages = context.get_messages(
        include_input=True, include_response=True
    )
    user_messages = [
        msg for msg in request_messages
        if hasattr(msg, "role") and msg.role == "user"
    ]
    if not user_messages:
        return
```

First, check if extraction is needed. Skip if all data is already known.

---

## after_run(): The Extraction Call

```python
    try:
        result = await self._chat_client.get_response(
            messages=request_messages,
            instructions=(
                "Extract the user's name and age from the message "
                "if present. If not present return nulls."
            ),
            options={"response_format": UserInfo},
        )
        extracted = result.value
        if extracted and user_info.name is None and extracted.name:
            user_info.name = extracted.name
        if extracted and user_info.age is None and extracted.age:
            user_info.age = extracted.age
        state.setdefault(self.source_id, {})["user_info"] = user_info
    except Exception:
        pass
```

Uses **structured LLM output** with the Pydantic model as `response_format`.

---

## The Data Flow

```
before_run() reads state  ──>  Injects instructions
                                      |
                                LLM responds
                                      |
after_run() reads messages ──>  Extracts data  ──>  Writes to state
                                                         |
                                              Next turn's before_run()
                                              reads updated state
```

`before_run()` **reads** from state. `after_run()` **writes** to state. State persists across turns.

---

## Step 5: Register and Run

```python
async def main():
    client = OpenAIResponsesClient()

    agent = client.as_agent(
        name="context-provider-agent",
        instructions=(
            "You are a friendly assistant. Always address "
            "the user by their name when you know it."
        ),
        context_providers=[UserInfoMemory(client)],
    )

    session = agent.create_session()
```

---

## Multi-Turn Conversation

```python
queries = [
    "Hello, what is the square root of 9?",
    "My name is Alex and I am 30 years old",
    "Now, what is the square root of 9?",
]

for query in queries:
    response = await agent.run(query, session=session)
    print(response.text)
```

| Turn | User Says | Agent Does |
|------|-----------|------------|
| 1 | "What is sqrt(9)?" | Asks for name and age instead |
| 2 | "I'm Alex, age 30" | `after_run()` extracts name + age |
| 3 | "What is sqrt(9)?" | Answers "3" and addresses Alex by name |

---

## Inspecting Extracted State

After the conversation, verify the extracted data:

```python
user_info = session.state.get("user-info-memory", {}).get(
    "user_info", UserInfo()
)
print(f"Extracted Name: {user_info.name}")  # Alex
print(f"Extracted Age: {user_info.age}")    # 30
```

The `state` dictionary is keyed by the provider's `source_id` (`"user-info-memory"`).

---

## Key Takeaways

- **Pydantic models** define the structure for extracted data
- **`before_run()`** reads state and injects dynamic instructions
- **`after_run()`** extracts structured data using an LLM call with `response_format`
- **Session state** persists across turns, letting the provider accumulate knowledge
- The provider changes agent behavior **dynamically** without any tool calls
- A single provider instance is shared; **state dict** keeps sessions isolated

**Next:** Use Neo4j context providers for automatic knowledge graph retrieval.
