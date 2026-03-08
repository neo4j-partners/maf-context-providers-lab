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


# Entity Extraction Pipeline

---

## From Unstructured Text to Structured Graph

Long-term memory stores entities, preferences, and facts extracted from conversations.

But how does the extraction happen?

The `neo4j-agent-memory` package uses a **multi-stage pipeline** that combines:
- Fast pattern matching
- Model-based extraction
- LLM fallback

Results are merged to maximize **coverage** and **accuracy**.

---

## The Three-Stage Pipeline

Each stage has different strengths. They run in sequence:

| Stage | Tool | Strengths | Trade-offs |
|-------|------|-----------|------------|
| **1. spaCy** | Rule-based NER | Fast, no API calls, runs locally | Limited to common entity types |
| **2. GLiNER** | Lightweight model | More accurate for domain-specific entities, supports POLE+O | Slower than spaCy |
| **3. LLM** | Language model | Most accurate, catches what others missed | Slowest, most expensive |

If spaCy catches "Christopher Nolan" as PERSON, GLiNER confirms it, and the LLM stage can skip entities already found.

---

## The POLE+O Schema

Entities are typed using the POLE+O data model:

| Type | Description | Example |
|------|-------------|---------|
| **P**erson | Individual people | Christopher Nolan, Leonardo DiCaprio |
| **O**bject | Physical or conceptual things | Inception, iPhone |
| **L**ocation | Places | Los Angeles, Cupertino |
| **E**vent | Occurrences with a time aspect | Oscar Ceremony, Film Festival |
| **O**rganization | Companies, groups | Warner Bros, Neo4j |

Each entity can also have a **subtype** for finer classification (e.g., Person:Individual, Object:Vehicle).

---

## How Entities Map to Neo4j

Extracted entities become nodes with labels derived from the POLE+O type and subtype:

| Entity Type | Subtype | Neo4j Labels |
|-------------|---------|--------------|
| PERSON | INDIVIDUAL | `:Entity:Person:Individual` |
| OBJECT | VEHICLE | `:Entity:Object:Vehicle` |
| ORGANIZATION | COMPANY | `:Entity:Organization:Company` |
| LOCATION | CITY | `:Entity:Location:City` |
| EVENT | MEETING | `:Entity:Event:Meeting` |

Each entity node stores name, type, subtype, description, confidence score, and a vector embedding.

---

## Configuring Extraction with MemorySettings

```python
settings = MemorySettings(
    neo4j={
        "uri": os.environ["NEO4J_URI"],
        "username": os.environ["NEO4J_USERNAME"],
        "password": SecretStr(os.environ["NEO4J_PASSWORD"]),
    },
    extraction={
        "extractor_type": "pipeline",
        "enable_spacy": True,
        "enable_gliner": True,
        "enable_llm_fallback": True,
        "confidence_threshold": 0.5,
        "entity_types": [
            "PERSON", "ORGANIZATION", "LOCATION", "EVENT", "OBJECT"
        ],
    },
)
```

---

## Key Extraction Parameters

| Parameter | Purpose |
|-----------|---------|
| **`extractor_type`** | `"pipeline"` for multi-stage, `"llm"` for LLM-only |
| **`enable_spacy`** | Toggle spaCy stage on/off |
| **`enable_gliner`** | Toggle GLiNER stage on/off |
| **`enable_llm_fallback`** | Toggle LLM fallback on/off |
| **`confidence_threshold`** | Minimum score (0.0-1.0) for entity storage. Lower = more entities, more noise |
| **`entity_types`** | Limit extraction to specific POLE+O types |

---

## Merge Strategies

When multiple stages find the same entity, the pipeline decides which result to keep:

| Strategy | Behavior | Best For |
|----------|----------|----------|
| **`confidence`** | Keeps highest confidence score per entity | Default, usually best |
| **`union`** | Keeps all unique entities from all stages | Maximum coverage |
| **`intersection`** | Only keeps entities found by multiple stages | Maximum precision |
| **`cascade`** | Uses first stage results, fills gaps with later stages | Speed (later stages skip found entities) |

---

## Entity Deduplication

The same entity may be mentioned in different ways: "Christopher Nolan," "Nolan," "the director of Inception."

The package deduplicates using **embedding similarity**:

| Threshold | Behavior |
|-----------|----------|
| Above **auto-merge** (0.95) | Merged automatically |
| Between **flag** (0.85) and auto-merge | Flagged for review |
| Below **flag** threshold | Treated as distinct entities |

```python
resolution={
    "strategy": "composite",
    "exact_threshold": 1.0,
    "fuzzy_threshold": 0.85,
    "semantic_threshold": 0.8,
}
```

---

## Automatic vs Manual Extraction

**Automatic:** When `extract_entities=True` is set on `Neo4jMicrosoftMemory`, entity extraction runs in `after_run()` after every agent response. Runs **asynchronously** so it doesn't slow responses.

**Manual:** Pre-populate the memory graph with known entities:

```python
async with MemoryClient(settings) as memory_client:
    entity = await memory_client.long_term.add_entity(
        name="Inception",
        entity_type="OBJECT",
        description="2010 science fiction film directed by Christopher Nolan",
    )
```

---

## The Full Pipeline in Action

```
User: "I love Christopher Nolan's Inception"
                    |
        +-----------+-----------+
        v           v           v
      spaCy      GLiNER       LLM
   "Christopher  "Christopher  (skips already
    Nolan"        Nolan"        found entities)
   (PERSON)      (PERSON,
                  conf: 0.95)
        +-----+-----+
              v
        Merge (confidence strategy)
              v
    "Christopher Nolan" (PERSON, 0.95)
    "Inception" (OBJECT, 0.92)
              v
    Store in Neo4j as :Entity nodes
    Link to source conversation
```

---

## Summary

- The extraction pipeline uses **three stages**: spaCy, GLiNER, LLM
- Entities are typed using the **POLE+O schema** (Person, Object, Location, Event, Organization)
- Results are merged using configurable **merge strategies**
- Duplicate entities are resolved using **embedding similarity**
- Extracted entities become **labeled nodes in Neo4j** linked to their source conversations
- Extraction can be **automatic** (after every turn) or **manual** (pre-populated)

**Next:** Using memory as a context provider.
