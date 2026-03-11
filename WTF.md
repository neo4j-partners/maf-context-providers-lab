# Site Content Issues

## ~~Leftover Tag Markers~~ FIXED

All `# tag::` / `# end::` build artifact markers removed from 9 files (~55 instances).

## ~~Duplicate Run/Execution Code~~ FIXED

Removed duplicate run code blocks from:
- 3-2-vector-provider.adoc
- 3-3-fulltext-provider.adoc
- 3-4-hybrid-provider.adoc
- 4-6-gds-integration.adoc

## Not Changing: Client Pattern

Site lessons intentionally use `OpenAIResponsesClient()` directly for simplicity. Labs use `get_client()` wrapper for Azure/OpenAI flexibility. This is by design.
