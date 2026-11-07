## Contract Paraphrase

D1 (methodology_rigor): From a cross-disciplinary standpoint, this dimension asks whether the work's design, data handling, statistical reporting and reproducibility support would satisfy a careful reader trained in the field's own review norms. A nonparametric statistician would read it as asking whether any empirical check is reported with enough detail (sample sizes, seeds, uncertainty, code or data pointers) that an outsider could rerun it. This dimension is owned by the methodology reviewer and I do not score it.

D2 (domain_accuracy): This dimension asks whether claims agree with current evidence in flow matching and diffusion modelling, whether prior work is represented fairly, and whether field-specific terms and results are used correctly. Seen from adjacent fields, it is the guarantee that the vocabulary an outside reader inherits is the field's real vocabulary and not a private one. It belongs to the domain reviewer and I do not score it.

D3 (argumentative_coherence): This dimension asks whether the central thesis holds together internally, whether the evidence offered actually carries the claims made, and whether any reasoning gap undermines the main argument. For an outside reader, coherence is what lets a stated conclusion be trusted without re-deriving every step. It is owned by the devil's advocate seat, with methodology also eligible; I do not score it.

D4 (cross_disciplinary_relevance): This is the dimension I own. It asks whether the framing, definitions and stated implications can be followed by readers from neighbouring fields (nonparametric statistics, kernel smoothing, statistical learning theory, privacy and memorisation auditing), and whether any claim that reaches into those fields, or into practice, is actually substantiated rather than asserted. It also covers whether the reach of the conclusions is stated honestly: what carries over beyond the setting analysed, and what does not.

D5 (writing_and_structure): This dimension asks whether the manuscript is organised and written clearly, whether figures and tables communicate well, and whether it follows the venue's conventions. Clear structure is a precondition for outside readers, but scoring it is the editor's job, not mine.

D6 (venue_fit_and_contribution): This dimension asks whether the work suits the configured venue and makes an original and significant contribution for that venue's readers. Cross-field relevance can feed into significance, but the fit and contribution judgement belongs to the editor-in-chief seat and I do not score it.

## Scoring Plan

### D4: cross_disciplinary_relevance
dimension_id: D4
what_to_look_for: Whether core objects and results are defined so a statistician or privacy auditor can follow them, whether links to classical estimators or quantisation views are stated and correct, whether implicit assumptions are named with their effect on scope, and whether practical or privacy implications come with a testable diagnostic and evidence beyond a stylised setting.
what_triggers_block: A headline practical, privacy, or cross-field claim is presented as established but rests only on a stylised or toy setting with no stated assumption boundary, or a key cross-field equivalence is asserted that does not hold as stated, so an adjacent-field reader would be materially misled about what the result licenses.
what_triggers_warn: Cross-field connections or practical implications are plausible but under-explained, the assumptions limiting scope are only partly stated, or definitions require field-internal background that is not supplied, without changing what the core claims license.

criteria_binding_unavailable

[CONTRACT-ACKNOWLEDGED]
