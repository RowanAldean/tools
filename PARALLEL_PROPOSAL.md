# Parallel tools proposal

This fork replaces the deprecated Exa module with `parallel_search` and `parallel_extract`.
The default search mode is Parallel Fast. Both tools connect to the hosted Search MCP,
with no key needed for light use and optional `PARALLEL_API_KEY` for higher limits.

This is a breaking provider replacement. The old Exa parameter surface is not recreated.
Review [the migration notes](docs/parallel-migration.md) before moving an existing application.
The exact migration boundary is the Exa module and its examples, configuration and tests.
Other providers and tools remain unchanged.

| Call site | Consumed behavior | Parallel route | Decision |
| --- | --- | --- | --- |
| Exa search module | Agent web search | MCP web_search with Fast mode | migrate to new objective/query contract |
| Exa contents module | Page content retrieval | MCP web_fetch with optional full content | migrate to explicit extract contract |
| Provider-specific crawl, filters and summaries | Broad old optional API surface | No equivalent claimed | not exposed; existing callers must assess migration before adoption |

The tools repository's contribution policy rejects new tools. This is a discussion fork,
not an accepted upstream integration. Maintainers can choose an exception or a standalone
package. The higher-priority harness and CLI default replacement is here:
https://github.com/RowanAldean/harness-sdk/tree/agent-tasks/parallel-default

Published developer value evidence and its limits are documented in the harness proposal.
No universal benchmark claim or upstream agreement is implied by this fork.
