# Reader-evaluation questions

A hand-curated set of 20 questions to check the v0 widget against the goals in
`CLAUDE.md`: answers should be (a) accurate to the paper's claims, (b) calibrated
to the audience implied by the question's phrasing, (c) not over-hedged.

For each question, run it against the deployed widget, then mark the answer
against the rubric at the bottom.

## Audience tier — journalist / curious practitioner

1. What's the main finding of the paper, in plain English?
2. Why look at crypto specifically? What about this market makes it interesting?
3. Are crypto returns just speculation, or is there real risk-and-return going on?
4. The paper says crypto-equity correlations are rising over time — is that a
   small effect or a big one? Should an investor care?
5. What's the sample? How many coins, what time period, what data source?

## Audience tier — MSc finance student / quant practitioner

6. Walk me through what IPCA is at a high level. I know Fama–French style factor
   models for equities but not IPCA.
7. What's the difference between systematic mispricing and risk compensation in
   the IPCA setup? Which parameter is which?
8. What's a "pure-alpha portfolio" in this paper, and how does it perform?
9. Which characteristic groups drive mispricing most? Which drive risk
   compensation? Are these the same?
10. How robust are the results to volatility scaling? Does that change the
    headline?
11. Does the paper compare individual exchanges? What's the takeaway?

## Audience tier — PhD finance student / academic

12. Lay out the IPCA estimation. What does the alternating least squares loop
    look like — what do you iterate, and what's the first-order condition for
    the latent factors $f_{t+1}$?
13. How is the Wald-type bootstrap test for $\Gamma_\alpha = 0$ constructed?
    What's the null and what does rejection mean economically?
14. In the augmented IPCA with equity factors, what does $W_\delta$ test, and
    how do they get its p-value?
15. The paper claims a 5–67% reduction in predictive $R^2$ when alphas are
    restricted to zero, depending on the factor model. Where in the paper does
    that range come from?

## Figure / table router checks

16. Show me Figure 5 and explain what each panel is showing.
17. What does Figure 1c specifically — the speculative demand panel — tell me?
18. Walk me through Table 2. What's being compared, and what's the bottom line?
19. Appendix Figure 6: what's it adding beyond what the main text already says?

## Honesty / scope check

20. Does the paper say anything about what regulators should do, or about CBDCs?
    (Expected: a clean "no, that's outside the paper's scope" — not a fabricated
    answer.)

---

## Rubric (per answer)

For each, mark:

- **Accuracy** — does the answer match what the paper actually says? Spot-check
  any specific number against the source (paper.md or the table .tex).
- **Calibration** — does the depth match the question's tier? A journalist
  question shouldn't get a derivation; a PhD question shouldn't get a one-liner.
- **Hedging** — count meta-disclaimers ("based on the paper", "I believe",
  "while the paper suggests"). One or two is fine; more than that is over-hedged.
- **Figure attachment** — for Q16–19, did the right image(s) arrive? Was the
  description grounded in what's actually visible vs paraphrased from the
  caption?
- **Honest refusal** — for Q20, did the model decline cleanly rather than
  fabricate?

Pass criterion for v0: 17 of 20 marked OK across all four columns.
