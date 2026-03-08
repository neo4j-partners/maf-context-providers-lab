# Slides vs Site Content Review

## Overall Assessment

The slides and site content are well-aligned. The slide order matches the site navigation flow, and the key concepts covered in each lesson are consistently represented in both formats. Below are the specific issues found.

---

## 1. Em-Dash Overuse (`--`)

**ACTION**: FIX ALL

The slides use em-dashes (`--`) heavily throughout. Many can be replaced with colons, periods, or sentence restructuring for cleaner slide text. Here are the worst offenders:

### Section 1

**01-what-is-maf-slides.md**
- Line 83: `"This works well for specific actions, but poorly for background knowledge — the agent may not realize it should ask."` - Use a period or colon.
- Line 93: `"The agent never decides whether to use the provider -- it just receives the context"` - Rewrite as two sentences.
- Line 158: `"**Tools** are reactive -- the agent decides when to call them"` - Use a colon.
- Line 159: `"**Context providers** are proactive -- they inject knowledge on every turn automatically"` - Use a colon.

**03-first-agent-slides.md**
- Line 58: `"No API key or model name in code -- it reads..."` - Use a period.
- Line 178: `"Tools are **reactive** -- the agent must choose to call them"` - Use a colon.
- Line 179: `"the agent often does not realize it should ask"` - Fine, but the surrounding bullets all use `--` creating a pattern of overuse.

### Section 2

**01-what-are-context-providers-slides.md**
- Line 88: `"Tools are **reactive** -- the agent must recognize a tool is relevant and choose to call it."` - Colon or period.
- Line 175: `"**`context.extend_instructions()`** -- Adds text..."` - Use a colon.
- Line 178: `"**`context.extend_messages()`** -- Adds messages..."` - Use a colon.
- Line 228: `"**Tools are reactive** -- the agent must decide to call them"` - Already said this multiple times across slides.

### Section 3

**04-fulltext-provider-slides.md** - 8+ em-dashes, the worst offender:
- Line 76: `"**Term frequency** -- how often..."` - Colon.
- Line 77: `"**Inverse document frequency** -- how rare..."` - Colon.
- Line 78: `"**Document length normalization** -- shorter documents..."` - Colon.
- Lines 100-103: Four consecutive bullet points all using `--`.

**03-graph-enriched-provider-slides.md**
- Line 57: `"The query traverses outward from the matched node — following relationships..."` - Break into two sentences.
- Lines 69-72: Four consecutive bullet points all using `--`.

### Section 4

**01-memory-types-slides.md**
- Line 67: `"**What was said** -- the conversation itself."` - Colon.
- Line 69: `"**What was learned** -- facts and preferences..."` - Colon.
- Line 71: `"**What was tried** -- the reasoning and tool calls..."` - Colon.
- This pattern of `**Bold** -- explanation` appears 15+ times across section 4 slides.

**04-memory-tools-slides.md**
- Line 37: `"**passively** -- it injects relevant memories..."` - Colon.
- The bold-emdash-explanation pattern is used in nearly every bullet.

**Recommendation:** Limit em-dashes to 1-2 per slide maximum. Replace `**Term** -- definition` with `**Term:** definition` throughout. Use periods for sentence breaks.

---

## 2. Flow & Content Match Issues

### 2a. Slides have content not in site

**ACTION**: REMOVE ALL

**02-vector-provider-slides.md** - "Understanding Similarity Scores" table (lines 148-159) with score ranges (0.95-1.0, 0.90-0.95, etc.) does not appear anywhere in the site content. Either add to site or remove from slides for consistency.

**01-what-is-maf-slides.md** - "History" table comparing AutoGen and Semantic Kernel predecessors (lines 35-44) is more detailed in slides than site. The site mentions both but doesn't use a comparison table. Minor, acceptable for presentation format.

### 2b. Site has content not in slides


**3-1-neo4j-context-providers-overview.adoc** - The site discusses `neo4j-graphrag-python`'s knowledge graph construction pipeline (`SimpleKGPipeline` for building KGs from unstructured text). The slides omit this entirely. This is a significant feature mention in the site that presenters may want to reference. Consider adding a brief mention to slides.

**ACTION**: ADD JUST THIS ONE

**3-1-neo4j-context-providers-overview.adoc** - The site has a "Learn More" section with three links (neo4j-graphrag-python GitHub, docs, agent-framework-neo4j GitHub). Slides have no equivalent resources slide. Consider adding a resources/links slide at the end of section 3.

**ACTION**: IGNORE 

**3-2-vector-provider.adoc** - Site mentions `pip install agent-framework-neo4j` setup step. Slides skip this. Should be in the setup slides (02-setup-slides.md) or the overview slides.

**ACTION**: IGNORE

### 2c. Ordering note

The site file numbering is confusing: after 3-2 (vector), the site goes to 3-5 (graph-enriched), then 3-3 (fulltext), then 3-4 (hybrid). The slides use sequential numbering (02, 03, 04, 05) which follows the same flow. The site file naming is misleading but the actual navigation order matches. No fix needed, but worth noting.

**ACTION**: PROPOSE FIX 

---

## 3. Slides That Are Too Prose-Heavy (Not Bullet-Point Enough)

These slides have paragraph text that should be converted to bullet points for better presentation:


**01-what-is-maf-slides.md**
- Line 44: `"Developers migrating from either framework have a clear upgrade path. The core patterns are familiar; the execution model is more structured."` - Convert to bullets.
- Line 50: `"The Microsoft Agent Framework orchestrates a lifecycle around each LLM call, turning a bare model into an agent that can retrieve, reason, and act."` - Too long for a slide. Break into bullets.
- Line 63: `"The core concept in MAF is the **agent**. An agent follows the **ReAct**..."` - Full paragraph. Should be a bullet or two.
**ACTION**: FIX
- 
**01-what-are-context-providers-slides.md (section 2)**
- Lines 37-42: Three full-sentence bullets. Each should be shorter.
- Line 100: `"Context providers **inject relevant knowledge before every LLM call**, regardless of the query."` - Fine as a key statement, but the surrounding text is also prose.
**ACTION**: FIX
- 
**03-graph-enriched-provider-slides.md**
- Lines 55-58: Long paragraph describing the two-step process. Should be bullets.
- Lines 67-72: Five bullet points that are each full sentences. Trim to fragments.
**ACTION**: FIX
- 
**03-memory-context-provider-slides.md**
- Lines 37-43: Opening paragraph is too long for a slide. Break into 3 bullets.
**ACTION**: FIX
- 
**General pattern:** Many slides have a heading followed by a paragraph, then bullets. The paragraph should usually be the first bullet or removed entirely.
**ACTION**: PROPOSE FIX 
---

## 4. Repeated Content Across Slides

The tools vs context providers comparison is explained at least 4 times across different slide decks:
1. `01-what-is-maf-slides.md` (lines 99-107) - Full comparison table
2. `03-first-agent-slides.md` (lines 196-203) - "The Gap: Background Knowledge"
3. `01-what-are-context-providers-slides.md` (lines 86-108) - "The Problem with Tools Alone" + comparison table
4. `04-memory-tools-slides.md` (lines 88-98) - Context Provider vs Memory Tools table
**ACTION**: PROPOSE FIX 


The first two are acceptable (intro + reinforcement). The third repeats the same table from the first. Consider trimming the table in `01-what-are-context-providers-slides.md` since the audience has already seen it, and instead just reference "as you saw earlier."
**ACTION**: FIX

---

## 5. Minor Content Inconsistencies

- **Slide 02-setup-slides.md line 39**: Says "Neo4j Sandbox" but site says "Neo4j Sandbox" with a link. Consistent. OK.
- **ACTION**: IGNORE 

- **Slide 03-first-agent-slides.md line 78**: Shows abbreviated code `return f"Title: {info['title']}\nDirector: {info['director']}..."` while the site shows the full return statement. Acceptable for slides.
- **ACTION**: IGNORE 

- **Slide 01-neo4j-context-providers-overview line 40**: Uses an em-dash `—` (unicode) while all other slides use `--` (double hyphen). Inconsistent em-dash style. Pick one.
**ACTION**: REMOVE EM-DASH and make natural flow sentence 


- **Slide 05-hybrid-provider-slides.md line 120**: Trade-offs table shows "Setup complexity: Most" which is awkward. Consider "Highest" or "Most complex".
**ACTION**: FIX

---

## 6. Summary

| Category | Count | Priority |
|----------|-------|----------|
| Em-dash overuse | ~80+ instances across all slides | High - fix throughout |
| Prose-heavy slides (should be bullets) | ~12 slides | Medium |
| Content in slides but not site | 1 (similarity scores table) | Low |
| Content in site but not slides | 2 (KG pipeline, install step) | Low |
| Repeated content across decks | 1 pattern (tools vs context providers) | Low |
| Minor inconsistencies | 2 | Low |
