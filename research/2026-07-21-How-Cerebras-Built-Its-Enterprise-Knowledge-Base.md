---
title: "How Cerebras Built Its Enterprise Knowledge Base"
source: "https://www.cerebras.ai/blog/how-we-built-our-knowledge-base"
author:
  - "[[Isaac Tai]]"
  - "[[Daniel Kim]]"
  - "[[Mike Gao]]"
published:
created: 2026-07-21
description: "See how Cerebras built an enterprise AI knowledge base that connects Slack, code repositories, documentation, and custom data sources."
tags:
  - "source/web-clip"
type: "source"
status: "unprocessed"
domain:
---
Employees ask our internal knowledge base more than 15,000 questions every day. It's become one of the most widely adopted internal tools at the company since launching 3 months ago. Used by humans, automations and agents.  
  
At Cerebras, our teams work across data center operations, chip design, hardware, training, inference, cloud platform, and more. With hundreds of new employees joining every year, our communication channels were filling up with the same questions:

> *“Where can I find X?”*  
> *“Who is the expert in Y?”*  
> *“What is Z?”*

We built Cerebras Knowledge to help people connect people and systems to useful information.

<svg viewBox="0 0 900 760" role="img" aria-labelledby="fig-001-title fig-001-desc" data-hero-stack=""><title id="fig-001-title">Exploded vertical stack of the internal knowledge base</title> <desc id="fig-001-desc">Sources feed distillation, embeddings, retrieval, fusion, and synthesis layers.</desc><defs><marker id="arrow-001" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0 0 10 5 0 10Z" fill="currentColor"></path></marker></defs><g><path d="M235 104V656"></path><path d="M665 104V656"></path><path d="M450 152V608"></path></g></svg>

### Meeting data where it lives

Finding information inside an organization is hard. The data is scattered across tools, and every quarter or so someone proposes the same brilliant fix: let’s record everything in one platform so that all information is in a single place. The dream of a single source of truth, of course, rarely works in practice.

Information is generated wherever it is convenient and ergonomic: suggested edits in a document, threads in Slack, code references in GitHub, and status metadata in Jira. These platforms are tailor-made for their specific domains, optimized through years of product engineering and analytics. Discussing a pull request in Google Docs would be a terrible experience.

So we set out to design a system that required minimal change to existing behavior. On the data collection side, this meant extracting data from each platform directly.

### Anatomy of a knowledge base

Our knowledge base provides three things:

1. A platform for collecting and storing internal data.
2. A platform for querying that data.
3. A layer that enforces authentication and authorization, with auditing and analytics.

At the core is a single Postgres table that holds embeddings, raw summaries, and metadata from many sources. The system continually ingests data from across the company and maintains a query-ready datastore.

We wanted a data interface that was simple but could work with most forms of data. We also wanted other developers at Cerebras to be able to build custom connectors. The result is deliberately simple: every source, from Slack threads to netlists, lands in the same embeddings table, and anything in that table is immediately queryable through the same interface:

<svg viewBox="0 0 900 500" role="img" aria-labelledby="fig-002-title"><title id="fig-002-title">Many data sources feeding one queryable embeddings table</title> <defs><marker id="arrow-002" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto"><path d="M0 0 10 5 0 10Z" fill="currentColor"></path></marker></defs><g><rect x="48" y="60" width="200" height="44" fill="#fff"></rect><rect x="48" y="126" width="200" height="44" fill="#fff"></rect><rect x="48" y="192" width="200" height="44" fill="#fff"></rect><rect x="48" y="258" width="200" height="44" fill="#fff"></rect><rect x="48" y="324" width="200" height="44" fill="#fff"></rect><rect x="48" y="390" width="200" height="44" fill="#fff"></rect><rect x="396" y="152" width="228" height="190" fill="none" stroke="currentColor"></rect><rect x="700" y="210" width="160" height="74" fill="none" stroke="currentColor"></rect><path d="M248 82H322M248 148H322M248 214H322M248 280H322M248 346H322M248 412H322"></path><path d="M322 82V412"></path><path marker-end="url(#arrow-002)" d="M322 247H388"></path><path marker-end="url(#arrow-002)" d="M624 247H692"></path><path d="M396 200H624"></path></g><g><text x="68" y="86">SLACK</text> <text x="68" y="152">WIKI / CONFLUENCE</text> <text x="68" y="218">CODE REPOS</text> <text x="68" y="284">NETLISTS</text> <text x="68" y="350">PRM DOCS</text> <text x="68" y="416">CUSTOM DATABASES</text> <text x="420" y="184">EMBEDDINGS</text> <text x="780" y="247" text-anchor="middle" dominant-baseline="middle">QUERY</text> </g><g><text x="420" y="234">DOCUMENT</text> <text x="420" y="264">EMBEDDING</text> <text x="420" y="294">METADATA</text> <text x="420" y="324">SOURCE + TIMESTAMPS</text> <text x="700" y="196">MCP - WEB UI - AGENTS</text> <text x="396" y="372">ONE EMBEDDINGS TABLE</text> <text x="48" y="468">ONE CONNECTOR PER SOURCE</text></g></svg>

Each data source defines what the data is, how to connect to it, and how often it should be fetched. Each resulting embedding row follows the same interface regardless of whether it came from Slack, a code repository, a document system, or a custom database.

### Slack

Slack was the most important data source we needed to design for. It is where the most up-to-date engineering discussions happen across the company.

<svg viewBox="0 0 900 430" role="img" aria-labelledby="fig-003-title"><title id="fig-003-title">Slack event flow from Socket Mode through distillation and embedding</title> <defs><marker id="arrow-003" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto"><path d="M0 0 10 5 0 10Z" fill="currentColor"></path></marker></defs><g><rect x="38" y="172" width="132" height="58" fill="#fff"></rect><polygon points="232,201 282,157 332,201 282,245" fill="none" stroke="currentColor"></polygon><rect x="398" y="76" width="154" height="58" fill="#fff"></rect><rect x="386" y="172" width="178" height="58" fill="#fff"></rect><rect x="386" y="268" width="178" height="58" fill="#fff"></rect><rect x="636" y="172" width="152" height="58" fill="none" stroke="currentColor"></rect><rect x="646" y="64" width="132" height="52" fill="#fff"></rect><rect x="646" y="274" width="132" height="52" fill="#fff"></rect><rect x="646" y="350" width="132" height="52" fill="#fff"></rect><path marker-end="url(#arrow-003)" d="M170 201H224"></path><path marker-end="url(#arrow-003)" d="M282 157V105H390"></path><path marker-end="url(#arrow-003)" d="M332 201H378"></path><path marker-end="url(#arrow-003)" d="M475 230V260"></path><path marker-end="url(#arrow-003)" d="M564 297H598V201H628"></path><path marker-end="url(#arrow-003)" d="M712 172V124"></path><path marker-end="url(#arrow-003)" d="M712 230V266"></path><path marker-end="url(#arrow-003)" d="M736 230V342"></path></g><g text-anchor="middle" dominant-baseline="middle"><text x="104" y="201">SOCKET EVENT</text> <text x="282" y="201">ROUTE</text> <text x="475" y="105">BOT REPLY</text> <text x="475" y="201">REINGEST_THREAD</text> <text x="475" y="297">UPSERT THREAD</text> <text x="712" y="201">SYNC_WORKER</text> <text x="712" y="90">DISTILL</text> <text x="712" y="300">THREAD VECTOR</text> <text x="712" y="376">BURST VECTORS</text> </g><g><text x="376" y="48">@MENTION / DM</text> <text x="368" y="156">TRACKED CHANNEL</text> <text x="410" y="350">RESET WATERMARKS</text></g></svg>

### How we process unstructured Slack conversations

We initially tested whether simple embeddings over raw text performed well enough. We quickly realized that vector search alone was insufficient for matching all relevant data.

Slack messages present several challenges:

- Information density varies enormously: “hey yeah sure mike” and a detailed kernel explanation are both messages.
- Message lengths vary, and shorter messages frequently beat longer, more detailed messages in cosine similarity.
- The meaning of a message often depends on the surrounding conversation.

We needed a hybrid approach. We built Slack ingestion so every thread is retrievable through several search techniques at once, where each technique makes up for the weaknesses of the others:

- **Full-text search** catches the exact tokens that embeddings blur together: error strings, flag names, host names. When an engineer pastes a literal error message, an exact lexical match is almost always the best evidence, and no amount of semantic similarity should outrank it.
- **Embedding search** catches paraphrase. The person asking “restore hangs after manifest load” and the person who answered “checkpoint stalls on the NFS mount” may never share vocabulary. Vector similarity is what connects a question to an answer written in different words.(1)
- **Inverse document frequency** separates signal from filler. A short message built around rare tokens, such as an obscure config flag, deserves to rank. “sounds good, thanks!” sits close to many queries in embedding space but scores near zero once term rarity is taken into account.
- **Age decay** encodes that Slack answers expire. Two threads can answer the same question, and the one from six months ago may describe infrastructure that no longer exists. When relevance is otherwise equal, the newer thread wins.

SEARCH / SLACK CANDIDATES FULL-TEXT

QUERY

“restore hangs after manifest load”

1. 2W AGO
	**NO SHARED TOKENS** **PARAPHRASE MATCH** **CKPT\_PREFETCH: RARE** **RECENT WINS TIE**
	Thread
	Checkpoint stalls on the NFS mount — set `CKPT_PREFETCH=4`.
2. 1D AGO
	**EXACT TOKENS** **ERR\_MANIFEST\_TIMEOUT: RARE**
	Message
	`ERR_MANIFEST_TIMEOUT`: restore hangs after manifest load.
3. 3H AGO
	**FALSE NEIGHBOR** **NO RARE TOKENS**
	Message
	sounds good, thanks! will try that
4. 8MO AGO
	**ALSO MATCHES** **8 MO: DECAYED**
	Thread
	restore hangs after manifest load → use `LEGACY_FETCHER=1`.

No single scorer is trusted on its own. Each technique produces its own ranked view of the same corpus, and those views are fused at query time (see [Reranking](https://www.cerebras.ai/blog/how-we-built-our-knowledge-base#reranking)).

### Socket Mode

To collect data in real time, we installed a Slack bot into our workspace and ran it in Socket Mode. Slack pushes every message event to us over a persistent WebSocket, so we get real-time updates without polling the Web API and burning through its rate limits.

When an event arrives, we immediately acknowledge it, deduplicate it using the stable event ID, and mark the message for the ingest consumer.

The ingest consumer does not save a new message in isolation. It resolves the thread that the message belongs to and re-fetches the entire conversation, including the parent and every reply, from the Slack API. It then writes the whole thread back as one row. A reply to an existing thread therefore re-pulls the parent and all siblings, so the stored content, participant list, and last-activity timestamp always reflect the complete conversation.

Every Slack channel in our system has its own data source. This provides fine-grained tuning for data freshness. A team may choose to ingest a busy incident channel more frequently, for example.

### Threads and messages

Raw Slack text is keyword-searchable as soon as it lands because we maintain a Postgres full-text (GIN) index over the raw content. To enable useful vector search, however, we do some additional processing.(8)

During distillation, an LLM extracts structured data from the full thread:

- A one-line question that an engineer would actually search for.
- A short summary.
- The resolution.
- The systems and code references mentioned.

#CKPT-SUPPORT / THREAD\_8F42 FULL THREAD INPUT

1. 09:14
	**QUESTION**
	Maya
	Restore stalls after manifest load on the larger cluster. Small runs are fine.
2. 09:17
	**SUMMARY**
	Owen
	I can reproduce with 128 shards. The logs stop before cache warmup.
3. 09:18
	**CONTEXT**
	Sam
	My laptop also stalls when it sees Monday.
4. 09:21
	**RESOLUTION**
	Maya
	Setting `CKPT_PREFETCH=4` makes it complete. The default is too high for the NFS mount.

{

"code\_refs" \["CKPT\_PREFETCH"\]

}

We embed these data points and write them into the shared embeddings table. The original transcript is not embedded directly. In our experiments, accuracy increased significantly when the thread was normalized into a consistent format.(7,9) The additional metadata also gives the semantic match more useful signal.

### Bursting

At this point Slack search was good, but we kept encountering the same problem: important messages inside long threads were not always represented in the thread-level summary.

To boost the signal from individual messages, we use bursting. A burst is a run of consecutive messages from the same author. We embed individual bursts with the thread topic prepended as context(2) because sometimes the answer lives in one tangent message whose vocabulary never makes it into the thread summary. Burst embeddings make that message findable on its own.

To prevent low-signal data from reaching the database, each burst is scored against a weighted combination of signals and must clear a threshold before it is embedded:

- It contains a relatively rare token across the corpus, with IDF of at least 4.0.
- The combined burst is at least 200 characters.
- One or more messages in the burst contain reactions, providing a social boost.

After distillation, qualifying bursts are embedded and stored in the embeddings table alongside the thread-level record.

### Code repositories

Initially we debated whether embedding code repositories was necessary. With the rise of Claude Code and other command-line tools, creating code embeddings felt counterintuitive when it seemed like “grep is all you need.” After talking with others in the industry and reading Cursor’s findings on semantic search in large codebases, we decided to try.

We have many internal repositories, some larger than 40 GB. Our main concern was how to keep them current efficiently.

### Using CocoIndex to maintain code embeddings

After several experiments, we landed on CocoIndex, an open-source document embedding framework that specializes in vectorizing codebases.

For each repository, we split the code using language-specific regex boundaries ordered from coarse to fine. The splitter tries higher-level boundaries, such as classes, first. If a resulting chunk is still too large, it falls back to method boundaries and then smaller blocks. We embed the resulting chunks and write the vectors to Postgres. A single file may generate multiple embeddings at different levels of specificity, such as file-level and function-level records.

CocoIndex tracks synchronization metadata in Postgres. On each commit, it re-embeds and re-exports only the changed code chunks instead of recomputing the whole repository. This worked especially well for us because the synchronization state and embedding store live in the same database.

As the number of codebases grew, we moved repository onboarding into configuration files that teams can submit themselves, including allowlists and denylists at the file-path level.

### Custom data sources

Some teams already had their own databases and did not want to move data into Slack or a document system just to participate in the knowledge base. They wanted the same query surface over their existing tables.

To support this, we treat custom sources as plugin scripts. A team opens a pull request with a small Python module that knows how to read from its system and emit rows shaped like our embeddings table, plus a matching data source entry.

As long as the script writes into the shared database using the same schema as every other embedding row, the rest of the stack works unchanged. The data becomes queryable alongside Slack, code, and documents, with no special handling elsewhere in the system.

### Planning and tool fan-out

For every query, we first run a short planning pass where an LLM decides which tools and data sources are likely to matter. The main tools:

- subsystem\_index: per-file LLM summaries.
- search: the unified vector pipeline across Slack, wiki, code, and other indexed sources, merged and reranked internally.
- search\_slack: direct Slack retrieval.
- search\_code: ripgrep over source repositories.
- recent\_prs: recent pull requests relevant to the question.
- who\_knows: people with demonstrated expertise on a topic.

The planner works over a compact description of what we have indexed: which projects exist, which sources are available in each project, and what each source is good at answering. Given the user’s query and active scope, it emits tool selections that the executor fans out in parallel, normalizes into a common evidence format, and passes to a final synthesis LLM.(4)

<svg viewBox="0 0 900 460" role="img" aria-labelledby="fig-007-title"><title id="fig-007-title">Planner, parallel tool execution, evidence normalization, and synthesis</title> <defs><marker id="arrow-007" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto"><path d="M0 0 10 5 0 10Z" fill="currentColor"></path></marker></defs><g><rect x="58" y="188" width="142" height="64" fill="#fff"></rect><rect x="274" y="188" width="142" height="64" fill="none" stroke="currentColor"></rect><rect x="492" y="48" width="150" height="52" fill="#fff"></rect><rect x="492" y="122" width="150" height="52" fill="#fff"></rect><rect x="492" y="196" width="150" height="52" fill="#fff"></rect><rect x="492" y="270" width="150" height="52" fill="#fff"></rect><rect x="492" y="344" width="150" height="52" fill="#fff"></rect><rect x="704" y="142" width="148" height="64" fill="none" stroke="currentColor"></rect><rect x="704" y="264" width="148" height="64" fill="none" stroke="currentColor"></rect><path marker-end="url(#arrow-007)" d="M200 220H266"></path><path marker-end="url(#arrow-007)" d="M416 220H458V74H484"></path><path marker-end="url(#arrow-007)" d="M416 220H458V148H484"></path><path marker-end="url(#arrow-007)" d="M416 220H484"></path><path marker-end="url(#arrow-007)" d="M416 220H458V296H484"></path><path marker-end="url(#arrow-007)" d="M416 220H458V370H484"></path><path marker-end="url(#arrow-007)" d="M642 74H674V174H696"></path><path marker-end="url(#arrow-007)" d="M642 148H696"></path><path marker-end="url(#arrow-007)" d="M642 222H674V174H696"></path><path marker-end="url(#arrow-007)" d="M642 296H674V296H696"></path><path marker-end="url(#arrow-007)" d="M642 370H674V296H696"></path><path marker-end="url(#arrow-007)" d="M778 206V256"></path></g><g text-anchor="middle" dominant-baseline="middle"><text x="129" y="220">QUESTION</text> <text x="345" y="220">PLANNER</text> <text x="567" y="74">SEARCH</text> <text x="567" y="148">SEARCH_SLACK</text> <text x="567" y="222">SEARCH_CODE</text> <text x="567" y="296">RECENT_PRS</text> <text x="567" y="370">WHO_KNOWS</text> <text x="778" y="166">EVIDENCE</text> <text x="778" y="288">SYNTHESIS</text> </g><g text-anchor="middle" dominant-baseline="middle"><text x="778" y="190">NORMALIZED ROWS</text> <text x="778" y="312">ANSWER + CITATIONS</text></g></svg>

### Reranking

A document can surface near the top simply because it shares vocabulary with the query while answering a different question. Before reranking, we combine the retrievers’ incompatible result lists with reciprocal rank fusion, or RRF. For every document, we add weight / (60 + rank) for each list in which it appears, with a default weight of 1.0 and a smoothing constant of 60.

The smoothing constant makes consensus matter more than a single strong vote: a document that shows up near the top across several retrievers can beat one that ranks first in only one of them. We then merge duplicate chunks back to one source, cap how many results each file can contribute, and end up with a more diverse top twenty.

We send the original query and those candidates to a small reranker model. It gives each document a score from zero to ten, and we keep the top ten.(6)

Once the ranking is final, we add context back to the winners. For example, if we match a wiki section we pull in the two neighboring sections so the heading, preconditions, and caveats that chunking split apart aren’t lost. This gives readers a complete snippet instead of a lonely paragraph that’s missing important context.

So the output of search is a rich packet of evidence: results fused from different retrievers, deduplicated at the source level, reranked against the actual question, and only then expanded with surrounding context.

### MCP

In the MCP integration, we expose retrieval building blocks as direct tools instead of hiding them behind one “answer this question” endpoint. These tools are intentionally simple and as LLM-free as possible so clients can query them quickly and cheaply.(5)

Each MCP tool corresponds to one underlying retrieval primitive, such as search\_slack, search\_code, search, or who\_knows. Tool inputs and outputs are narrow, structured, and stable, making them easy to call from any client or agent without embedding additional orchestration logic inside the tool itself.

Most tools run one query pipeline, such as vector search, lexical search, or ripgrep, apply lightweight scoring heuristics, and return raw evidence rows.

Claude Code, or any MCP-compatible agent, becomes the orchestration engine. It decides which tools to call, in what order, and how to assemble the results into a final answer or code edit. The retrieval layer itself does not depend on those LLM decisions in order to serve requests.

### Web UI

In the web UI, the same tools exist, but they are connected to a complete query pipeline that runs end to end for every user question. The UI agent owns the planner and executor steps.

**Planner:** A lightweight LLM pass inspects the query and active project, then chooses which retrieval tools to invoke, such as search, search\_slack, and subsystem\_index.

**Executor:** The system fans those tool calls out in parallel, gathers the results, and normalizes them into a shared evidence schema with scores, recency, and source hints.

**Synthesis:** A final LLM pass takes the typed evidence bundle and original question, then produces the answer shown in the UI, including citations, caveats, and cross-source synthesis.

From the user’s perspective, the web UI is simply “ask a question and get an answer.” Under the hood, it runs the same planner → executor → synthesizer pattern that MCP clients can recreate explicitly.

<svg viewBox="0 0 760 390" role="img" aria-labelledby="fig-009-title"><title id="fig-009-title">MCP exposes retrieval primitives while the web UI runs the complete agent pipeline</title> <defs><marker id="arrow-009" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto"><path d="M0 0 10 5 0 10Z" fill="currentColor"></path></marker></defs><g><rect x="50" y="52" width="286" height="276" fill="#fff"></rect><rect x="424" y="52" width="286" height="276" fill="none" stroke="currentColor"></rect><rect x="84" y="104" width="218" height="42" fill="#fff"></rect><rect x="84" y="164" width="218" height="42" fill="#fff"></rect><rect x="84" y="224" width="218" height="42" fill="#fff"></rect><rect x="458" y="104" width="218" height="42" fill="#fff"></rect><rect x="458" y="164" width="218" height="42" fill="#fff"></rect><rect x="458" y="224" width="218" height="42" fill="#fff"></rect><path marker-end="url(#arrow-009)" d="M567 146V156"></path><path marker-end="url(#arrow-009)" d="M567 206V216"></path></g><g text-anchor="middle" dominant-baseline="middle"><text x="193" y="80">MCP CLIENT</text> <text x="567" y="80">WEB UI</text> <text x="193" y="125">DIRECT TOOL CALLS</text> <text x="193" y="185">RAW EVIDENCE ROWS</text> <text x="193" y="245">CLIENT ORCHESTRATES</text> <text x="567" y="125">PLANNER</text> <text x="567" y="185">EXECUTOR</text> <text x="567" y="245">SYNTHESIS</text></g></svg>

### Organization

As the corpus grew, “search everything everywhere” rapidly stopped being useful. Engineers on compiler teams did not want infrastructure runbooks in their results, and vice versa. Projects are how we make search relevant by default.

### Projects and scoped search

We introduced projects as the primary way to organize the workspace that a query runs over. A project is a named bundle of data sources: specific Slack channels, code repositories, internal databases, and document spaces relevant to a team or initiative.

Projects are intentionally lightweight. The same data source, such as a shared incidents channel or central platform repository, can be referenced by multiple projects instead of being duplicated.

<svg viewBox="0 0 760 420" role="img" aria-labelledby="fig-010-title"><title id="fig-010-title">Projects reference shared data sources without duplicating them</title> <defs><marker id="arrow-010" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto"><path d="M0 0 10 5 0 10Z" fill="currentColor"></path></marker></defs><g><rect x="56" y="76" width="214" height="86" fill="none" stroke="currentColor"></rect><rect x="56" y="258" width="214" height="86" fill="none" stroke="currentColor"></rect><rect x="476" y="36" width="214" height="54" fill="#fff"></rect><rect x="476" y="112" width="214" height="54" fill="#fff"></rect><rect x="476" y="188" width="214" height="54" fill="#fff"></rect><rect x="476" y="264" width="214" height="54" fill="#fff"></rect><rect x="476" y="340" width="214" height="54" fill="#fff"></rect><path marker-end="url(#arrow-010)" d="M270 108H404V63H468"></path><path marker-end="url(#arrow-010)" d="M270 120H404V139H468"></path><path marker-end="url(#arrow-010)" d="M270 132H404V215H468"></path><path marker-end="url(#arrow-010)" d="M270 290H404V215H468"></path><path marker-end="url(#arrow-010)" d="M270 302H404V291H468"></path><path marker-end="url(#arrow-010)" d="M270 314H404V367H468"></path></g><g text-anchor="middle" dominant-baseline="middle"><text x="163" y="108">COMPILER PROJECT</text> <text x="163" y="290">PLATFORM PROJECT</text> <text x="583" y="63">COMPILER SLACK</text> <text x="583" y="139">MONOLITH REPO</text> <text x="583" y="215">SHARED INCIDENTS</text> <text x="583" y="291">PLATFORM REPO</text> <text x="583" y="367">CLOUD RUNBOOKS</text> </g><g text-anchor="middle" dominant-baseline="middle"><text x="163" y="132">DEFAULT QUERY SCOPE</text> <text x="163" y="314">DEFAULT QUERY SCOPE</text></g></svg>

### Onboarding and defaults

During onboarding, users are prompted to select or create a default project that matches how they work, such as ML training infrastructure, Compiler, or Data Center Operations.

That default project is stored on the user profile and scopes queries automatically. A new engineer gets high-signal answers without first having to learn which Slack channels, repositories, or document spaces matter.

### Final Thoughts

In the end, the knowledge base works because it meets people where the information already lives, instead of forcing everything into one rigid system. By combining various search techniques, we can surface evidence quickly. The result is a search experience that stays flexible enough for real company data, but structured enough to remain useful as Cerebras keeps growing.

REFERENCES

1. Malkov and Yashunin, [*Efficient and Robust Approximate Nearest Neighbor Search Using Hierarchical Navigable Small World Graphs*](https://arxiv.org/abs/1603.09320), arXiv:1603.09320 / IEEE TPAMI 2018.
2. Anthropic, [*Introducing Contextual Retrieval*](https://www.anthropic.com/news/contextual-retrieval), 2024.
3. Cormack, Clarke, and Büttcher, [*Reciprocal Rank Fusion Outperforms Condorcet and Individual Rank Learning Methods*](https://dl.acm.org/doi/10.1145/1571941.1572114), SIGIR 2009.
4. Li et al., [*Search-o1: Agentic Search-Enhanced Large Reasoning Models*](https://arxiv.org/abs/2501.05366), arXiv:2501.05366, 2025.
5. Anthropic, [*Code Execution with MCP*](https://www.anthropic.com/engineering/code-execution-with-mcp), 2025.
6. Liu et al., [*Lost in the Middle: How Language Models Use Long Contexts*](https://arxiv.org/abs/2307.03172), arXiv:2307.03172, 2023.
7. Anthropic, [*Use XML Tags*](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/use-xml-tags).
8. Salesforce/Slack Engineering, *How Slack AI Processes Billions of Messages*.
9. Improving Agents, *Best Nested Data Format*.
10. Cursor, [*Improving Agent with Semantic Search*](https://cursor.com/blog/semsearch), 2025.

---
*Clipped from [cerebras.ai](https://www.cerebras.ai/blog/how-we-built-our-knowledge-base) on 2026-07-21T13:56:39-04:00*
