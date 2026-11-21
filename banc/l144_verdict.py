"""L144 verdict: B-cert (raw_l142 B29, cutwA+cutng25) BEFORE any B30
read, then anchors/P4/B30 table/grid/H-branches/pooled. Criteria
VERBATIM L118-L131 (metric helpers copied VERBATIM from the certified
l142_verdict.py; B-cert vs results_l142.json proves the copy). PREREG
l144/PREREG.md."""
import json
import math

import numpy as np

WIN, DT = 6000, 0.01
SEGB = [(0, 2000, 0.7), (2000, 4000, 1.4), (4000, 6000, 0.7)]
MEAS0 = 500
B26 = list(range(3001, 3017))       # l135 FRESH (cert chain)
B25 = list(range(2901, 2917))  # context batch (l133)
B24 = list(range(2801, 2817))  # context batch (l131)
B21 = list(range(2501, 2517))  # context batch (l126)
B29 = list(range(3301, 3317))  # l142 FRESH (B-cert + pooled)
B30 = list(range(3317, 3333))  # L144 FRESH
B27 = list(range(3101, 3117))  # L141 context (sil1110 on intact closure)
PAIRS = ["Ti", "Tr", "Ta", "Sr", "Pr"]
PREF = {"Ti": ("f", "e"), "Tr": ("f", "e"), "Ta": ("a", "b"),
        "Sr": ("a", "b"), "Pr": ("a", "b")}
TS = np.arange(499, WIN, 10)
Z = 1.959963984540054


def S_of(a, b):
    sa, sb = a.std(), b.std()
    return float(-np.corrcoef(a, b)[0, 1]) if sa > 1e-6 and sb > 1e-6 else float("nan")


_SM = {}


def s_arrays(raw, a, s, pk):
    key = (id(raw), a, s, pk)
    if key not in _SM:
        ag, bg = PREF[pk]
        tr = {c: raw[f"{pk}_{c}_{a}_{s}"][:WIN]
              for c in (f"{ag}L", f"{ag}R", f"{bg}L", f"{bg}R")}
        SL = np.full(WIN, np.nan)
        SR = np.full(WIN, np.nan)
        for t in TS:
            SL[t] = S_of(tr[f"{ag}L"][t - 499:t + 1], tr[f"{bg}L"][t - 499:t + 1])
            SR[t] = S_of(tr[f"{ag}R"][t - 499:t + 1], tr[f"{bg}R"][t - 499:t + 1])
        _SM[key] = (SL, SR)
    return _SM[key]


def duty_seeds(raw, a, seeds, pk):
    """Rounded per-seed duty values (the l109/l111/l113 rounding-path atom)."""
    L, R = [], []
    for s in seeds:
        SL, SR = s_arrays(raw, a, s, pk)
        q07 = np.zeros(len(TS), bool)
        for a0, b0, f in SEGB:
            if f == 0.7:
                q07 |= (TS >= a0 + MEAS0) & (TS < b0)
        L.append(round(float(np.nanmean(SL[TS[q07]] >= .25)), 3))
        R.append(round(float(np.nanmean(SR[TS[q07]] >= .25)), 3))
    return np.array(L), np.array(R)


def side_k(raw, a, seeds, pk):
    L, R = duty_seeds(raw, a, seeds, pk)
    return dict(kL=int((L >= .5).sum()), kR=int((R >= .5).sum()),
                meanL=round(float(L.mean()), 3), meanR=round(float(R.mean()), 3))


def wilson(k, n):
    p = k / n
    den = 1 + Z * Z / n
    c = p + Z * Z / (2 * n)
    r = Z * math.sqrt(p * (1 - p) / n + Z * Z / (4 * n * n))
    return (c - r) / den, (c + r) / den


# ---- L144 verdict (PREREG l144/PREREG.md): B-cert FIRST, then B30 ----
ARMS144 = ["full", "b65", "cutwA", "cutng25", "sil1110", "sil1110_wA"]
LADDER144 = [("0", "full"), ("24", "cutwA"), ("silF", "sil1110"),
             ("silW", "sil1110_wA"), ("25", "cutng25")]
z144 = np.load("l144/raw_l144.npz")
z142 = np.load("l142/raw_l142.npz")
z137 = np.load("l137/raw_l137.npz")
z135 = np.load("l135/raw_l135.npz")
z133 = np.load("l133/raw_l133.npz")
z131 = np.load("l131/raw_l131.npz")
z126 = np.load("l126/raw_l126.npz")
ar = json.load(open("l144/anchors_run.json"))
r142 = json.load(open("l142/results_l142.json"))

# ---- B-cert BEFORE any B30 read (L85 rule): machinery on raw_l142 B29
# for {cutwA, cutng25} == results_l142.json Ti table EXACT ----
bcert_fail = []
for a in ("cutwA", "cutng25"):
    want = r142["table"]["Ti"][a]
    got = side_k(z142, a, B29, "Ti")
    for kk in ("kL", "kR", "meanL", "meanR"):
        if got[kk] != want[kk]:
            bcert_fail.append((a, kk, got[kk], want[kk]))
assert not bcert_fail, ("B-cert FAIL (no B30 read)", bcert_fail[:5])
print("B-cert vs results_l142.json Ti table {cutwA,cutng25}: PASS")

# ---- P0 anchors (gate booleans ONLY, L59 rule) ----
p0 = dict(c0a144_pass=ar["c0a144_pass"], c0a144_max=ar["c0a144_max"],
          fc142_pass=ar["fc142_pass"], fc142_max=ar["fc142_max"],
          fc137_pass=ar["fc137_pass"], fc137_max=ar["fc137_max"],
          g_cutwA_stored_exact=ar["g_cutwA_stored_exact"],
          g_cutng25_stored_exact=ar["g_cutng25_stored_exact"])
p0["pass"] = bool(p0["c0a144_pass"] and p0["fc142_pass"] and
                  p0["fc137_pass"] and p0["g_cutwA_stored_exact"] and
                  p0["g_cutng25_stored_exact"])
print("P0 anchors (C0A-144 + FC-142 + FC-137 + gains):",
      "PASS" if p0["pass"] else "FAIL",
      f"(C0A {p0['c0a144_max']:.1e} | FC142 {p0['fc142_max']:.1e} | "
      f"FC137 {p0['fc137_max']:.1e})")

# ---- P4 health ----
af_mean = {a: round(float(np.mean([float(z144[f"af_{a}_{s}"]) for s in B30])), 6)
           for a in ARMS144}
af_range_ok = all(0.01 < float(z144[f"af_{a}_{s}"]) < 0.9
                  for a in ARMS144 for s in B30)
b65_band = 0.105056 <= af_mean["b65"] <= 0.113056
p4 = dict(af_range_ok=bool(af_range_ok), b65_band=bool(b65_band),
          af_mean=af_mean)
print("P4", json.dumps({k: p4[k] for k in ("af_range_ok", "b65_band")}))

# ---- B30 per-side duty table (5 pairs x 6 arms) ----
table = {}
for pk in PAIRS:
    table[pk] = {}
    for a in ARMS144:
        t = side_k(z144, a, B30, pk)
        lbL, ubL = wilson(t["kL"], 16)
        lbR, ubR = wilson(t["kR"], 16)
        t.update(lbL=lbL, ubL=ubL, lbR=lbR, ubR=ubR)
        table[pk][a] = t
print("---- B30 per-side duty table ----")
for pk in PAIRS:
    for a in ARMS144:
        t = table[pk][a]
        print(f"{pk} {a:11s} kL {t['kL']:2d}/16 meanL {t['meanL']:.3f} | "
              f"kR {t['kR']:2d}/16 meanR {t['meanR']:.3f}")

# ---- Ti grid classification (criteria VERBATIM L118-L131) ----
m0 = table["Ti"]["full"]["meanR"]
_, Rfull = duty_seeds(z144, "full", B30, "Ti")
_, RwA = duty_seeds(z144, "cutwA", B30, "Ti")
grid = {"meanR": {}, "kR": {}, "meanL": {}, "kL": {}, "legs": {}}


def _restore(t):
    return bool(t["meanR"] >= .45 and t["kR"] >= 12)


def _super(t):
    return bool(t["meanR"] >= .60 and t["kR"] >= 12)


def _partial(t):
    return bool(.35 <= t["meanR"] <= .50 and 3 <= t["kR"] <= 8)


cls = {}
for kk, a in LADDER144:
    t = table["Ti"][a]
    _, Rd = duty_seeds(z144, a, B30, "Ti")
    legs = dict(
        mean_paired_dR_vs_full=round(float((Rd - Rfull).mean()), 3),
        n_down_vs_full=int(((Rd - Rfull) <= -.20).sum()),
        mean_paired_dR_vs_wA=round(float((Rd - RwA).mean()), 3),
        n_down_vs_wA=int(((Rd - RwA) <= -.20).sum()),
        n_up_vs_wA=int(((Rd - RwA) >= .20).sum()))
    kill = (t["meanR"] <= m0 - .10) and (t["kR"] <= 4) and \
        (legs["mean_paired_dR_vs_full"] <= -.20)
    grid["meanR"][kk] = t["meanR"]; grid["kR"][kk] = t["kR"]
    grid["meanL"][kk] = t["meanL"]; grid["kL"][kk] = t["kL"]
    grid["legs"][kk] = legs
    cls[kk] = dict(arm=a, meanR=t["meanR"], kR=t["kR"], meanL=t["meanL"],
                   kL=t["kL"], kill=bool(kill), restore=_restore(t),
                   super=_super(t), partial=_partial(t), legs=legs)
    print(f"Ti {kk:>5s} ({a:11s}): meanR {t['meanR']:.3f} kR {t['kR']:2d}/16 "
          f"| meanL {t['meanL']:.3f} kL {t['kL']:2d}/16 | dR_full "
          f"{legs['mean_paired_dR_vs_full']:+.3f} dR_wA "
          f"{legs['mean_paired_dR_vs_wA']:+.3f} n_up_wA "
          f"{legs['n_up_vs_wA']:2d}/16 -> "
          f"{'KILL' if kill else 'no-kill'}"
          f"{'/RESTORE' if _restore(t) else ''}"
          f"{'/SUPER' if _super(t) else ''}"
          f"{'/PARTIAL' if _partial(t) else ''}")
grid["m0"] = m0

# ---- H-branch verdicts (registered BOTH directions) ----
c_silW, c_silF = cls["silW"], cls["silF"]
dR_scale = 0.075  # L141 clamp reference scale (silrand spread, intact)
fires = bool(c_silW["super"] or c_silW["restore"])
moved = abs(c_silW["legs"]["mean_paired_dR_vs_wA"]) > dR_scale
if fires and moved:
    h_edge, h_act = False, True
    h_note = ("H-ACT: sil1110_wA flips (substrate-gated activity "
              "carriage) — the wA-base flip needs only 1110's SILENCE")
elif fires and not moved:
    h_edge, h_act = False, True
    h_note = ("H-ACT* (degenerate leg: class fires with |dR_wA| <= .075 "
              "— band-edge draw, DISCLOSE, do not force (L55/L109))")
elif not fires and not moved:
    h_edge, h_act = True, False
    h_note = ("H-EDGE: sil1110_wA stays in cutwA's band with |dR_wA| <= "
              ".075 — edges carry it on this base too; two-factor law's "
              "cleanest statement (same substrate, activity-vs-edges)")
else:
    h_edge, h_act = False, False
    h_note = ("INTERMEDIATE: no class flip but |dR_wA| > .075 — "
              "disclosed, no class forced (L109)")
p1 = dict(arm="sil1110", dR_vs_full=c_silF["legs"]["mean_paired_dR_vs_full"],
          in_scale=bool(abs(c_silF["legs"]["mean_paired_dR_vs_full"])
                        <= dR_scale),
          meanR=c_silF["meanR"], kR=c_silF["kR"],
          note="P1 replication leg (L141 B27: dR -.088, in full's band)"
          if abs(c_silF["legs"]["mean_paired_dR_vs_full"]) <= dR_scale
          else "P1 FAILS: B30 anomalous for clamps — read legs against it")
p3 = dict(arm="sil1110_wA", Ti_meanL=c_silW["meanL"], Ti_kL=c_silW["kL"],
          cutwA_Ti_meanL=cls["24"]["meanL"], cutwA_Ti_kL=cls["24"]["kL"],
          note="P3 descriptive: crossed-law Ti_L read on the clamp arm")
print("H-EDGE" if h_edge else "H-ACT" if h_act else "INTERMEDIATE", "|",
      h_note)
print("P1", json.dumps(p1))
print("P3", json.dumps(p3))

# ---- L141 B27 context (stored raw recompute, beside the grid) ----
ctx = {}
for a in ("full", "sil1110"):
    t27 = side_k(z137, a, B27, "Ti")
    _, R27 = duty_seeds(z137, a, B27, "Ti")
    ctx[a] = t27
_, R27f = duty_seeds(z137, "full", B27, "Ti")
_, R27s = duty_seeds(z137, "sil1110", B27, "Ti")
ctx["paired_dR"] = round(float((R27s - R27f).mean()), 3)
print("L141 B27 context (raw_l137):", json.dumps(ctx))

# ---- pooled reads (L90 full-precision Wilson, unrounded) ----
def pooled(raws, a, batches, pk="Ti"):
    Ls, Rs = [], []
    for raw, b in zip(raws, batches):
        L, R = duty_seeds(raw, a, b, pk)
        Ls.append(L); Rs.append(R)
    R_ = np.concatenate(Rs); L_ = np.concatenate(Ls)
    kR, kL = int((R_ >= .5).sum()), int((L_ >= .5).sum())
    lbR, ubR = wilson(kR, len(R_)); lbL, ubL = wilson(kL, len(L_))
    return dict(kR=kR, n=len(R_), lbR=lbR, ubR=ubR, kL=kL, lbL=lbL, ubL=ubL,
                meanR=round(float(R_.mean()), 3),
                meanL=round(float(L_.mean()), 3))


pooled_ng25 = pooled([z131, z133, z135, z142, z144], "cutng25",
                     [B24, B25, B26, B29, B30])
pooled_wA = pooled([z126, z131, z133, z135, z142, z144], "cutwA",
                   [B21, B24, B25, B26, B29, B30])
print("pooled cutng25 B24+B25+B26+B29+B30:", json.dumps(pooled_ng25))
print("pooled cutwA  B21+..+B30:", json.dumps(pooled_wA))

# ---- disclosures + sanity ----
san = dict(
    full_class_batch_drawn=dict(meanR=m0, kR=table["Ti"]["full"]["kR"],
        note="class labels read vs m0/paired legs, not bare bands (L109)"),
    sil_wA_no_independent_gain="sil1110_wA rides cutwA's stored gain "
        "(graph-identity af-match; PREREG disclosure)",
    clamp_window_only="l137 form verbatim: settle clamp-free, X zeroed "
        "from window step 0",
    sil_arms_single_batch="sil1110/sil1110_wA: B30 only; L141 B27 "
        "sil1110 quoted beside (ctx)",
    edge_arms_not_rerun="l142 edge ladder stands on B29 (single-batch "
        "there); L144 changes nothing about it")
print("sanity b65 Ti kL/kR", table["Ti"]["b65"]["kL"], table["Ti"]["b65"]["kR"])

out = dict(design="L144 sil1110-on-wA-base (PREREG l144/PREREG.md)",
           anchors=ar, p0=p0, p4=p4, table=table, grid=grid,
           classes=cls, hypotheses=dict(H_EDGE=bool(h_edge),
                                        H_ACT=bool(h_act), note=h_note),
           P1=p1, P3=p3, ctx_l141_b27=ctx,
           pooled=dict(cutng25_5batches=pooled_ng25,
                       cutwA_6batches=pooled_wA),
           disclosures=san)
json.dump(out, open("l144/results_l144.json", "w"), indent=1)
print("results_l144.json written")
