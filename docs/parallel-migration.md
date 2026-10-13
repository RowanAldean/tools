# Parallel search and extraction

This proposal replaces the deprecated Exa module with Parallel tools. It is a breaking
provider replacement, not an alias for the old Exa API. Existing imports and saved tool
calls must migrate to `strands_tools.parallel.parallel_search` and `parallel_extract`.

Search accepts an objective, exactly three keyword queries, and a stable conversation ID.
Extract accepts 1-20 HTTP(S) URLs, the same conversation ID, an optional focused objective,
and a full-content flag. Both return the standard Strands status/content envelope. The
JSON content contains ranked Parallel results, warnings and usage, and extraction preserves
per-URL errors. Usage counts are not dollar amounts or relevance scores.

No key is needed for light use. `PARALLEL_API_KEY` enables higher limits using Bearer
authentication. Anonymous searches use Fast mode; authenticated searches also pin Fast.
Queries and fetched URLs go to Parallel under https://parallel.ai/privacy-policy.

The old provider's category indexes, score fields, generated per-page summaries, structured
summary schemas, crawl controls, subpages, moderation settings and date-range filters are
not claimed to be equivalent. They are not exposed by these new tools. Applications that
need them require a separate design before migrating. Other providers in this repository
remain unchanged.

The tools repository currently rejects new tool additions. This fork is a concrete
maintainer discussion proposal. An accepted release may instead need a standalone
community package and a catalog entry, or an agreed exception from the Strands team.
