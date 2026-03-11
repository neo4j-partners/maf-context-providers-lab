# Slides: Dense Paragraph Blocks to Fix

Convert dense prose into definition lists (bold term + definition) or bullet points. The most common pattern is: intro prose + bullets + dense prose conclusion — make the conclusion a bullet too.

## Section 1: Introduction to MAF

### 01-what-is-maf-slides.md

- **"What Are Tools?"** (line ~72): Opening sentence and closing sentence are prose sandwiching bullets. Convert both to bullets.

### 02-setup-slides.md

- **"What the Codespace Does"** (line ~98): Trailing blockquote note could be a bullet instead.

## Section 2: Context Providers

### 01-what-are-context-providers-slides.md

- **"Relationship Blindness"** (line ~69): Trailing sentence "These questions require *reasoning over relationships*..." should be a bullet.
- **"The Problem with Tools Alone"** (line ~94): Trailing **Example:** paragraph should be a definition-list entry.
- **"State Management"** (lines ~190-191): Two-sentence prose explanation of the problem. Convert to bullets or definition list.

### 02-simple-context-provider-slides.md

- **"The Data Flow"** (line ~193): Trailing sentence after diagram. Convert to bullet.

## Section 3: Neo4j Context Providers

### 01-neo4j-context-providers-overview-slides.md

- **"Neo4j Context Providers for MAF"** (line ~42): Trailing sentence "This module focuses on..." should be a bullet.
- **"Beyond Retrieval"** (lines ~50-52): Last two bullets are explanatory prose. Tighten.
- **"Neo4jContextProvider"** (line ~64): Trailing sentence "You configure the provider..." should be a bullet.

### 02-vector-provider-slides.md

- **"What is Vector Search?"** (lines ~37, 44): Opening definition and closing enablement sentence are prose. Convert to definition list.
- **"Embeddings Must Match"** (line ~76): Trailing sentence listing supported embedders. Convert to bullet list.
- **"Configure the Provider"** (lines ~101-102): Last two bullets contain multi-sentence explanations. Simplify.
- **"With vs Without Context"** (lines ~138-144): Both comparison blocks are prose. Convert to definition list entries with bullets.

### 03-graph-enriched-provider-slides.md

- **"Why Search Alone Isn't Enough"** (line ~45): Trailing bold conclusion. Convert to bullet.
- **"The Two-Step Process"** (line ~60): Trailing sentence "The matched node is the anchor..." should be a bullet.
- **"Why OPTIONAL MATCH Matters"** (lines ~146-148): Two trailing prose paragraphs (importance explanation + rule of thumb). Convert to bullets.

### 04-fulltext-provider-slides.md

- **"How It Works"** (line ~62): Opening prose before numbered list. Convert to definition or bullet.
- **"BM25 Ranking"** (line ~79): Trailing example sentence. Convert to bullet.
- **"Stop Word Filtering"** (line ~119): Trailing explanation sentence. Convert to bullet.
- **"Using the Provider with an Agent"** (line ~141): Trailing interchangeability sentence. Convert to bullet.

### 05-hybrid-provider-slides.md

- **"The Problem with One Search Mode"** (line ~44): Trailing bold solution statement. Convert to bullet.
- **"Requirements"** (line ~84): Trailing sentence "Both indexes must exist..." should be a bullet or note.
- **"Using the Provider with an Agent"** (line ~108): Trailing interchangeability sentence. Convert to bullet.

## Section 4: Agent Memory

### 01-memory-types-slides.md

- **"A Conversation Without Memory"** (lines ~51-52, 58): Setup prose and bold conclusion. Convert both to bullets.
- **"What Memory Needs to Capture"** (lines ~66-73): Multi-sentence explanations inside numbered items. Trim to one sentence each.
- **"Long-Term Memory"** (line ~111): Trailing sentence "Extraction happens automatically..." should be a bullet.
- **"Connected Memory"** (line ~165): Trailing philosophical sentence. Convert to bullet.

### 02-memory-context-provider-slides.md

- **"No Tool Calls Required"** (lines ~109-110, 117): Opening prose and trailing conclusion. Convert to bullets.
- **"Multi-Turn Conversation Example"** (lines ~122-130): Dense prose after each turn heading. Convert to definition list with short definitions.
- **"Inspecting Stored Memories"** (lines ~135-136, 143-144): Opening and trailing prose. Convert to bullets.

### 04-memory-tools-slides.md

- **"Passive Memory"** (lines ~37-39, 48): Opening two-sentence description and trailing conclusion. Convert to bullets.
- **"The Combined Pattern"** (lines ~115-125): Multi-sentence prose after each turn. Shorten to one sentence per turn or use definition list.

### 05-reasoning-memory-slides.md

- **"What a Reasoning Trace Contains"** (line ~60): Trailing sentence after table. Convert to bullet.
- **"Recording Traces"** (line ~73): Trailing multi-sentence explanation. Convert to bullets.
- **"Finding Similar Traces"** (line ~110): Trailing philosophical conclusion. Convert to bullet.
- **"Reasoning Memory in Action"** (lines ~140-143): Both session descriptions are dense paragraphs. Convert to definition list with shorter definitions.

### 06-gds-integration-slides.md

- **"Beyond Simple Lookups"** (line ~46): Trailing conclusion. Convert to bullet.
- **"When GDS Is Not Available"** (lines ~152-153): Two trailing sentences. Convert to bullets.
