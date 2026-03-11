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

- **Long-term memory**: stores entities, preferences, and facts extracted from conversations
- **Extraction pipeline**: processes conversation messages to identify entities and store them as Neo4j nodes
- **Multi-stage approach**: combines fast pattern matching, model-based extraction, and LLM fallback
- **Results are merged** to maximize coverage and accuracy

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

## Configuring Extraction

Configured through `MemorySettings` with an `extraction` section:

- **Stages**: spaCy, GLiNER, and LLM fallback can each be toggled independently
- **Confidence threshold**: minimum score (0.0–1.0) for storing an entity
- **Entity types**: limit extraction to specific POLE+O types
- **Extractor type**: `"pipeline"` for multi-stage, or `"llm"` for LLM-only
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

The same entity may be mentioned differently: "Christopher Nolan," "Nolan," "the director of Inception."

- **Auto-merge (0.95+)**: merged automatically
- **Flag (0.85–0.95)**: flagged for review
- **Below threshold**: treated as distinct entities
- **Resolution strategy**: combines exact matching, fuzzy string matching, and semantic similarity

---

## Automatic vs Manual Extraction

**Automatic:** extraction runs in `after_run()` after every agent response

- Processes the agent's most recent response, not the full conversation history
- **Async by default** — runs as a background task, doesn't block the next turn
- Sync and offline batch modes also available

**Manual:** pre-populate the graph with known entities using `MemoryClient`

- Useful for seeding domain knowledge before the agent starts (key people, products, locations)

---

## The Full Pipeline in Action

Given a message like *"I love Christopher Nolan's Inception"*:

1. **spaCy** quickly identifies "Christopher Nolan" as a PERSON
2. **GLiNER** confirms "Christopher Nolan" (PERSON, confidence 0.95) and also finds "Inception" (OBJECT, confidence 0.92)
3. **LLM** skips entities already found, saving time and cost
4. **Merge** uses the confidence strategy, keeping the highest-confidence result for each entity
5. **Store**: both entities are saved as `:Entity` nodes in Neo4j, linked back to the source conversation

---

## Summary

- The extraction pipeline uses **three stages**: spaCy, GLiNER, LLM
- Entities are typed using the **POLE+O schema** (Person, Object, Location, Event, Organization)
- Results are merged using configurable **merge strategies**
- Duplicate entities are resolved using **embedding similarity**
- Extracted entities become **labeled nodes in Neo4j** linked to their source conversations
- Extraction can be **automatic** (after every turn) or **manual** (pre-populated)

**Next:** Using memory as a context provider.
