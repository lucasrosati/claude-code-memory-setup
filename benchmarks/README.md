# Token metrics: evidence audit and reproduction protocol

Audit date: 2026-10-07. Public `main` inspected at
[`a89c275e139d25deb01529e6c7f1954844164ff7`](https://github.com/lucasrosati/claude-code-memory-setup/tree/a89c275e139d25deb01529e6c7f1954844164ff7).
Scope: tracked files, full available Git history, issue #12 and its comments.
No private project, vault, provider usage records, or paid model execution was available.

## Where the claims came from

| Claim | Earliest public evidence found | What can be reproduced now |
| --- | --- | --- |
| 71.5x fewer tokens **per session** | Initial README, [`ad8e4ef`](https://github.com/lucasrosati/claude-code-memory-setup/commit/ad8e4ef182cd5556579f9e45d8b7cedaa1d81b59), 2026-04-12 | Presence of the claim in history; no session usage ledger |
| ~20,000 tokens reading ~40 files versus ~280 querying a graph | Full PT-BR guide, [`884ee58`](https://github.com/lucasrosati/claude-code-memory-setup/commit/884ee58889d7e15745330e4cdca22242710b1e5b), 2026-04-12 | Arithmetic only: 20,000 / 280 = 71.428571…; approximately 98.6% less context under those assumptions |
| 499x per query; React + Supabase, 126 TypeScript files | Same full guide, `884ee58` | Claim and accompanying inventory only; no baseline/graph token counts, exact question or answer, tokenizer, model, or raw records |

English translation arrived in `09ddc0f` on the same day; `a444d64` made it the main README. Later README edits inspected do not add a measurement protocol. The proximity of 71.5x to 20,000/280 suggests a connection, but the history does not prove the derivation. Rounded inputs cannot justify the extra precision. The 40-file illustration and 126-file report are different scenarios and must not be combined.

The project source snapshot, graph, retrieval output and transcripts behind the inventory are not published here. All inventory counts remain author-reported. This is an absence-of-public-evidence finding, not evidence that the claims are false.

## Independent review is not independent token validation

[Issue #12](https://github.com/lucasrosati/claude-code-memory-setup/issues/12), opened 2026-07-20, reports 82/100 and offers a right of reply; it had no comments at audit time. Its body uses both hands-on language and an explicit repo-surface/not-hands-on description. The [Hlido passport](https://hlido.eu/passport/lucasrosati-claude-code-memory-setup/) retrieved on 2026-10-07 dates the review to 2026-07-16 and lists repository checks, not token measurements. That date differs from the September 24 date supplied with this audit request. The [review URL](https://hlido.eu/reviews/lucasrosati-claude-code-memory-setup/) could not be retrieved during this audit, so its exact current wording/publication date was not independently verified. Neither accessible source supplies reproduction data for 71.5x or 499x. Do not present the score as validation of either ratio.

## Measurement boundaries

**Retrieval payload:** count the exact text returned to the agent (including file names, wrappers and truncation) using a named, versioned tokenizer or provider count endpoint. A small graph query output is not the size of the entire graph. Bytes, characters and file counts are not tokens. This measurement excludes model reasoning, tool schemas, prompts and repeated context; label it a payload comparison, never session savings.

**Query:** include every model request and tool step needed to answer one fixed question, including retries, graph retrieval and fallback source reads. Report input and output separately. Compare correct answers at equivalent completeness; a shorter but incorrect answer is a failed task, not a saving.

**Session:** sum usage over all requests from a clean start through the identical ordered task list and final save. Include instructions, vault reads, conversation history resent to the model, graph queries, source edits, retries and save operations. Count each actual model request once. Never infer this total from a retrieval payload ratio.

Report initial graph/vault construction and incremental updates separately, including any LLM calls, CPU time and elapsed time. AST-only extraction can avoid LLM generation calls; reading its output still consumes model context. Semantic extraction can cost tokens. For N sessions, report both steady-state usage and memory-arm usage plus build/update tokens amortized over an explicitly stated N. Physical token reduction is not dollar reduction: cached inputs, model rates, output tokens and subscription billing differ.

## Reproducible paired benchmark (requires real data)

1. Choose a public fixture repository and pin its full commit SHA. Publish its file inclusion/exclusion list, graph/vault snapshots and SHA256 hashes. Pin Python, Graphify, Claude Code, model identifier, tokenizer, OS and every extraction/query command with flags. Save the graph before querying. Capture actual commands rather than assuming a CLI version supports the guide's commands.
2. Freeze `tasks.json` before running either arm. Each entry must contain an ID, verbatim prompt, expected facts or patch/test acceptance criteria, permitted tools, maximum steps and timeout. Use at least structural, behavioral and editing tasks; include a task needing source fallback. Example fixed prompt: “Which functions call X, in which files?” Replace X with a real symbol and publish the source-grounded expected list. Have a reviewer score correctness against that list, blind to the arm where possible.
3. Baseline arm: source navigation with normal search/read tools, no generated graph or vault. Memory arm: same source and tools plus the pinned graph and vault. Keep model, prompts, limits and unrelated instructions identical. Publish the differing navigation instructions. Do not force baseline to read every file unless explicitly studying that artificial baseline; separately report whole-codebase reading as a stress case.
4. Run each task in a fresh isolated session for the query experiment. Run the full ordered list in fresh isolated sessions for the separate session experiment. Reset history and workspace changes between paired runs, preserve identical starting source, and alternate arm order over at least five paired repetitions. State random seed/model sampling settings and cache state; run cold and warm cache separately. Do not quietly exclude failures/timeouts; report success rate and failed-run usage separately.
5. Preserve request/response logs, tool outputs and provider usage objects with request IDs. Record build/update usage in a separate ledger. Normalize each actual model request to the schema below, without summing duplicate streaming events or snapshots. Document the provider/version-specific mapping. If `input_tokens` already includes cache reads/writes, subtract them before filling `input_uncached`; if it excludes them, retain it. Unknown or missing counts are **missing data**, never zeros. Zero means measured zero. Keep raw usage for auditing.
6. Summarize each ledger with the command below. Publish per-pair results, median and range across repetitions, sample size, correctness scores, payload counts and build/update totals. Compare matched successful pairs but also publish all failures and their usage. Do not pool query and session scopes or average ratios across unrelated tasks. A session ledger may include the same requests as a query ledger for a separate analysis, but those analyses must never be added together.

Normalized JSONL row (one model request): `scope` (`query`/`session`), `pair` (task/repetition or session/repetition ID), `arm` (`baseline`/`memory`), `request_id`, and `usage` containing exactly four **disjoint** nonnegative integer fields: `input_uncached`, `input_cache_read`, `input_cache_write`, `output`. Logs remain responsible for proving completeness, correctness and provenance; the summarizer only validates pairing, basic counts and duplicate IDs within an arm/scope.

```bash
# Offline plumbing check: invented counts, NOT project benchmark results
python3 benchmarks/summarize.py benchmarks/example.synthetic.jsonl
# Real captured data, once available
python3 benchmarks/summarize.py /path/to/normalized-usage.jsonl > /path/to/results.json
```

The synthetic example yields 140 versus 70 total tokens (2x, 50% reduction) solely to verify arithmetic. It does not invoke Graphify or a model and provides no evidence for this project's savings. The script reports `baseline / memory` and `100 * (1 - memory / baseline)`; undefined ratios are null. It retains cache categories so cost can be calculated separately with dated provider prices.

**Current result:** no historical token-saving ratio is reproducible from the published artifacts. The arithmetic illustration is reproducible; empirical query and session savings require the inputs and captures above. No paid runs have been performed and no replacement performance numbers are claimed.
