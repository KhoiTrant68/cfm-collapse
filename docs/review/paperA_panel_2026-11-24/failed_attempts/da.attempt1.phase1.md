## Contract Paraphrase

D1 (methodology_rigor): Read adversarially, this asks whether the study design could have produced a different answer at all. For a theory paper with numerical checks that means asking whether the experiments are set up so that a false theorem would visibly fail, whether seeds, sample sizes and tolerances are reported, and whether someone else could rerun the checks and get the same numbers. Another seat owns this; I will raise methodology concerns only where they break the argument chain.

D2 (domain_accuracy): Every claim about flow matching, the closed-form empirical velocity field, memorisation, and prior results must match the published literature. An adversarial reading looks for prior work that is caricatured to make the contribution look new, terms used in a nonstandard sense without saying so, and attributed results that the cited sources do not actually state. The domain seat owns this.

D3 (argumentative_coherence): This is the dimension I own. The central thesis has to hold together from assumptions to conclusion. Each theorem's hypotheses must actually be met in the settings it is applied to, the numerical evidence must test the claim rather than a weaker neighbour of it, and no step may rely on a fallacy (equivocation, circularity, affirming the consequent, a sufficient condition presented as necessary) that the conclusion depends on. I will look hardest for the strongest counter-argument, for alternative explanations of the observed behaviour, and for conclusions drawn more broadly than the evidence allows.

D4 (cross_disciplinary_relevance): The framing and definitions should make sense to neighbouring communities, such as diffusion-model practitioners, optimal-transport theorists, and privacy or memorisation researchers. Any claim about what the result means for those fields must be backed up, not just asserted. An adversarial reader checks whether implications for practice are stated as if they followed from idealised theory without the bridging argument. The perspective seat owns this.

D5 (writing_and_structure): The manuscript should be organised so that a reader can find each claim, its proof and its supporting evidence. Figures and tables should show what the text says they show, and the exposition should follow the conventions of the venue. An adversarial reader notices when the structure hides weak links, for example key assumptions placed only in an appendix. The editor seat owns this.

D6 (venue_fit_and_contribution): The work should make a contribution that is original, significant and suited to the target readership. Adversarially, the question is whether the main result is new or a restatement of known facts in different notation. No venue criteria were supplied for this run, so I make no claim about venue fit. The editor seat owns this.

## Scoring Plan

### D3: argumentative_coherence
dimension_id: D3
what_to_look_for: Trace each headline claim back to the theorem or experiment that supports it. Check that every theorem hypothesis (exact versus learned field, finite sample, idealised optimiser, conditioning structure, time-horizon limits) holds in each setting where the result is invoked. Check that the numerical checks could have falsified the claim, rather than only illustrating it. Check that conclusions about classes of interventions do not go beyond the cases actually proved or tested. Check whether the paper considers the strongest alternative explanation for each observed effect, such as discretisation or integrator error, finite-capacity smoothing, or a choice of metric, threshold or seed. Check that "keeps", "prevents" and "necessary/sufficient" have one meaning throughout.
what_triggers_block: A headline claim rests on a step that does not follow from what precedes it. Examples: a sufficient condition used as if it were necessary; a result proved for the exact empirical field then applied to trained networks with no bridging argument or bound; a universal claim over a family of interventions supported only by a few hand-picked instances. Any of these needs substantial reworking of the claim or new proof or evidence before the thesis can stand.
what_triggers_warn: The core chain holds, but a local gap remains. Examples: a hypothesis is used without being restated, an obvious alternative explanation is left unaddressed, wording in the abstract or conclusion is stronger than the theorems support, or numerical checks cover a narrow range (dimension, sample size, step count, seeds) with no discussion of whether the result extends. Each can be fixed by rewording, adding caveats or a short added argument without changing the thesis.
what_triggers_fatal: The central thesis is contradicted internally or by the paper's own evidence. Examples: a core theorem is false because of a counterexample that fits its stated hypotheses; the main argument is circular, assuming the memorisation or collapse behaviour it claims to derive; or the paper's numerical results directly contradict the main theorem in the regime the theorem covers. In each case no rewording or caveat leaves a defensible core claim.

criteria_binding_unavailable

[CONTRACT-ACKNOWLEDGED]
