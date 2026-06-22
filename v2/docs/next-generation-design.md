# Next-Generation Review Checklists — Design Decisions

Status: **Draft / living document**
Last updated: 2026-06-22

This document captures the design decisions for evolving the Azure Review Checklists
project beyond the macro-enabled Excel spreadsheet, leveraging the existing structured
recommendation corpus (`v2/recos/**`) and modern tooling including LLMs.

It is a decision log, not an implementation spec. Decisions are revisited as we learn more.

---

## 1. Context & motivation

### Where the project stands today

- **v1** — monolithic `checklists/*.json`, imported into a macro-enabled Excel
  spreadsheet (VBA + VBA-JSON). Translated to several languages via Azure Translator.
  Azure Resource Graph (ARG) queries run with the **user's own credentials**.
  Azure Monitor workbooks render ARG results dynamically.
- **v2 (in progress)** — one structured file per recommendation under
  `v2/recos/Services` and `v2/recos/Practices` (~2000 files), sourced from APRL and
  WAF service guides, with embedded ARG queries, GUID labels, severity, and WAF pillar
  metadata. Consolidated by GitHub Actions (`get_aprl`, `get_waf_sg`, `autotag`, etc.).
- **web (prototype)** — Flask + MySQL on Azure Container Instances, `filldb` /
  `fillgraphdb` init containers; managed identity on the roadmap.

### Problems with the current macro spreadsheet

- Macro-enabled (`.xlsm`) files are restricted in many organizations for security
  reasons; VBA also does not work on Excel for Mac.
- Hard to collaborate / version control review state.

### Core constraint to preserve

The current model requires **no additional permissions**: ARG queries run with the
reviewer's own read-only access to the subscription(s). Any successor should preserve
this "no extra grants" property for the baseline experience.

### Current-state caveat — Azure AI endpoints decommissioned

The Azure-hosted AI endpoints previously used by the pipeline have been **decommissioned**;
re-enabling them would require deploying new model endpoints. Impact:

- **Automatic translation is currently broken.** `translate.py` (and the `translate.yml` /
  `translatev2.yml` workflows) depend on an **Azure Translator** endpoint
  (`AZURE_TRANSLATOR_ENDPOINT/REGION/KEY`) that no longer exists.
- **`cl.py v1tov2` reco-renaming is broken.** It depends on an **Azure Text Analytics**
  endpoint (`--text-analytics-endpoint`).
- **Embedding-based dedup still works.** `merge_waf_checklists.py` uses a **local**
  `sentence_transformers` model — no Azure endpoint — so it is unaffected.

Implication: this *strengthens* the case for replacing the broken Azure-hosted paths with
the provider-pluggable LLM approach — feature **(10) LLM-based translation** is not just an
enhancement, it restores a capability that is presently non-functional.

---

## Decision A — Distribution & authentication architecture

### A.1 Primary: local-first app (run on the reviewer's machine) — **CHOSEN**

A small, self-contained app (CLI that launches a localhost web UI, or single binary /
container) that runs on the reviewer's own machine.

- Authenticates to Azure using `DefaultAzureCredential` → the reviewer's existing
  `az login` / CLI session.
- **Zero new grants, no consent prompts, no hosted backend, no data leaving the machine.**
- Preserves the exact "runs with user credentials" property of the spreadsheet.
- Review state persists to a local, git-friendly file (SQLite or JSON).

This is the macro-spreadsheet replacement and the focus of initial effort.

### A.2 Team option: customer-deployed app with managed identity — **DEFERRED (specced)**

For multi-user / persistent engagements. One-click `azd up` deploys a Container App +
system-assigned managed identity with Reader on the target subscription(s).

- The tradeoff (app needs an identity) is acceptable **because the customer owns the
  identity and controls its scope** — no third party gets access.
- **Sequenced after A.1.** Nothing in A.1 blocks adding A.2 later.

**Authentication design for A.2** (low complexity — config, not code):

Two **independent** identities — do not conflate them:

| Direction | Identity | Purpose |
|---|---|---|
| App → Azure | Managed identity (Reader) | Runs ARG queries |
| Human → App | Entra ID built-in auth ("Easy Auth") | Controls who can open the UI |

- **Authentication:** platform-managed Entra ID built-in auth provider (App Service
  Easy Auth / Container Apps built-in auth). No MSAL code, no secrets stored. Requests
  arrive with a validated identity.
- **Authorization (escalating levels):**
  1. **Assignment required** — set "User assignment required = Yes" on the enterprise
     app and assign only named reviewers or a single security group. Blocks everyone
     else in the tenant. Meets the "not everybody can access" requirement on its own.
  2. **App roles** — `Reviewer` / `Admin` roles in token claims for read-only vs. edit.
  3. **Network boundary** — ingress IP allowlist or private endpoint (defense in depth).
- **The real effort in A.2** is not auth; it is multi-user concurrent state, persistent
  storage with backup, and deployment lifecycle/cost ownership.

### A.3 Other options considered (not chosen now)

- **VS Code extension** — natural for the MS/partner audience, reuses Azure Account
  session. Kept as a possible future surface.
- **Static SPA + bring-your-own-token (MSAL)** — no backend, but requires an app
  registration the user consents to (slightly worse on "no extra permission").

---

## Decision B — LLM features are optional and provider-pluggable

### B.1 Positioning — **CHOSEN**

- The **core review works with zero LLM**: load checklist, run ARG with user creds, set
  status/comments, export report. This preserves the "no extra requirements" baseline.
- LLM features (B.3) light up **only if a provider is configured**; otherwise the
  related UI is hidden/disabled.
- LLM capability is delivered via a **pluggable provider abstraction** — the heavy parts
  (RAG retrieval over `v2/recos`, prompt templates, schema validation) are
  provider-agnostic; only a thin `complete()` / `embed()` seam is provider-specific.

### B.2 Provider options

| Provider | Audience | Notes |
|---|---|---|
| **GitHub Copilot** (SDK / Copilot CLI / VS Code) | MS employees & partners | **Recommended default** for the primary audience; reuses existing entitlement |
| **GitHub Models** | Anyone with a GitHub account | Free/low-tier on-ramp for non-Copilot users |
| **Azure AI Foundry / Azure OpenAI** | Customers with their own Azure | Fits the A.2 deployment; data stays in tenant |
| **OpenAI / Anthropic direct** | BYO API key | Simplest fallback |
| **Local (Ollama / ONNX)** | Air-gapped / regulated orgs | No data egress |

**Native GitHub Copilot integration is the recommended default for MS employees and
partners**, who already have the entitlement.

### B.3 Candidate LLM features

Two distinct audiences:

- **Reviewers (run the tool)** — LLM optional:
  - **(5) Narrative report generation** — exec summary, prioritized remediation roadmap,
    per-pillar WAF scoring, grounded (RAG) on the checklist corpus.
  - **(6) Finding triage & evidence-linking** — cluster non-compliant ARG results,
    explain *why* each violates the recommendation, draft the "Comments" cell.
  - **(7) Conversational review assistant** — query live review state + corpus; best
    delivered by exposing the corpus + review state as an **MCP server** so Copilot CLI /
    VS Code Copilot / any agent can drive a review without a bespoke chat UI.
- **Contributors (improve the repo)** — LLM runs in CI / their own Copilot, **invisible
  to reviewers**:
  - **(8) Authoring copilot** — draft title/description/severity/WAF pillar, propose ARG
    queries, semantic duplicate detection against existing GUIDs, schema validation in PR.
  - **(9) ARG query generation/repair** — for recos marked `automatable` but lacking a
    query.
  - **(10) LLM-based translation** — terminology-aware, glossary-respecting replacement
    for Azure Translator, including long-form descriptions.

---

## Decision C — Content & pipeline modernization (candidate, not yet decided)

Noted for later discussion:

- **(11) Recommendation API / package** — publish the corpus as a versioned REST/GraphQL
  endpoint or npm/PyPI package as a single source of truth.
- **(12) Schema convergence** — finish the v2 per-reco model; treat v1 JSON, Excel, web,
  workbooks, and WAF consolidation as *renderers* of one data model.
- **(13) Provenance & freshness** — surface "last reviewed / may be stale"; auto-open
  issues when upstream (APRL/WAF) changes a source recommendation.

### C.1 Corpus refresh: hybrid (mechanical ingestion + LLM-in-the-loop via PRs) — **CHOSEN**

Question considered: should the YAML corpus become a "knowledge base" refreshed
periodically by an LLM (e.g. GitHub Copilot), replacing the mechanical Python pipelines
triggered by upstream repo updates?

**Decision: hybrid, not replacement.** An LLM must **not** write to the source of truth
autonomously. Keep the deterministic pipeline for ingestion/validation and wrap an LLM
around it for the judgment tasks scripts do badly. Rationale:

- **Determinism & auditability** — mechanical syncs produce reviewable, reproducible
  `git diff`s; an LLM refresh is non-deterministic and erodes the "why did this change?"
  provenance that reviewers and contributors depend on.
- **ARG queries are executable code** — unsupervised LLM rewrites of embedded KQL risk
  silently wrong queries that mis-classify resources as compliant: the worst failure mode
  for a review tool.
- **Cost/latency** — periodically reprocessing ~2000 files via an LLM is expensive for
  work that string-matching does for free and instantly.
- **Upstream is already structured** — APRL/WAF publish machine-readable sources;
  mechanical pull is the right transport, with no semantic gap to bridge.

**Where the LLM genuinely adds value** (judgment tasks):

- Semantic dedup & conflict detection across overlapping sources (improving on the
  string-based `find_duplicate_guids`; note embeddings are *already* used in
  `merge_waf_checklists.py`).
- Consolidation/summarization into larger bodies (e.g. WAF write-ups).
- Change triage — explain upstream diffs, flag breaking/semantic changes, draft updates.
- Drafting new fields (description, severity, WAF pillar) and proposing ARG queries for
  `automatable`-but-unqueried recos.

**The pattern — LLM-in-the-loop, never autonomous-on-main:**

```
mechanical sync (detect change) → LLM judgment (dedup / draft / summarize / explain)
  → PR → CI validation (schema + ARG lint/run) → human merge
```

Determinism and provenance are preserved at the `main`-branch boundary; LLM leverage
happens inside the *proposal* step. A scheduled GitHub Action with Copilot fits this.

---

## Appendix — Current mechanical pipeline inventory (`scripts/`)

Tasks performed today by scripts / GitHub Actions, for reference when deciding what stays
mechanical vs. gains an LLM-in-the-loop layer:

| Script | Task | Hybrid candidate? |
|---|---|---|
| `sync_folder.py` | Pull latest files from the repo's main branch | No — pure transport |
| `translate.py` | Translate checklist to es/ja/pt/ko/zh-Hant via Azure Translator | Yes — feature (10); **currently broken (endpoint decommissioned)** |
| `merge_waf_checklists.py` | Merge WAF / review / service-guide checklists, dedup via **local** embeddings (`sentence_transformers`) | Yes — already AI-assisted; **still works (local model)** |
| `create_master_checklist.py` / `compile_checklist.py` | Combine all checklists into a master JSON + macro-free XLSX | No — deterministic assembly |
| `verify_checklist.py` | Validate checklist correctness / schema | No — must stay deterministic (CI gate) |
| `sort_checklist.py`, `timestamp_checklist.py` | Housekeeping (ordering, timestamps) | No |
| `workbook_create.py` | Generate Azure Monitor workbook from a checklist | No — deterministic render |
| `update_excel_openpyxl.py`, `checklist_graph_update.py` | Populate Excel / import ARG results into spreadsheet | No |
| `checklist_graph.sh` | Run ARG queries with the user's credentials | No — the "no extra permission" core |
| `cl.py` | CLI: `analyze-v1/2`, `list/show-recos`, `v1tov2` (uses **Text Analytics**, **endpoint decommissioned**), `run-arg` | Partly — `v1tov2` AI-assisted but currently broken |
| `upload2cosmosdb.py`, `upload2tablestorage.py` | Publish corpus to Cosmos DB / Table Storage | No — relates to (11) API/package |

Takeaway: ingestion, validation, assembly, and rendering stay **mechanical**; translation,
dedup/merge, and authoring/triage are the **LLM-in-the-loop** surfaces — and two of them
(`merge_waf_checklists.py`, `cl.py v1tov2`) already use AI, so C.1 extends an existing
precedent rather than introducing a new paradigm.

---

## Open items / next steps

- [ ] Confirm Decision C scope.
- [ ] Sketch the LLM provider-abstraction interface (`complete()` / `embed()` with
      Copilot, Foundry, and local implementations).
- [ ] Prototype A.1 (local-first app with `DefaultAzureCredential`).
- [ ] Design the MCP server over the checklist corpus + review state (feature 7).

## Decision summary

| ID | Decision | Status |
|----|----------|--------|
| A.1 | Local-first app (`DefaultAzureCredential`) as primary | **Chosen** |
| A.2 | Customer-deployed app + managed identity, Easy Auth + assignment-required | **Deferred, specced** |
| B.1 | LLM features optional; no-LLM baseline guaranteed; provider-pluggable | **Chosen** |
| B.2 | GitHub Copilot as recommended default for MS/partners | **Chosen** |
| C   | Content/pipeline modernization (API, schema convergence, provenance) | **Proposed** |
| C.1 | Hybrid corpus refresh — mechanical ingestion + LLM-in-the-loop via PRs (no autonomous writes to main) | **Chosen** |
