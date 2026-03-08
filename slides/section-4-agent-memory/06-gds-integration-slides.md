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


# Graph Algorithm Integration

---

## Beyond Simple Lookups

Without GDS, the agent can search entities by **name** and **embedding similarity**.

With GDS, the agent gains **graph algorithm capabilities**:

- **PageRank** -- Which entities are most important?
- **Shortest Path** -- How are two entities connected?
- **Node Similarity** -- Which entities are like this one?

These answer questions that simple lookups can't.

---

## PageRank: Entity Importance

Identifies the **most important entities** based on graph connectivity.

An entity mentioned in many conversations and linked to many other entities ranks higher.

**Use case:** "What are the most important topics we've discussed?"

The agent calls `find_important_entities` and gets entities ranked by their centrality in the memory graph.

---

## Shortest Path: Connection Discovery

Finds **connection paths** between entities through the graph.

**Use case:** "How is Christopher Nolan connected to Blade Runner?"

The path might reveal connections through:
- Shared actors
- Shared genres
- Shared themes
- Conversation mentions

The agent calls `find_connection_path` to traverse the entity graph.

---

## Node Similarity: Related Entities

Finds entities with **similar graph neighborhoods**.

Two directors who share actors, genres, or themes will score as similar -- even if their names never appear together in conversation.

**Use case:** "What else is like this?"

The agent calls `find_similar_items` to discover entities with similar relationship patterns.

---

## Configuring GDS Integration

GDS is **optional**. Enable it through `Neo4jMicrosoftMemory`:

```python
from neo4j_agent_memory.integrations.microsoft_agent import GDSConfig

memory = Neo4jMicrosoftMemory.from_memory_client(
    memory_client=memory_client,
    session_id="movie-gds-session",
    include_short_term=True,
    include_long_term=True,
    include_reasoning=True,
    extract_entities=True,
    gds_config=GDSConfig(
        enabled=True,
        use_pagerank_for_ranking=True,
        pagerank_weight=0.3,
    ),
)
```

---

## GDS Configuration Options

| Parameter | Purpose | Default |
|-----------|---------|---------|
| **`enabled`** | Master toggle for GDS features | `False` |
| **`use_pagerank_for_ranking`** | Rank entity search results partly by PageRank | `False` |
| **`pagerank_weight`** | How much PageRank influences ranking (0.0-1.0) | `0.3` |
| **`fallback_to_basic`** | Fall back to basic Cypher if GDS not installed | `True` |

Higher `pagerank_weight` values favor well-connected entities in search results.

---

## GDS Tools

When GDS is enabled, `create_memory_tools()` generates **additional tools**:

```python
tools = create_memory_tools(memory, include_gds_tools=True)
```

| Tool | Purpose |
|------|---------|
| **`find_connection_path`** | Shortest path between two entities |
| **`find_similar_items`** | Entities with similar graph neighborhoods |
| **`find_important_entities`** | Most central entities by PageRank |

These work alongside the six standard memory tools.

---

## Example: Using GDS Tools

```python
agent = client.as_agent(
    name="movie-gds-agent",
    instructions=(
        "You are a movie assistant with access to a knowledge graph. "
        "You can find connections between entities, discover similar "
        "items, and identify the most important topics in conversations."
    ),
    tools=tools,
    context_providers=[memory.context_provider],
)

query = "How is Christopher Nolan connected to Ridley Scott?"
response = await agent.run(query, session=session)
```

The agent uses `find_connection_path` to traverse the entity graph and find connections through shared actors, genres, themes, or conversation mentions.

---

## When GDS Is Not Available

If Neo4j GDS is not installed (e.g., on a free-tier sandbox), the integration **falls back** to basic Cypher queries:

| Algorithm | GDS Version | Fallback Version |
|-----------|-------------|-----------------|
| **Shortest Path** | GDS shortest path | Cypher `shortestPath()` |
| **PageRank** | GDS PageRank | Degree-based approximation |
| **Node Similarity** | GDS node similarity | Degree-based approximation |

The tools still work, but with **reduced accuracy**.

Set `fallback_to_basic=True` (default) to enable this behavior.

---

## The Full Memory Stack

| Layer | Components | Purpose |
|-------|-----------|---------|
| **Context Provider** | `memory.context_provider` | Automatic memory injection/extraction |
| **Memory Tools** | `create_memory_tools()` | Explicit search, save, recall |
| **GDS Tools** | `create_memory_tools(include_gds_tools=True)` | Graph algorithm analysis |
| **Memory Types** | Short-term, long-term, reasoning | Different kinds of memory |
| **Storage** | Neo4j graph database | Connected, persistent, searchable |

All layers work together, backed by the same Neo4j database.

---

## Course Summary

You have built agents with:

- **Tools** -- Python functions the agent can call on demand
- **Context Providers** -- Automatic knowledge graph retrieval before every turn
- **Vector, fulltext, and hybrid search** -- Different retrieval strategies
- **Graph-enriched traversal** -- Following relationships for richer context
- **Persistent memory** -- Short-term, long-term, and reasoning memory backed by Neo4j
- **Entity extraction** -- Automatic structured knowledge from unstructured conversation
- **Graph algorithm analysis** -- PageRank, shortest path, and node similarity via GDS

---

## Summary

- **GDS integration** adds graph algorithm capabilities to agent memory
- **PageRank** identifies the most important entities
- **Shortest Path** discovers connections between entities
- **Node Similarity** finds related entities by graph neighborhood
- These are exposed as **agent tools** alongside memory context provider and standard memory tools
- **Fallback mode** uses basic Cypher when GDS is not installed
- This completes the full memory stack: context provider + memory tools + GDS tools
