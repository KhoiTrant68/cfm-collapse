## Contract Paraphrase

D1 (methodology_rigor, mandatory, owned by the methodology seat): read adversarially, this dimension asks whether the procedures a reader would need to re-derive or re-run the work are present and sound, meaning stated assumptions, proof dependencies, numerical protocols, seeds, tolerances and reporting granularity, such that a hostile replicator could not obtain a different answer by making a defensible alternative choice. I do not score it, but any logical gap I find that comes from a missing procedure is evidence the methodology seat should weigh.

D2 (domain_accuracy, mandatory, owned by the domain seat): this dimension asks whether what the work says about the field, including prior results, standard definitions and established terminology, is stated correctly, so that the novelty or contrast it claims is not built on a misreported predecessor or on a term used differently from the literature. From the adversarial side, a misrepresented baseline result is the cheapest way to manufacture a contribution. I do not score it.

D3 (argumentative_coherence, mandatory, owned by my seat): this is the dimension I am accountable for. It asks whether the central thesis survives its strongest counter-argument: whether each stated result follows from the stated hypotheses with no hidden extra assumption, whether the informal headline claims are no stronger than the formal statements they summarise, whether numerical checks actually test the claims they are cited for rather than an easier proxy, whether evidence was selected to favour the thesis, and whether an alternative explanation accounts for the same observations at least as well.

D4 (cross_disciplinary_relevance, high, owned by the perspective seat): this dimension asks whether readers from neighbouring areas could follow the framing and definitions and whether any claim of relevance beyond the core subfield is actually supported rather than asserted. Adversarially, a broad-impact claim with no supporting argument is an overreach, but scoring it belongs to the perspective seat.

D5 (writing_and_structure, normal, owned by the EIC seat): this dimension asks whether the organisation, exposition, figures and tables let a reader locate and check each claim, and whether venue conventions are followed. Poor structure can conceal a logic gap, which is why I note it, but I do not score it.

D6 (venue_fit_and_contribution, mandatory, owned by the EIC seat): this dimension asks whether the work belongs at the configured venue and adds something original and significant for its readers. From the adversarial angle, the question is whether the contribution stays non-trivial once overclaims are removed. No criteria binding was supplied for this run, so I make no venue-fit claim, and the dimension is not mine to score.

## Scoring Plan

### D3: argumentative_coherence
dimension_id: D3
what_to_look_for: I will trace each headline claim in the abstract, introduction and conclusion back to the formal statement it relies on and check that the hypotheses match. I will look for unstated extra assumptions in the proofs, such as regularity, exactness of the learned object, limits taken in an unjustified order, or uniqueness assumed rather than shown. I will check whether each numerical check tests the claimed regime or only a convenient special case, and whether positive-only evidence, a narrow configuration sweep or post hoc thresholds would make a check unable to fail. I will look for scope drift from an idealised object to practical trained models, for circular use of a result inside its own justification, and for the most parsimonious alternative explanation of each reported phenomenon.
what_triggers_block: A load-bearing conclusion that the paper states as established, but that depends on a step which is unjustified yet repairable: a missing hypothesis, an unproved lemma used as if proved, a numerical check that tests a proxy rather than the stated claim, or an informal claim that strictly exceeds its formal counterpart. The core thesis can still be saved by narrowing the claim, adding the assumption, or supplying the missing argument or check, without any new idea.
what_triggers_warn: A non-central inconsistency or overreach that leaves the main thesis standing. Examples are hedged scope language that drifts in a secondary section, an alternative explanation that is plausible but not addressed for a supporting observation, a numerical check reported without the failure cases or parameter ranges needed to show it could have failed, or a terminology shift that a careful reader can resolve.
what_triggers_fatal: The central thesis itself cannot stand as stated. A main theorem is contradicted by a counterexample within its own hypotheses, two core results are mutually inconsistent, the argument for the headline claim is circular, the paper's own numerical evidence directly contradicts the headline claim, or a simpler alternative mechanism explains all the reported evidence and the contribution reduces to a known or trivial fact once that mechanism is taken into account.

criteria_binding_unavailable

[CONTRACT-ACKNOWLEDGED]
