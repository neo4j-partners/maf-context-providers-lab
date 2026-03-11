# Site Content Issues

## Leftover Tag Markers

Build artifact tags (`# tag::`, `# end::`) left in code blocks across 9 files. Total: ~55 instances.

### 1-3-first-agent.adoc
- Lines ~111, 113, 121: `# end::agent[]`, `# tag::run[]`, `# end::run[]` in collapsible block

### 2-2-simple-context-provider.adoc
- Lines ~286, 288, 307: tag markers in collapsible block

### 3-2-vector-provider.adoc
- Lines ~101, 103, 110: tag markers in standalone code block
- Lines ~197, 199, 206: tag markers in collapsible block

### 3-3-fulltext-provider.adoc
- Lines ~189, 191, 198: tag markers in collapsible block

### 3-4-hybrid-provider.adoc
- Lines ~86, 88, 95: tag markers in standalone code block
- Lines ~185, 187, 194: tag markers in collapsible block

### 3-5-graph-enriched-provider.adoc
- Lines ~204, 206, 213: tag markers in collapsible block

### 4-2-memory-context-provider.adoc
- Lines ~66, 68, 83, 85, 96, 98, 110: tag markers in first code section
- Lines ~252, 254, 269, 271, 282, 284, 296: tag markers in collapsible block

### 4-4-memory-tools.adoc
- Lines ~56, 58, 80, 82, 95, 97, 122: tag markers in first code section
- Lines ~319, 321, 343, 345, 358, 360, 385: tag markers in collapsible block

### 4-6-gds-integration.adoc
- Lines ~92, 94, 101: tag markers in collapsible block

## Duplicate Run/Execution Code

These files show agent run code twice: once in the lesson body and again in the collapsible complete code block. The lesson body versions use `async def main()` / `asyncio.run(main())` instead of the simpler notebook-style `async with` block.

- **3-2-vector-provider.adoc**: lines ~84-112 vs ~181-208
- **3-3-fulltext-provider.adoc**: lines ~92-116 vs ~173-200
- **3-4-hybrid-provider.adoc**: lines ~72-97 vs ~171-196

## Inconsistent Client Pattern

Some files use `OpenAIResponsesClient()` directly while the labs use `get_client()` from `llm_provider`. Files to check:

- 3-2-vector-provider.adoc
- 3-3-fulltext-provider.adoc
- 3-4-hybrid-provider.adoc
- 3-5-graph-enriched-provider.adoc (partially fixed)
- 4-2-memory-context-provider.adoc
- 4-4-memory-tools.adoc
