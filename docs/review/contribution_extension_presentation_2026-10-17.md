# Presentation review

Reviewed `contribution_extension_proofs_2026-10-17.tex` as supplied on 17 October 2026. Read-only source inspection; no computations or literature review.

The composition section explicitly fixes a constant guidance strength `w >= 0` before Theorem 2. The threshold, closed zero basin, Gaussian pushforward, and tensor product conclusions are stated in an order supported by their proofs. No theorem-surface rewrite is needed.

Minimal clarifications:

1. In the robustness proof, specify that `J_s` is the Jacobian of the flow **from `s_0` to `s`**, and that `E` and `B` in the following volume argument are subsets of the state space at `s_0`. The integral formula and final transfer to time zero then agree unambiguously. As written, “source point” and “initial ball” could suggest time zero, whose Jacobian also has a finite initial-time contribution.
2. The scalar construction introduces labels, bandwidth, and exact conditioned means without explicitly specifying its label observation model. Add the same uniform atom weights, label `y(a)=a`, and Gaussian label noise of standard deviation `h` that appear in the tensor corollary. This makes the asserted shifts `+/- h^{-2}` self-contained.
3. In the tube lemma's last sentence, qualify “positive-mass endpoint submeasure” by the source condition: the source must give positive mass to the open inverse interval (as the standard Gaussian does). A nonempty open interval guarantees positive Lebesgue measure, but arbitrary absolutely continuous sources need not charge it.
4. In the abstract, replace “full-dimensional training support” with “training support of full affine span,” matching the tensor corollary. A finite support is not full-dimensional in the measure/interior sense.

The tube lemma needs no oddness or requirement that `0` lie between its barriers: bounded `u` implies `x=u/beta -> 0`. Its stated bounded locally Lipschitz hypotheses and eventual inward signs support the claimed open basin. The tensor example explicitly has full affine span and its off-training atoms have first coordinate zero.

## Editor disposition

All four clarifications were applied. The scalar section explicitly fixes a constant nonnegative guidance strength. Page breaks were adjusted to keep the principal robustness statement and tensor statement intact. Final source/PDF bindings and checks are in `contribution_extension_verification_2026-10-17.json`; this disposition is the editor's record, not an additional independent mathematical vote.
