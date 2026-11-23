# Readability review, round 3 (read-only)

Repo: cfm-collapse, branch paper-split-drafts, commit 834f3bf. Nothing edited.
Paper A = paper_theory/main.tex. Paper B = paper_mechanism/main.tex.
Scope: title, abstract, intro + contributions, first paragraph of each section, theorem lead-ins,
captions (overview/teaser first), conclusion. Theorem statements, proofs and numbers untouched.

Overall: B is close to the target voice (clear question, clear stakes, honest caveats); its main
problem is one key definition (radial ratio) and caption overload. A is mathematically careful but
a newcomer meets ~10 undefined terms (exact field, source, atom, prior, blend, circumcentre,
conjunction, support, boundary marker, schedule of bounded variation) before learning why the
question matters, and it never gives the one picture that makes "two fields keep, three can blend"
click.

---------------------------------------------------------------------------------------------------
## Paper A: "Which Interventions Keep a Conditional Flow on Its Training Set?"

### Top 10 issues (ranked)

1. **Abstract opens without the stake, and defines the object in jargon** - main.tex:105-112
   Original: "Conditional flow-matching samplers are often run with a field other than the one their
   objective targets. ... the exact empirical field, the population minimiser for a fixed training set"
   Why: The reader is not told that the issue is copying of training data until sentence 3, and
   "population minimiser" / "exact empirical field" are opaque. The explainer's strength (why it
   matters first) is missing.
   Rewrite: "A flow-matching model that fits its finite training set perfectly reproduces training
   examples, which matters when those examples are copyrighted, medical or personal. In practice the
   field that is sampled is modified: labels are noised during training, guidance is added at
   sampling time, and conditions are composed. We ask which of these modifications, applied to the
   perfectly fitted field (the exact minimiser of the training loss for a fixed training set), can
   make its samples differ from the training examples."

2. **No plain picture for the central dichotomy (two fields vs three)** - main.tex:192-195 (also
   abstract 119-125, conclusion 1371-1379)
   Original: "Combinations of two fields only reweight the training examples. Three fields can blend
   them. At a tie of two examples ... this needs a specific sign pattern."
   Why: This is the headline, but the reader gets no intuition for *why* the count and signs matter.
   The proofs have one (Step 2: the tie repels unless the combined covariance trace turns negative);
   one sentence of it in the intro would make it click.
   Rewrite (add after line 195): "Intuitively, a point midway between two training examples is
   unstable for the exact field, like a ball balanced on a ridge: any small offset sends the
   trajectory to one side, so almost no trajectory ends there. Subtracting a field that is less
   decided between the two examples than the fields that are added can turn this ridge into a
   valley, and a positive fraction of trajectories then ends at the midpoint."

3. **"Three fields" is never counted for the reader** - main.tex:119, 147-148, 221-223
   Original: "Composition, guidance applied to the label-averaged field, combines three fields"
   Why: A newcomer reads "guidance applied to an average" and cannot see three fields. The count is
   the paper's main organising idea.
   Rewrite: "The conjunction of two conditions combines three exact fields: the two conditional
   fields are added and the unconditional field is subtracted, (1+w)(v_a+v_b)/2 - w v_unc."

4. **Core vocabulary used before definition** - "source" fig:unrolled caption main.tex:156;
   "atom(s)" main.tex:254, 275; "prior(s)" main.tex:114, 210; "support" main.tex:273; "blend"
   main.tex:119; "circumcentre" main.tex:223
   Why: The teaser caption ("Where each source ends") and the intro table assume these. Without them
   a newcomer cannot read Figure 2 or Table 1, which are exactly what a skimmer looks at first.
   Rewrite (one short paragraph at the start of the Introduction or end of its first paragraph):
   "Throughout, a *source* is the initial noise point x_0 of a sampling trajectory and its
   *endpoint* is where the trajectory ends at t=1. Each training example is an *atom*, a point mass
   of the endpoint law. Every field we study is built from exact fields that weight the training
   examples by a probability vector, its *prior*. A *blend* is an endpoint that is not a training
   example but an affine combination of several, such as their midpoint (in general, the
   *circumcentre*, the point equidistant from them). The *support* of the endpoint law is the set of
   points it can end on."

5. **"Boundary marker" is undefined and reads as hedging** - main.tex:128, 308
   Original: "We therefore present the composition as a boundary marker, not a practical mechanism."
   Why: A reader cannot tell what boundary or why "therefore". The intended meaning (composition
   shows where the guarantee ends, but we do not claim trained samplers produce blends) is fine and
   honest, but must be said plainly.
   Rewrite: "Composition therefore marks the limit of the guarantee: it is the only operation studied
   here that can create blends at the exact optimum, but we do not claim that trained samplers
   produce them."

6. **Abstract sentences that a newcomer cannot parse** - main.tex:113-119, 122-125
   Original: "So do every fixed combination of two such fields, which includes negative prompting by
   substitution, and guidance with a nonnegative bounded schedule of bounded variation. For
   guidance, the analogous statement was known for the stochastic sampler, and for a fixed strength
   every trajectory of the flow was known to converge, possibly to a point that is not a training
   example." / "At a tie of two examples, a point equally close ... strictly between those of the
   added fields." (52 words)
   Why: Grammar slip ("So do every" -> "So does"), stacked qualifiers, and a prior-work sentence in
   the middle of the results. "Negative prompting by substitution" and "bounded variation" are not
   abstract-level terms.
   Rewrite: "The same holds for any fixed combination of two such fields, which covers classifier-free
   guidance, guidance whose strength varies in time, and negative prompts used in place of the
   unconditional field." Move the prior-work sentence to the introduction. Split the tie sentence:
   "Call a point a tie of two examples if it is equally close to both and closer to them than to any
   other example. At such a tie, a blend requires subtracting a field that is less decided between
   the two examples than the fields that are added."

7. **Threshold stated without its practical meaning** - main.tex:120-122 (abstract), 148-149
   (overview caption)
   Original: "For two examples with prior log-odds +-2B this happens exactly when the guidance
   strength exceeds 1/sinh^2 B"
   Why: B is undefined there, and the reader is not told what the formula implies. The paper itself
   gives the plain reading at line 987-989 ("the more confidently each condition identifies its own
   example, the smaller the guidance at which their conjunction blends them"); it should be in the
   abstract.
   Rewrite: "For two examples, each favoured by one condition with confidence B (prior log-odds
   2B), a blend occurs exactly when the guidance strength exceeds 1/sinh^2 B, roughly 4e^{-2B}: the
   more confidently each condition picks its own example, the weaker the guidance needed to blend
   them."

8. **"Technique" paragraph is unreadable at the intro stage** - main.tex:251-267
   Original: "...a blow-up at the scale (1-t)^2 with a Lyapunov--Perron graph turns this failure
   into the spectral criterion. ... a signed second moment of a signed measure with unit mass and zero
   mean. A quadratic that vanishes at the extreme means bounds it whenever no inner prior is
   subtracted."
   Why: Six specialist terms in four sentences, before Section 4 defines anything. It interrupts the
   path from contributions to the practical reading.
   Rewrite: keep the first two sentences (two-step template) and replace the rest with "Guidance
   needs a separate energy bound because it subtracts a field. The composition is exactly where the
   second step fails; zooming in on the tie at the scale (1-t)^2 turns this failure into the
   spectral criterion. Section 4 gives the details." Move the last three sentences to the proof
   strategy paragraph (line 568).

9. **Theorem lead-ins missing or purely technical** - main.tex:596-599 (Thm posmix, no lead-in),
   668-671 (Prop cfgatom), 862-876 (Thm spectral), 1084-1087 (Prop regular)
   Original: subsection title followed directly by the theorem; "For w>0 its prior coefficients have
   opposite signs, so Theorem~\ref{thm:posmix} does not apply."
   Why: Each theorem should be preceded by one sentence saying what it means. The explainer's "read
   the formula" habit is absent here.
   Rewrites:
   - before Thm posmix: "The first result says that averaging exact fields with positive weights,
     which models a network that blurs nearby labels, can change how often each training example is
     returned but never returns anything else."
   - before Prop cfgatom: "Classifier-free guidance subtracts the unconditional field, so the
     previous argument does not apply; the next result shows that guidance of any fixed nonnegative
     strength still ends on training examples."
   - before Thm spectral: "In more than one dimension the question becomes whether the tie attracts
     trajectories from every direction; the sign of each eigenvalue of a signed covariance matrix
     answers it."
   - Prop regular, add: "In practice, a network that stays smooth up to the end of sampling can only
     approach a training example, never land exactly on it."

10. **Long, stacked sentences in the practice paragraph and conclusion** - main.tex:308-314
    ((iii), 61 words), 1372-1375 (45 words), 186-191 (47 words)
    Original: "Among the operations studied here with strictly positive priors, only combining three or
    more fields changes the support of the exact law without adding noise (averaging hard-label
    fields can, at a symmetric tie, Section~\ref{sec:posmix}), and at a tie of two examples only when
    a field less decided between them is subtracted."
    Why: The "What this means in practice" paragraph is the most valuable part for newcomers but
    buries its point under parentheses and qualifiers.
    Rewrite: "(iii) Composition is the only exception. Among the operations studied here, only a
    combination of three or more fields can, without added noise, make the exact field return
    something other than a training example. At a tie of two examples it does so only if a less
    decided field is subtracted. (Averaging hard-label fields can also do it, but only at a symmetric
    tie.)" Conclusion 1372-1375: split into "Label noise and label averaging reweight the training
    examples. So does every fixed combination of two exact fields, including guidance with a fixed or
    bounded time-varying strength and negative prompts used in place of the unconditional field. In
    all these cases every trajectory converges, and almost every one ends on a training example."

Also worth fixing (lower rank):
- Title (main.tex:89-90): "Keep ... on Its Training Set" is ambiguous (keeps what? the samples) and
  hides the answer. Option: "Which Sampler Interventions Stop a Perfectly Fitted Conditional Flow
  from Copying? Two Fields Cannot, Three Can". If a question title is kept, at least "Which
  Interventions Move a Conditional Flow's Samples off Its Training Set?"
- Overview caption (main.tex:141-149): lists theorem numbers for every row; a newcomer needs the
  sentence "all keep the samples on training images; only composition can produce a blend" first,
  with references after.
- Contribution 5 (main.tex:237-243, 38-word sentence): add the practical reading "so whether a
  trained sampler blends depends on whether the network resolves a very thin layer around the tie;
  standard networks do not".
- "label averaging" (main.tex:179, 108): say once that it models "a network that cannot tell nearby
  labels apart and so outputs the average of their fields".
- "exact field" first prose use (main.tex:174-177): add "the field a perfectly trained network would
  learn".

### What already works (keep)
- Intro para 2 (main.tex:186-191): names two readers (practitioner, auditor) and what each needs.
  This is exactly the "why it matters" move; consider moving it before the literature paragraph.
- "What this means in practice" (main.tex:292-318): (i)-(iv) give practical meanings and honest
  limits (leakage, predictability, fixed-N caveat). Keep the structure; just split sentences.
- The definition of a tie given in-line at first use (main.tex:122-123, 194-195).
- The plain sentence at main.tex:987-989 ("the more confidently each condition identifies ...").
- Contribution 1 honestly states "This is not a new result" (main.tex:202-204).
- Limitations (main.tex:1340-1365) are concrete and honest; Section 6 intro (main.tex:1124-1129)
  clearly says numerics check, not prove.
- fig:unrolled (teaser) is an excellent picture; it only needs "source" defined.

---------------------------------------------------------------------------------------------------
## Paper B: "Chosen Early, Landed Late: When Trained Diffusion Models Copy Their Training Images"

### Top 10 issues (ranked)

1. **The key quantity (radial ratio) is defined in one 49-word sentence** - main.tex:80-83 (abstract),
   128-131 (intro), 196-197 (contributions)
   Original: "It stays away when the radial ratio approaches one fast enough; this ratio measures how far
   the predicted clean image still lies out along the state's own offset from the training image, in
   units of the state's distance, so a value of one means no pull toward the image."
   Why: Three nested spatial notions (offset, along, in units of) in one breath; a newcomer cannot
   form a picture. It is repeated three times with different wording.
   Rewrite (abstract): "It stays away when the network stops pulling it in: we measure this by the
   radial ratio, the fraction of the state's distance to the training image that remains in the
   network's predicted clean image. A ratio of one means no pull toward the image." Use the same
   sentence verbatim in intro and contributions.

2. **"Relative error" and "exact denoiser" not defined in plain words in the abstract** -
   main.tex:79-81, 89
   Original: "A trajectory reaches a training image when the error of its predicted clean image stays
   a fixed fraction below its distance to that image."
   Why: Error relative to what? The reader does not know there is a reference (the exact posterior
   mean) until the intro.
   Rewrite: "Let the error be the distance between the network's predicted clean image and the one
   the perfectly fitted (exact) denoiser would predict. A trajectory reaches a training image when
   this error stays a fixed fraction below the trajectory's distance to that image; the error itself
   may be large."

3. **The intro lacks the one analogy that the title promises** - main.tex:136-141
   Original: "To see the condition at work on real models, we swap the trained denoiser ..."
   Why: "Chosen early, landed late" is an aviation picture, but the text never uses it, so the title
   reads as wordplay. One sentence makes the two-decision structure memorable.
   Rewrite (insert before line 136): "Copying thus involves two decisions, much as a flight commits
   to an airport long before it is known whether it touches down on the runway: which training image
   the trajectory heads for, and whether it actually reaches it. Our experiments show that the two
   are made at different noise levels."

4. **Overstated: "explains landing"** - main.tex:94-95 (abstract), 1071 (conclusion), 1011-1012,
   1079
   Original: "The relative error explains landing; it does not detect copies better than ..."
   Why: Section 4.4 says the measurements "describe the mechanism ... They are not an independent
   test of it: part of the separation near the end is bookkeeping" (main.tex:864-867), and that 34 of
   41 off-atom samples never violate the hypothesis of (b) on the finite schedule (918-920).
   "Explains" claims more than the evidence; a newcomer will read it as a validated causal account.
   Rewrite: "The relative error describes how landing happens and is consistent with the theorem; it
   is not an independent test, and it does not detect copies better than ..."

5. **Overstated: "never copies"** - main.tex:167 (teaser caption), 1066 (conclusion)
   Original: "the public model, trained on all 50000 images, which never copies"
   Why: Evidence is 0 copies in 200-500 samples under one criterion and one sampler. A careful
   reader will object.
   Rewrite: "the public model, trained on all 50000 images, none of whose samples copied a training
   image in our runs".

6. **Abstract results sentences are hard to decode** - main.tex:90-94
   Original: "...approach one from sigma~0.14. Handed the exact denoiser's state, the memorising model
   lands every sample from every swap level, while the public model lands half of them only from
   sigma~0.5."
   Why: sigma is never introduced (direction and range unknown), "swap level" is undefined in the
   abstract, and "lands half of them only from" is ambiguous.
   Rewrite: "(Noise level sigma runs from 80, pure noise, down to 0.002, nearly clean; sigma~1 is
   mid-way.) ... When the exact denoiser runs first and the network takes over at a given noise
   level, the memorising model reaches a training image whatever that level, whereas the public model
   does so for half of the samples only if it takes over at sigma 0.5 or below."

7. **Teaser and overview captions are too long and mix definitions with results** -
   main.tex:166-187 (~300 words), 146-159
   Original (teaser): "...black where the tile is that training image (closer to it than a third of
   its distance to the output's second-nearest one). ... a swap at s is drawn at sigma=s ..."
   Original (overview): "Three marks on the noise axis, drawn against the five marked levels of the
   18-step schedule (sigma=80, 5.3, 1.9, 0.59 and 0.002), organise the results."
   Why: The teaser is the first thing a reader looks at; its message (same noise, same image chosen,
   one model lands and the other does not) is buried after the plotting conventions. "latent" is
   undefined.
   Rewrite: open the teaser caption with the message: "The same starting noise (latent) is sampled by
   a model that does not copy (top) and one that does (middle). Both head for the same training
   image early (the exact prediction, blue, settles on it by sigma=1.9), but only the 500-image model
   reaches it." Then the plotting conventions; move the off-atom criterion and drawing details to
   the main text. Overview: "Three noise ranges organise the results: where the image is chosen,
   where a copy becomes visible in the denoiser output, and where the state lands."

8. **Contributions use terms defined only later** - main.tex:202-208, 215-224
   Original: "At an identifying label, a learned endpoint lies within limsup (1-t)|Delta| ..." /
   "The contraction that the relative error leaves over sigma in [0.002,0.585] has median 1.75 ..." /
   "The reverse swap, with the exact field first, ..."
   Why: "identifying label", "contraction", "reverse swap" and "Heun bound" appear before
   definition; the numbers 1.75 / 0.68 have no scale.
   Rewrite: "At a label that belongs to a single training example, the endpoint misses that example
   by at most the limiting size of the scaled error ..." and "Summed over the late noise levels, the
   pull toward the image (the contraction, 1 minus the relative error) is about 2.5 times larger for
   copies than for new samples (median 1.75 against 0.68) on a 2000-image model." Define "reverse
   swap" where the two swap directions are named (line 136-140).

9. **Section 4 opening and Theorem 4.1 lead-in are notation, not meaning** - main.tex:462-466,
   468-471
   Original: "...a field affine in space can have vanishing hard-conditioned loss and endpoint law
   N(a,I_d) through a late amplification (Proposition ...), while an explicit risk-transfer condition
   restores a finite-time bound" / "Write m* = sum_j w_j x^j for any posterior mean with continuous
   weights ..."
   Why: The practical claim (low training loss does not guarantee copying or not copying) is hidden
   in jargon, and the main theorem is preceded only by notation.
   Rewrite: "Both statements concern the error along the sampled trajectory, not the training loss:
   a network can reach arbitrarily small training loss and still produce samples spread around the
   training image, because the loss weights late times too little (Proposition ...)." Before the
   theorem: "The theorem compares, at each moment of sampling, two distances: how far the network's
   prediction is from the exact one, and how far the state still is from the training image. If the
   first stays a fixed fraction of the second, the state is pulled in; if the network's pull fades
   fast enough, it is not."

10. **Undefined technical names a newcomer cannot resolve** - "EDM", "Heun sampler" main.tex:85-86;
    "posterior mean" main.tex:126, 447-449; "Mimg" main.tex:663; "latent" main.tex:140
    Why: Each is one phrase away from being understood.
    Rewrites: "EDM, a widely used diffusion model family (Karras et al., 2022)"; "the deterministic
    second-order (Heun) solver that EDM uses for sampling"; "the posterior mean m*, the average of the
    training images weighted by how likely each is to have produced the current noisy state; this is
    what a perfectly fitted network predicts"; "10 million training images shown (10 Mimg)"; "a latent,
    the Gaussian noise from which a sample starts".

Also worth fixing (lower rank):
- Conclusion "Implications" (main.tex:1071-1077, 55-word sentence): split into one sentence per
  stage ("Methods against memorisation can act at two stages. At medium noise ... At late noise ...").
- EDM section intro (main.tex:672-674): "These are not the quantities of Theorem ... in the coordinates
  t=1/(1+sigma) ...; we did not record those." Good honesty, but say the consequence: "so the EDM
  measurements illustrate the theorem in its EDM form (Proposition ...), not the flow-matching form."
- Title: good hook. "When" slightly promises more than one dataset supports; acceptable for a title,
  but the abstract should say "on CIFAR-10" early (it does at line 86).

### What already works (keep)
- Abstract lines 75-78: states the puzzle (exact optimum always copies, trained models sometimes do
  not) and the question in plain words before any formula. Model of the target voice.
- Intro para 1 with the concrete 96% vs 0% contrast (main.tex:111-113).
- Intro para 2 (main.tex:118-122): three uses of the answer, with an honest "we do not test any such
  method here".
- "The condition is relative: the error may be large while the state is far ..." (main.tex:131-132)
  and Theorem 4.1's follow-up "Part (b) does not ask for a small error" (main.tex:493): exactly the
  plain-reading habit wanted.
- Swap section opening (main.tex:688-693): explains what each direction can and cannot tell,
  including "by construction".
- "We do not claim a better detector" (main.tex:229-233) and the Limitations/Planned experiments
  section, including the refuted prediction: honest and clear.
- fig:mechanism (main.tex:506-518): the 1D picture of copy / still copy / stop short is the best
  newcomer figure in either paper.

---------------------------------------------------------------------------------------------------
## Tom tat (tieng Viet)
Bai B da gan voi giong van mong muon; can sua chu yeu dinh nghia "radial ratio" (mot cau 49 tu), lam
gon caption teaser, va ha giong hai cho noi qua ("explains landing", "never copies").
Bai A chinh xac nhung nguoi moi gap khoang 10 thuat ngu chua dinh nghia (source, atom, prior, blend,
circumcentre, conjunction, boundary marker...) truoc khi biet vi sao cau hoi quan trong.
Viec dang lam nhat cho A: mo dau abstract bang chuyen copy du lieu, dem ro "ba truong" la gi, va them
mot cau hinh anh "dinh doc / thung lung" de giai thich vi sao hai truong giu, ba truong co the tron.
