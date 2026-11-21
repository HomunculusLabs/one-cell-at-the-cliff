# Second opinion — claude.ai fable 5.2 (web instance, owner-pasted 2026-11-21)

PROVENANCE: owner-supplied document (Discord). NOT one of our dispatches — a
claude.ai-hosted fable 5.2 that independently rebuilt the network from the raw
connectome tables in its own code (no torch, no access to our release assets)
and ran its own 56-cell deletion scan at fixed base gain, 8 seeds/arm.
Converges with our API-dispatched round-2 referee on: silent twin (0.0004 vs
carrier 0.39 ON THE CUT BASE, 3 input edges), Methods weight-rule misstatement,
fragility (1% jitter, 3-syn floor). NEW hits we must own: (1) Alstott et al.
2009 PLOS Comput Biol — lesion-location prior art our novelty sweep missed
(not on arXiv; outside our windows); (2) both our referee rounds were the same
model family (fable) — family-internal review. Its scan: carrier unique
UPWARD mover (.72, 8/8); ~1/3 of active-cell deletions move the readout
(1 up, 9 down, 25 unchanged); silent deletions = noise floor .42 ± .05.
Its stated limits: one run, 8 seeds, fixed gain (not per-arm re-matching),
own reimplementation. Note: it claims raw traces are not in the repo — they
ARE, as release assets (v0.1-lineage); its sandbox could not run torch.

---

# Second opinion: One cell at the cliff

Nov 21, 2026 · @No

## Verdict

**Don't send it yet.** The simulations in [one-cell-at-the-cliff](https://github.com/HomunculusLabs/one-cell-at-the-cliff) are real and reproducible, but the control the paper is named after is broken. What survives is a modest result about one model, not a discovery about flies (the draft itself says as much).

## What holds up

I rebuilt the network from the raw connectome tables in my own code, with my own noise, and got her headline numbers.

- **Structure:** all stored pins match exactly (21,809 cells, 647,953 edges, the same 25 deleted cells).
- **Dynamics:** the 24-cell-cut base gave 3/16 seeds (hers 28%), removing the "carrier" DNp33-L gave 16/16 (hers 97%), and the 23-cell cut gave 0/16 (hers 0/82).
- **Citations:** two of her 2026 references that I looked up do turn up on arXiv ([ApproxBrain](https://arxiv.org/pdf/2611.06929), [FlyHack](https://arxiv.org/pdf/2610.13018)), and the ApproxBrain figures she quotes agree with its abstract. I couldn't find the Habib preprint she calls her closest prior art.

## What doesn't

1. **The "mass twin" is a silent cell.** On the cut base it fires at 0.0004 against the carrier's 0.39, and it has 3 input edges. Deleting a cell that isn't firing is a no-op in a rate model, so "identity, not mass" as presented reduces to "deleting an active cell does more than deleting an inactive one." Her notebook calls it the "SILENT twin"; the draft, claim map and referee report never mention it.
2. **The Methods section misstates the model.** It says weights are in-degree normalized; the run code uses raw log synapse counts, and her own notebook says so. Her six verification gates check that numbers match the ledger, not that statements are true.
3. **The effect is fragile, by her own data.** A 1% weight jitter swings the base from 0/16 to 15/16, and dropping 3-synapse pairs erases the effect. The readout is one correlation between 51 flexor and 6 extensor motor neurons on one side.
4. **Novelty is overstated.** It rests on ten arXiv keyword queries. A 2009 PLOS Computational Biology paper ([Alstott et al.](https://pmc.ncbi.nlm.nih.gov/articles/PMC2688028)) already tied a virtual lesion's impact to where in the network it lands.
5. **"Preregistered" can't be verified.** The public repo's history is three commits from the morning of 21 November 2026.

## The control she didn't run

The carrier survives a fair control, but it is not alone at the cliff. I deleted 56 single cells one at a time from the same base (8 seeds each, base gain). The number is mean right-tibia duty, her readout; silent-cell deletions set the noise floor at .42 ± .05.

| Deleted cell | Cells | Result (mean right-tibia duty) |
| --- | --- | --- |
| Silent cohort cells, including her twin (.36) | 13 | All within noise (.34–.49) |
| Carrier | 1 | .72, 8/8 seeds |
| Other active cells: 13 cohort, 12 matched to the carrier on rate × output weight, 10 random | 35 | 1 up (.62), 9 down (five below .14), 25 unchanged |

Seven barely-active cells are left out; none stood out. The carrier is the strongest upward mover and unique among its 34 cohort siblings. But roughly a third of active cells move this readout when deleted, mostly killing it.

## Before sending

Three fixes turn this into an honest "reproducible model result plus a better control" paper.

- Report the twin's firing rate and replace it with activity-weighted twins.
- Add the single-cell null distribution.
- Fix the Methods sentence.

## Reviewer fit and the limits of this check

I can't vouch from memory for who Sauers is or what he's qualified in. This needs someone who builds connectome-constrained models of the fly nerve cord; an AI person can judge the agent's process but not the neuroscience. The existing referee round was another instance of this same model, so it wasn't independent either, and it missed the first two problems above.

My check has limits: one run, 8 seeds per arm, fixed gain rather than her per-arm re-matching. I couldn't run her PyTorch code here, and her raw traces aren't in the repo.
