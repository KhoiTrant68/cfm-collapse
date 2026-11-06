## Contract Paraphrase

D1 (methodology_rigor, mandatory, owned by the methodology seat). From the editorial chair, this dimension asks whether the work can be checked and repeated. Experimental designs, data handling, and statistical reporting have to meet the normal peer-review bar for the field. For theory-led work that means the stated assumptions are actually used and the empirical checks are set up so they could fail. I will not score this dimension. I will check that the owning seat's verdict is consistent with the rest of the panel.

D2 (domain_accuracy, mandatory, owned by the domain seat). This dimension asks whether the claims agree with what the field currently knows, whether prior results are described correctly, and whether technical terms and cited results are used without factual error. I will not score it. I will treat a domain-seat finding that prior work is misrepresented as directly relevant to my own originality judgement under D6.

D3 (argumentative_coherence, mandatory, owned by the Devil's Advocate with the methodology seat eligible). This dimension asks whether the central thesis is consistent with itself, whether the evidence offered actually supports each headline claim, and whether any reasoning error breaks the main argument. I will not score it. I will read its outcome alongside D6, because a contribution only counts if the argument for it holds.

D4 (cross_disciplinary_relevance, high priority, owned by the perspective seat). This dimension asks whether the framing, definitions, and implications are readable by people in adjacent subfields, and whether any claim that reaches outside the home field is backed by evidence. I will not score it. I will note where it bears on how wide an audience the work can reach.

D5 (writing_and_structure, normal priority, owned by me). This dimension covers how the manuscript is organised, how clearly it explains itself, how good the figures and tables are, and whether it follows the venue's conventions. For a theory-heavy ML conference paper the questions are: can a reviewer find the main result, its assumptions, and its proof path within the page limit, and are the appendices organised so that results can be checked?

D6 (venue_fit_and_contribution, mandatory, owned by me). This dimension asks whether the manuscript suits its configured venue and whether it makes an original, significant contribution for that venue's readers. No author-confirmed review-target binding was supplied for this run. I will therefore judge fit only against general expectations for a top ML conference in generative-model theory, not against bound venue criteria. Originality and significance are measured against existing theory and empirical work on diffusion and flow-matching models.

## Scoring Plan

### D5: writing_and_structure
dimension_id: D5
what_to_look_for: Whether the main theorem or claim, its assumptions, and its scope are stated precisely in the main text before they are used. Whether notation is introduced once and stays consistent. Whether each formal statement points to its proof and the appendix follows the main-text order. Whether every figure or table has axes, units, seeds or sample sizes, and a caption that says what it shows. Whether the contribution list in the introduction matches what is actually proved and measured. Whether page-limit, anonymity, and reproducibility-statement conventions are followed.
what_triggers_block: The headline formal result cannot be found or read from the main text alone, for example because it is stated only informally or its assumptions appear only in an appendix. Or notation or definitions change between sections, so that a reader cannot tell which object a key theorem is about.
what_triggers_warn: The exposition is correct but hard to navigate. Examples are dense notation with no summary table, proofs that are not cross-referenced, figures whose captions or legends leave the plotted quantity unclear, contribution bullets that slightly overstate what the body delivers, or minor convention problems such as overflowing pages or a missing limitations or reproducibility statement.

### D6: venue_fit_and_contribution
dimension_id: D6
what_to_look_for: Whether the paper states a clear new result that is not already a direct corollary of known analyses of the empirical or closed-form optimum of diffusion and flow-matching objectives, guidance, or memorisation. Whether it places itself precisely against the closest prior theorems and states what is new: the assumptions, the generality, the mechanism, or the measured consequence. Whether the result says something about the behaviour of learned models that matters to ICLR readers, beyond idealised objects. Whether the empirical part tests the theory in ways that could falsify it, rather than only illustrating it.
what_triggers_block: The paper shows real competence, but its central contribution is unclear in a way that can be fixed. Examples are claimed novelty that substantially overlaps an uncited or under-discussed prior result, a gap between the idealised setting that is proved and the learned-model setting that is claimed, with that gap left unbounded or not acknowledged, or significance resting mainly on assertion and not on a demonstrated consequence.
what_triggers_warn: The contribution is real and fits the venue but is modest or incrementally framed. Examples are a comparison with the nearest prior results that is present but thin, a narrow scope of experimental validation (few datasets, scales, or seeds), or broader implications for practice that are stated more strongly than the evidence supports.
what_triggers_fatal: The central result is already established in prior work with no substantive new element, or it is mathematically trivial or wrong in a way that removes the claimed contribution, or the paper falls outside the scope of a machine-learning venue, so that no revision within one review cycle could produce a publishable contribution.

criteria_binding_unavailable

[CONTRACT-ACKNOWLEDGED]
