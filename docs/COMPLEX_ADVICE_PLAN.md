# Complex Advice Expansion Plan

## Current Architecture Review (What limits advice complexity today)

The current agent is clean and reliable, but optimized for **single-question tactical answers** rather than deep, multi-step coaching.

### 1) Prompt and tool constraints

- The system prompt asks for actionable advice, but the tool interface only supports:
  - `query_knowledge(category, subcategory)`
  - `web_search(query, num_results)`
- There is no explicit tool for:
  - collecting player context (nation, year, goals, constraints)
  - decomposing long-horizon plans into phases
  - validating trade-offs or generating alternatives

### 2) Retrieval depth is shallow

- `query_knowledge` returns one file at a time via a strict category/subcategory map.
- The model can make multiple calls, but there is no built-in retrieval strategy like:
  - cross-file synthesis
  - relevance ranking
  - "best next sources" selection

### 3) No explicit strategic state model

- Conversation history exists, but there is no structured state object for strategic context:
  - short-term objective
  - long-term win condition
  - economy/military/diplomatic risk posture
  - unresolved assumptions
- This makes advice drift likely across turns.

### 4) No quality guardrails for advanced outputs

- The agent currently has no post-generation validation for:
  - contradiction checks
  - feasibility checks (e.g., overcommitting resources)
  - confidence/uncertainty reporting
  - source coverage checks ("did we consult enough evidence?")

## Target Outcome

Enable the agent to produce **campaign-level strategic guidance** that is:

1. Context-aware (adapts to player skill, nation, start conditions).
2. Multi-horizon (immediate moves + 5/15/30-year intent).
3. Trade-off explicit (what you gain, what you risk, alternatives).
4. Self-audited (states confidence, assumptions, and gaps).

## Roadmap

## Phase 1 — Advice Scaffolding (Low risk, high impact)

### Deliverables

1. **Add an internal response schema** in prompts:
   - Situation
   - Objectives (short/mid/long)
   - Recommended plan by phase
   - Risk matrix
   - Fallback plans
   - "If X happens, pivot to Y" triggers
2. **Add a "clarifying questions" behavior** when key context is missing.
3. **Introduce a "complex query mode" heuristic** (e.g., query contains multiple constraints, long timelines, or optimization goals).

### Implementation notes

- Update `SYSTEM_PROMPT` with explicit advanced-output format requirements.
- Keep existing tools unchanged in this phase.
- Add unit tests for output-format compliance by mocking model outputs where needed.

### Success criteria

- Complex strategy queries consistently return phased plans with explicit risks.
- Fewer vague responses for multi-part questions.

## Phase 2 — Better Retrieval and Synthesis

### Deliverables

1. **New synthesis helper in knowledge layer**:
   - support fetching multiple subcategories in one call (e.g., military + economy + diplomacy)
   - add simple relevance ordering based on query keywords
2. **Tool expansion**:
   - `query_knowledge_multi(categories_or_topics: list[str])`
   - optional `web_search_comprehensive(...)` path for difficult questions
3. **Source tracking metadata**:
   - surface which files were used in final advice

### Implementation notes

- Extend `EU5Knowledge` with a multi-fetch API that returns a structured bundle.
- Keep backward compatibility with existing `query_knowledge`.
- Reuse existing Tavily comprehensive search function already present in `search.py`.

### Success criteria

- Complex answers cite broader relevant mechanics without requiring repeated manual user prompting.
- Higher consistency across economy/military/diplomacy recommendations.

## Phase 3 — Strategic Memory and Planning State

### Deliverables

1. **CampaignState object** persisted in memory per session:
   - nation, timeframe, neighbors/threats
   - objectives and accepted risks
   - active commitments (wars, alliances, economy priorities)
2. **State-aware planning loop**:
   - generate plan
   - check against current state
   - update state after each major recommendation
3. **Session save/load support** (JSON export/import) for long campaigns.

### Implementation notes

- Add a lightweight dataclass model under `eu5_agent/`.
- Store "assumptions" explicitly so the model can revise them when user corrections arrive.
- Wire into CLI to show/update campaign context.

### Success criteria

- Advice remains coherent over long conversations.
- Agent avoids repeating contradictory recommendations.

## Phase 4 — Reliability Guardrails for Advanced Advice

### Deliverables

1. **Self-critique pass** before final answer:
   - contradiction check
   - resource feasibility check
   - missing-information check
2. **Confidence labels** per major recommendation (High/Medium/Low + reason).
3. **Alternative path generation**:
   - conservative / balanced / aggressive variants

### Implementation notes

- Add a second internal completion call for critique in complex mode only.
- Cap extra token cost using strict budgets and short critique prompts.

### Success criteria

- Measurable reduction in conflicting or brittle recommendations.
- Users receive clearer "why" and "when to pivot" guidance.

## Phase 5 — Content Expansion to Unlock Better Plans

### Deliverables

1. Add high-impact nation playbooks (Ottomans, France, Castile, Portugal).
2. Add advanced strategy docs:
   - trade empire paths
   - subject/vassal management plans
   - institution and tech timing strategies
3. Add scenario templates (e.g., "small nation survival", "great power containment").

### Success criteria

- Higher answer depth for nation-specific campaign planning.
- Reduced dependency on web fallback.

## Testing and Evaluation Plan

1. **Golden query set** (20-30 complex prompts) covering:
   - long-horizon campaign planning
   - multi-constraint optimization
   - contingency planning
2. **Rubric scoring** (manual + optional LLM-judge):
   - specificity
   - internal consistency
   - cross-domain integration
   - risk awareness
   - actionability
3. **Regression tests**:
   - preserve quality for beginner/simple questions
   - ensure latency/cost stays within acceptable range

## Recommended Execution Order (2-3 sprints)

### Sprint 1

- Phase 1 (prompt/schema + complex mode heuristic)
- Initial golden query set + rubric

### Sprint 2

- Phase 2 (multi-source retrieval + tool expansion)
- Source-tracking output

### Sprint 3

- Phase 3 (campaign state) + selected Phase 4 checks
- Pilot with a few long conversation transcripts

## Near-term TODO candidates

1. Update prompt with explicit advanced answer template.
2. Add `query_knowledge_multi` and tests.
3. Expose comprehensive Tavily search path to the tool layer.
4. Implement `CampaignState` memory object.
5. Add complex-query evaluation script and baseline report.
