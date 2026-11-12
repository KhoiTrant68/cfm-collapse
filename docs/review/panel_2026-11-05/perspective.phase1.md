## Contract Paraphrase

D1 (methodology_rigor, mandatory, owned by the methodology seat). The study design, data handling, statistical reporting and reproducibility affordances must clear the ordinary peer-review bar of the field. From a cross-disciplinary seat I do not score this; I only note that a statistician reading the work will expect sample sizes, seeds, uncertainty estimates and estimator definitions to be stated so that an outside reader could rerun or re-derive them.

D2 (domain_accuracy, mandatory, owned by the domain seat). Claims must match current domain evidence, prior work must be represented correctly, and domain terminology and cited results must be free of factual error. I do not score this, but where the domain literature overlaps with adjacent fields (nonparametric estimation, learning theory, privacy auditing), misattribution of a classical result to recent work would also be a cross-field accuracy concern I would pass to that seat.

D3 (argumentative_coherence, mandatory, owned by the devil's advocate with the methodology seat also eligible). The central thesis must be internally consistent, the evidence must actually support the claims made, and no fallacy may undercut the main argument. I do not score this; my concern is limited to whether conclusions drawn for adjacent audiences follow from what is shown.

D4 (cross_disciplinary_relevance, high priority, owned by my seat). Framing, definitions and stated implications must be legible to readers from neighbouring fields, and any claim that reaches into another discipline must be backed by argument or evidence rather than asserted. This is the one dimension I score: I will judge whether a kernel-smoothing or learning-theory reader can map the paper's objects onto familiar ones, and whether any implications stated for memorisation, privacy or deployment practice are substantiated.

D5 (writing_and_structure, normal, owned by the editor-in-chief seat). Organisation, clarity of exposition, figure and table quality and adherence to venue conventions. I do not score this; I note only that accessibility to adjacent readers depends partly on notation being introduced before use.

D6 (venue_fit_and_contribution, mandatory, owned by the editor-in-chief seat). The work must fit the configured venue and make an original, significant contribution for its readership. I do not score this and, with no review-target binding supplied, I make no venue-fit claim of my own.

## Scoring Plan

### D4: cross_disciplinary_relevance
dimension_id: D4
what_to_look_for: Whether central objects (empirical targets, smoothing or bandwidth-like parameters, limiting regimes, guidance or averaging operators) are defined precisely enough that a nonparametric statistician can identify their classical counterparts (empirical measure, kernel density or Nadaraya-Watson estimators, bias-variance and bandwidth asymptotics); whether connections to that literature and to learning-theory generalisation notions are acknowledged rather than rediscovered; and whether any claim about memorisation, training-data reproduction, privacy risk or deployment consequences is tied to a stated, checkable criterion (a distance or nearest-neighbour test, a membership or extraction notion, an explicit regime of sample size and model capacity) and is scoped to the setting actually analysed.
what_triggers_block: An implication for an adjacent field is a headline claim but is unsupported, for example asserting a privacy or memorisation-risk conclusion for deployed or trained models while the analysis covers only an idealised or exact-empirical setting with no argument or evidence bridging the two, or a central definition is so field-internal or ambiguous that an adjacent reader cannot determine what is being claimed or test it.
what_triggers_warn: The core claims are scoped correctly and readable, but adjacent-field framing is incomplete: a known equivalence or classical precursor (for example the kernel-smoothing or empirical-measure view of the same limit) goes uncited or is presented as new, memorisation is used informally without an operational definition, or a cross-field implication is stated in the discussion with hedging but no supporting evidence or explicit limitation.

criteria_binding_unavailable

[CONTRACT-ACKNOWLEDGED]
