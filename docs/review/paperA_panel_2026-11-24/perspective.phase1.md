## Contract Paraphrase

D1 (methodology_rigor) asks whether the study design, data handling, statistical reporting and reproducibility affordances meet the peer-review bar of the field. From a cross-disciplinary standpoint I read this as the base that any adjacent-field reader, such as a privacy auditor, must be able to rely on before reusing a result: settings, seeds, data splits and evaluation protocols should be reported clearly enough that an outsider could rerun the evidence. Scoring this dimension belongs to the methodology seat, not to me.

D2 (domain_accuracy) asks whether claims match current domain evidence, prior work is represented correctly, and domain terminology and results are free of factual errors. For readers who come from privacy and data extraction, this also covers whether terms borrowed from that literature (memorisation, leakage, extraction, membership) are used with the meanings that literature gives them. Scoring this dimension belongs to the domain seat.

D3 (argumentative_coherence) asks whether the core thesis is internally consistent, whether the evidence supports the claims, and whether any fallacy undermines the central argument. My cross-disciplinary interest is the chain from formal statement to stated consequence: a conclusion should not be stronger than its premises allow. Scoring this dimension belongs to the devil's-advocate and methodology seats.

D4 (cross_disciplinary_relevance) asks whether framing, definitions and implications are accessible to readers in adjacent fields, and whether interdisciplinary claims are substantiated. This is my dimension. It covers whether readers from privacy, auditing and responsible-deployment work can tell which results hold only under idealised assumptions, whether imported concepts are defined to that community's standard, and whether any practical guidance or broader-impact statement offered to those readers actually follows from the evidence presented.

D5 (writing_and_structure) asks about the organisation of the manuscript, the clarity of its exposition, the quality of its figures and tables, and its adherence to venue conventions. For adjacent-field readers this decides whether the scope conditions and the takeaways can be found without reading every derivation. Scoring this dimension belongs to the editor-in-chief seat.

D6 (venue_fit_and_contribution) asks whether the manuscript fits the configured venue and makes an original, significant contribution suited to its readership. I make no venue-fit judgement in this phase or the next. Scoring this dimension belongs to the editor-in-chief seat.

## Scoring Plan

### D4: cross_disciplinary_relevance
dimension_id: D4
what_to_look_for: Whether every recommendation addressed to practitioners, auditors or privacy researchers is explicitly tied to the regime in which it was shown (exact or idealised optimum versus finite-capacity, finite-step trained models), with that gap stated next to the recommendation; whether terms such as memorisation, leakage, replication and extraction are defined operationally and placed against the membership-inference, training-data-extraction and differential-privacy literature; whether outputs that blend or interpolate several training records are classified as leakage or not, with a stated criterion; whether claims about which training record a model returns (its predictability or controllability) say what an adversary or auditor would need to know to exploit or test it; and whether a broader-impact statement exists that weighs both the auditing value and the misuse potential of the results.
what_triggers_block: The manuscript gives operational guidance to auditors or practitioners, or makes privacy or leakage claims about deployed or trained models, that rests only on results proven or observed at an idealised optimum, with no empirical bridge to trained models and no explicit statement that the guidance is conditional on that regime; or it states a leakage or memorisation conclusion under a definition that contradicts the standard privacy-literature meaning without saying so, so that an adjacent-field reader would draw a materially wrong conclusion.
what_triggers_warn: The idealised-to-practical gap is acknowledged but only in a limitations paragraph separate from the recommendations, or only partly bridged by experiments; or blends of training records, or the predictability of the returned record, are discussed without a stated leakage criterion or threat model; or privacy terms are used loosely without citing the relevant membership-inference, extraction or differential-privacy work; or the broader-impact statement is missing, generic, or does not address misuse of the findings.

criteria_binding_unavailable

[CONTRACT-ACKNOWLEDGED]
