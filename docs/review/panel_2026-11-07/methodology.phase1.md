## Contract Paraphrase

D1 (methodology_rigor, mandatory, owned by methodology). From a methodology standpoint this dimension asks whether the technical apparatus can actually carry the claims made with it. For a theory-led machine learning submission that means: every formal statement has explicit, checkable hypotheses; proofs or proof sketches establish exactly what is stated and no more; quantifiers such as "almost surely", "for almost every initial condition", or "generically" are defined and justified; any asymptotic or formal derivation is clearly separated from what is proved; and any numerical evidence comes with enough description (solvers, tolerances, discretisation, seeds, data subsets, sensitivity checks) that another researcher could reproduce it and judge how far numerical error could move the conclusions.

D2 (domain_accuracy, mandatory, owned by domain). This dimension concerns whether the claims match current evidence in the field, whether prior work is represented fairly and correctly, and whether domain terminology and cited results are used without error. Methodologically, I note that a misreported prior result can quietly weaken an argument's premises, but scoring this dimension belongs to the domain reviewer, not to me.

D3 (argumentative_coherence, mandatory, owned by the devil's advocate, methodology eligible). This dimension asks whether the central thesis holds together: whether the chain from assumptions to theorems to empirical illustration is internally consistent, whether the evidence offered for each claim is the right kind and strength (proof versus heuristic versus numerical consistency check), and whether any inferential step overreaches, for example generalising from a special case, treating a formal expansion as a theorem, or reading a numerical agreement as confirmation of a mechanism.

D4 (cross_disciplinary_relevance, high priority, owned by perspective). This dimension asks whether framing, definitions, and implications can be followed by readers in adjacent areas, and whether claims that cross disciplinary lines are substantiated. From my side, precise definitions and explicit hypotheses also serve this goal, but the dimension is scored by the perspective reviewer.

D5 (writing_and_structure, normal priority, owned by the editor-in-chief). This dimension covers organisation, clarity of exposition, figure and table quality, and conformity with venue conventions. Methodological transparency depends partly on clear presentation, for instance whether assumptions are stated where they are used, but scoring rests with the editor.

D6 (venue_fit_and_contribution, mandatory, owned by the editor-in-chief). This dimension asks whether the work suits the configured venue and makes an original, significant contribution for its readers. I do not judge significance; I only note that a contribution claim depends on the technical results being sound, which D1 and D3 assess.

## Scoring Plan

### D1: methodology_rigor
dimension_id: D1
what_to_look_for: Each formal result states its hypotheses completely and its proof covers exactly those hypotheses; measure-theoretic qualifiers and solution concepts for the underlying ODEs are defined; formal or asymptotic derivations are labelled as such and the bounds needed to make them rigorous are identified; numerical experiments report solver type, stiffness handling, tolerances, step or hand-off rules, seeds, data subsets, and sensitivity or cross-solver checks, and numerical results are framed in proportion to their error control; code or enough detail to reproduce is available.
what_triggers_block: A headline theorem relies on an unstated or unverified hypothesis, or a proof has a gap that undermines a central claim, or a key numerical conclusion depends on settings that are not reported or not checked for sensitivity, so the main result cannot be verified as stated.
what_triggers_warn: Hypotheses or qualifiers are stated loosely but are recoverable, a formal derivation is presented without clearly marking which steps are unproved, or numerical reporting lacks some solver, tolerance, or seed details while the conclusions still look robust.
what_triggers_fatal: A central theorem is false as stated (a counterexample within its hypotheses exists or the proof's core step is invalid), or the decisive numerical evidence is shown to be a solver or discretisation artefact, so the paper's main technical contribution does not stand.

### D3: argumentative_coherence
dimension_id: D3
what_to_look_for: The stated assumptions, theorems, and numerical illustrations form a consistent chain; each claim in the abstract and conclusion is traceable to a proved result or clearly labelled heuristic or numerical evidence; special cases are not generalised beyond what is shown; numerical agreement is presented as consistency rather than as proof unless error is controlled; no assumption used in one result contradicts another.
what_triggers_block: A main claim in the abstract or conclusions goes materially beyond what the theorems and experiments establish, or two parts of the argument rely on incompatible assumptions, so the central thesis is not supported as written.
what_triggers_warn: Some claims are phrased more strongly than their support (for example a heuristic or numerical finding described in theorem-like language), or the link between a theoretical result and its empirical illustration is under-explained, while the core thesis remains supported.
what_triggers_fatal: The central thesis is internally contradictory or rests on a step that, once corrected, removes the conclusion the paper is built around.

criteria_binding_unavailable

[CONTRACT-ACKNOWLEDGED]
