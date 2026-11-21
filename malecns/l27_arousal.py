"""L27: arousal-gated-escape — motor-side twin of the live duck's
oct-is-arousal lesson (octopamine amplifies fear but cannot cross threshold
alone). Does tonic CENTRAL octopamine, as a STATE, amplify the L19 looming
escape route through real wiring — or only raise baseline — and can arousal
ALONE create a gesture? (Live lesson says it must not.)

Static census FIRST (claim-carrier, L19 rule: measure what the wiring
carries before running dynamics):
  oct population = consensus_nt 'octopamine' (101 cells; 49 vnc_efferent
  PERIPHERAL, 35 cb_intrinsic + 16 visual_centrifugal CENTRAL).
  Out-weight target census; direct oct->DNp01-04 edges; z vs 5 random
  size-matched central-population draws.

Dynamic (P1-labeled per tick-37; l19_chain machinery verbatim: DT 10 ms,
gain .8846, x200 on DNp01-04 + DNc01/02, lit5x decay taus, amp 8 looming):
  STATE applied as tonic input on oct cells for 50 steps pre-event onward,
  baseline re-measured WITH the state on (so dm isolates the event response
  under that state). Arms x 3 seeds:
    a0    loom, no oct               (ANCHOR: must reproduce L19 numbers)
    lo+o1/2/4  loom + octCENTRAL tonic amp {1,2,4}
    oct1/2/4   oct-alone (no looming) — gesture creation check
    lo+r{0..4} loom + random-51 tonic amp 4 — placement null
Metrics: TTM/ext/flex pool peak, amplification ratio vs anchor, route
vector self-cos per arm + cos vs anchor mean, oct-alone SNR vs pre-event
noise, op point af per arm (saturation-compression guard, L21 lesson).

DESCRIPTIVE ONLY (owner movement law). CPU-only (8 threads).
"""
import json
import os
import time

import numpy as np
import pandas as pd
import torch

torch.manual_seed(0)
torch.set_num_threads(8)
TAU_BASE, DT, RMAX = 0.05, 0.010, 1.0
BG, NOISE = 0.02, 0.01
SETTLE, OCTON, EVENT, POST = 300, 50, 20, 150
T = OCTON + EVENT + POST
GAIN = 0.8846            # op point bisected in L11
G = 200.0                # per-class pathway gain (L13b)
AMP_EV = 8.0
SEEDS = [11, 22, 33]
TAU_DEACT, RATIO = 0.051, 5.0   # L18 Arm A (measured TDT relaxation)
OCT_AMPS = [1.0, 2.0, 4.0]
NDRAW = 5

os.makedirs("l27", exist_ok=True)
t0 = time.time()
ck = torch.load("male_graph.pt", map_location="cpu")
W, ids = ck["W"], ck["ids"].numpy()
N = W.shape[0]
ann = pd.read_feather("data/body-annotations-male-cns-v1.0-minconf-0.5.feather")
lab = ann[ann["superclass"].notna()].reset_index(drop=True)
assert (lab["bodyId"].to_numpy(np.uint64) == ids).all()
sup = lab["superclass"].astype(str).to_numpy()
typ = lab["type"].astype(str).to_numpy()
nt = pd.read_feather("data/body-neurotransmitters-male-cns-v1.0.feather")
mrg = lab.merge(nt[["body", "consensus_nt"]], left_on="bodyId",
                right_on="body", how="left")
cnt = mrg["consensus_nt"].fillna("none").astype(str).to_numpy()

motor = np.where(np.isin(sup, ["vnc_motor", "cb_motor"]))[0]
dn = np.where(sup == "descending_neuron")[0]
dn_typ = typ[dn]
loom = np.where(np.isin(typ, ["LC4", "LC16", "LC11", "LC12"]))[0]
leg_dns = dn[np.isin(dn_typ, [f"DNp{i:02d}" for i in range(1, 5)])]
neck_dns = dn[np.isin(dn_typ, ["DNc01", "DNc02"])]
assert len(leg_dns) == 8 and len(neck_dns) == 4 and len(loom) > 0

oct_all = np.where(cnt == "octopamine")[0]
oct_periph = oct_all[np.isin(sup[oct_all],
                             ["vnc_efferent", "efferent_ascending"])]
oct_central = np.array([i for i in oct_all if i not in set(oct_periph)])
assert len(oct_all) == 101, len(oct_all)
assert len(oct_central) == 51, len(oct_central)

typm = typ[motor]
M = len(motor)
PAIRS = {
    "Ti": (np.where(np.isin(typm, ["Ti flexor MN", "Acc. ti flexor MN"]))[0],
           np.where(typm == "Ti extensor MN")[0]),
    "Tr": (np.where(np.isin(typm, ["Tr flexor MN", "Acc. tr flexor MN"]))[0],
           np.where(typm == "Tr extensor MN")[0]),
}
POOL_F = np.concatenate([PAIRS["Ti"][0], PAIRS["Tr"][0]])
POOL_E = np.concatenate([PAIRS["Ti"][1], PAIRS["Tr"][1]])
TTM = np.where(np.array([str(t).startswith("TTMn") for t in typm]))[0]
assert len(TTM) > 0
print(f"oct all {len(oct_all)} (periph {len(oct_periph)} / central "
      f"{len(oct_central)}) | loom {len(loom)} | motor {M} | TTMn {len(TTM)}"
      f" | flex {len(POOL_F)} ext {len(POOL_E)}", flush=True)

# --- L13b per-class amplification, verbatim -------------------------------
rows_np = np.repeat(np.arange(N), np.diff(W.crow_indices().numpy()))
cols = W.col_indices().numpy()
mrow = np.zeros(N, bool); mrow[motor] = True
leg_src = np.zeros(N, bool); leg_src[leg_dns] = True
neck_src = np.zeros(N, bool); neck_src[neck_dns] = True
emask_leg = torch.from_numpy(mrow[rows_np] & leg_src[cols])
emask_neck = torch.from_numpy(mrow[rows_np] & neck_src[cols])
Wv = W.values()
Wg = W.clone()
v = Wg.values()
v[emask_leg] = Wv[emask_leg] * G
v[emask_neck] = Wv[emask_neck] * G
print(f"amplified x{G:.0f}: leg {int(emask_leg.sum())} + neck "
      f"{int(emask_neck.sum())} DN->motor edges", flush=True)

# --- STATIC census (claim-carrier) -----------------------------------------
w_all = W.values().numpy()
tgt_dn = np.zeros(N, bool); tgt_dn[dn] = True
tgt_vi = sup == "vnc_intrinsic"
tgt_mo = mrow.copy()
tgt_dnp = np.zeros(N, bool); tgt_dnp[leg_dns] = True


def census(idx):
    src = np.zeros(N, bool); src[idx] = True
    rm = src[rows_np]
    tot = float(w_all[rm].sum()) + 1e-12
    return dict(
        total_w=tot,
        frac_dn=float(w_all[rm & tgt_dn[cols]].sum() / tot),
        frac_vnc_intr=float(w_all[rm & tgt_vi[cols]].sum() / tot),
        frac_motor=float(w_all[rm & tgt_mo[cols]].sum() / tot),
        edges_dnp=int((rm & tgt_dnp[cols]).sum()),
        w_dnp=float(w_all[rm & tgt_dnp[cols]].sum()),
    )


cen_octc = census(oct_central)
cen_octp = census(oct_periph)
rng = np.random.default_rng(20261111 + 27)
CENTRAL_POOL = np.where(np.isin(sup, ["cb_intrinsic", "ol_intrinsic",
                                      "vnc_intrinsic", "visual_centrifugal",
                                      "descending_neuron",
                                      "ascending_neuron"]))[0]
draws = []
for d in range(NDRAW):
    rp = rng.choice(CENTRAL_POOL, size=len(oct_central), replace=False)
    draws.append(census(rp))
zfrac = lambda key: float((cen_octc[key] - np.mean([x[key] for x in draws]))
                          / (np.std([x[key] for x in draws]) + 1e-12))
static = dict(
    oct_all=len(oct_all), oct_peripheral=len(oct_periph),
    oct_central=len(oct_central),
    census_oct_central=cen_octc, census_oct_peripheral=cen_octp,
    random_draws=draws,
    z_octc_vs_rand=dict(frac_dn=zfrac("frac_dn"),
                        frac_vnc_intr=zfrac("frac_vnc_intr"),
                        frac_motor=zfrac("frac_motor")),
)
print("census octC:", {k: (round(v, 5) if isinstance(v, float) else v)
                       for k, v in cen_octc.items()})
print("census octP:", {k: (round(v, 5) if isinstance(v, float) else v)
                       for k, v in cen_octp.items()})
print(f"z octC vs rand51: dn {zfrac('frac_dn'):+.2f} "
      f"vnc_intr {zfrac('frac_vnc_intr'):+.2f} motor {zfrac('frac_motor'):+.2f}"
      f" | rand mean dn {np.mean([x['frac_dn'] for x in draws]):.5f} "
      f"sd {np.std([x['frac_dn'] for x in draws]):.5f}", flush=True)

# --- dynamic machinery (l19 verbatim + STATE tonic) ------------------------
tv = np.full(N, TAU_BASE, np.float32)
tv[motor[POOL_E]] = TAU_DEACT
tv[motor[POOL_F]] = TAU_DEACT * RATIO
tau = torch.from_numpy(tv).unsqueeze(1)


def run_state(oct_idx, amp_oct, loom_on, seed):
    """One rollout: settle -> oct tonic ON (50) -> baseline(with state) ->
    looming event (20) -> post (150). State stays on through post."""
    gen = torch.Generator().manual_seed(seed)
    X = (BG + NOISE * torch.randn(N, 1, generator=gen)).clamp(0, 1)

    def step(I):
        nonlocal X
        drive = torch.sparse.mm(Wg, X) + I
        t = torch.relu(GAIN * drive + BG)
        t = (t + NOISE * torch.randn(N, 1, generator=gen)).clamp(max=RMAX)
        X = X + (DT / tau) * (t - X)

    Z = torch.zeros(N, 1)
    for _ in range(SETTLE):
        step(Z)
    af0 = float((X > 0.05).float().mean())
    I_oct = Z.clone()
    if oct_idx is not None and amp_oct > 0:
        I_oct[oct_idx] = amp_oct
    I_ev = Z.clone()
    if loom_on:
        I_ev[loom] = AMP_EV
    for k in range(OCTON):          # state on, no event yet
        step(I_oct)
    base_m = X[motor].squeeze(1).numpy().copy()
    mbase = float(base_m.mean())
    pool_pre = {"TTM": base_m[TTM].mean(), "ext": base_m[POOL_E].mean(),
                "flex": base_m[POOL_F].mean()}
    rec = np.zeros((M, T), dtype=np.float32)
    dm_pk = np.zeros(M, np.float32); m_pk = -1.0
    for k in range(T):
        step(I_oct + (I_ev if k < EVENT else Z))
        xm = X[motor].squeeze(1).numpy()
        rec[:, k] = xm - base_m
        mm = float(xm.mean())
        if mm > m_pk:
            m_pk = mm
            dm_pk = xm - base_m
    # pool traces (state-relative): pre window = last 20 of OCTON-equivalent
    # (rec starts at event onset; noise floor from early POST-free window)
    tr = {k: rec[idx].mean(0) for k, idx in
          [("TTM", TTM), ("ext", POOL_E), ("flex", POOL_F)]}
    noise = {k: float(np.std(v[EVENT + 40:EVENT + 100])) for k, v in tr.items()}
    peak = {k: float(np.max(v[:EVENT + 60])) for k, v in tr.items()}
    return dict(rec=rec, dm_pk=dm_pk, af0=af0, mbase=mbase,
                pool_pre=pool_pre, tr=tr, noise=noise, peak=peak)


def cos(a, b):
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    return float(a @ b / (na * nb + 1e-12)) if na > 1e-9 and nb > 1e-9 else 0.0


ARMS = {}
ARMS["a0_loom"] = [run_state(None, 0.0, True, s) for s in SEEDS]
for a in OCT_AMPS:
    tag = f"lo+o{int(a)}"
    ARMS[tag] = [run_state(oct_central, a, True, s) for s in SEEDS]
    tag = f"oct{int(a)}alone"
    ARMS[tag] = [run_state(oct_central, a, False, s) for s in SEEDS]
for d in range(NDRAW):
    rp = rng.choice(CENTRAL_POOL, size=len(oct_central), replace=False)
    ARMS[f"lo+r{d}"] = [run_state(rp, 4.0, True, s) for s in SEEDS]
    print(f"null draw {d} done {time.time() - t0:.0f}s", flush=True)

# --- metrics ----------------------------------------------------------------
def arm_stats(runs):
    mvec = np.mean([r["dm_pk"] for r in runs], axis=0)
    self_cos = float(np.mean([cos(runs[i]["dm_pk"], runs[j]["dm_pk"])
                              for i in range(3) for j in range(i + 1, 3)]))
    return dict(
        mbase=float(np.mean([r["mbase"] for r in runs])),
        af0=float(np.mean([r["af0"] for r in runs])),
        peak_TTM=float(np.mean([r["peak"]["TTM"] for r in runs])),
        peak_ext=float(np.mean([r["peak"]["ext"] for r in runs])),
        peak_flex=float(np.mean([r["peak"]["flex"] for r in runs])),
        snr_TTM=float(np.mean([r["peak"]["TTM"] / (r["noise"]["TTM"] + 1e-9)
                               for r in runs])),
        self_cos=self_cos, mvec=mvec,
    )


S = {k: arm_stats(v) for k, v in ARMS.items()}
anchor = S["a0_loom"]
ratios = {f"lo+o{int(a)}": S[f"lo+o{int(a)}"]["peak_TTM"] / anchor["peak_TTM"]
          for a in OCT_AMPS}
rand_rat = [S[f"lo+r{d}"]["peak_TTM"] / anchor["peak_TTM"]
            for d in range(NDRAW)]
rand_mu, rand_sd = float(np.mean(rand_rat)), float(np.std(rand_rat))
oct_z = {f"lo+o{int(a)}": float((ratios[f"lo+o{int(a)}"] - rand_mu) / (rand_sd + 1e-12))
         for a in OCT_AMPS}
vs_anchor = {k: cos(s["mvec"], anchor["mvec"]) for k, s in S.items()}

out = dict(
    static=static,
    arms={k: {kk: vv for kk, vv in s.items() if kk != "mvec"}
          for k, s in S.items()},
    TTM_amplification=ratios,
    rand51_TTM_ratios=rand_rat, rand_mu=rand_mu, rand_sd=rand_sd,
    oct_z_vs_rand=oct_z,
    cos_vs_anchor=vs_anchor,
    anchor=dict(peak_TTM=anchor["peak_TTM"], peak_ext=anchor["peak_ext"],
                self_cos=anchor["self_cos"], snr_TTM=anchor["snr_TTM"],
                mbase=anchor["mbase"], af0=anchor["af0"]),
)
print(f"\nANCHOR loom: TTM pk {anchor['peak_TTM']:.4f} ext "
      f"{anchor['peak_ext']:.4f} self-cos {anchor['self_cos']:+.3f} "
      f"SNR {anchor['snr_TTM']:.1f}x af {anchor['af0']:.4f}")
for a in OCT_AMPS:
    la, oa = S[f"lo+o{int(a)}"], S[f"oct{int(a)}alone"]
    print(f"amp {a}: lo+oct TTM {la['peak_TTM']:.4f} (x{ratios[f'lo+o{int(a)}']:.3f} "
          f"z{oct_z[f'lo+o{int(a)}']:+.2f}) cos-vs-anchor "
          f"{vs_anchor[f'lo+o{int(a)}']:+.3f} self {la['self_cos']:+.3f} af "
          f"{la['af0']:.4f} | octALONE TTM {oa['peak_TTM']:.4f} SNR "
          f"{oa['snr_TTM']:.2f}x (create-gesture check)")
print(f"rand51: ratios {[round(r, 3) for r in rand_rat]} mu {rand_mu:.3f} "
      f"sd {rand_sd:.3f} | cos-vs-anchor "
      f"{np.mean([vs_anchor[f'lo+r{d}'] for d in range(NDRAW)]):+.3f}")
with open("l27/results_l27.json", "w") as f:
    json.dump(out, f, indent=1, default=float)
np.savez_compressed("l27/pool_traces.npz",
                    **{f"{k}__{p}": ARMS[k][i]["tr"][p]
                       for k in ARMS for i in range(3)
                       for p in ["TTM", "ext", "flex"]})
print(f"\nwrote l27/results_l27.json + pool_traces.npz "
      f"| total {time.time() - t0:.0f}s", flush=True)
