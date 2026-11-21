"""L26: ascending-echo — does the brain receive a copy of its own jump?

Every lane item so far flows sensory -> DN -> motor (descending). The
unexplored half is ASCENDING (cord -> brain). L12 measured the endocrine
interoception route DEAD (NSC -> DAN/KC ~0 edges); the electrical/
proprioceptive route is untested. Question: after the L19 jump chain fires,
do ascending populations carry a reproducible copy of the motor burst?

Arms:
  jump        L19 chain verbatim (loom volley, DNp01-04+DNc01/02 x200
              amplification, lit5x tau tiers) + ascending readout.
  jump_clampM same but X[motor] clamped to 0 EVERY step (L2 opto form:
              clamp activity, not W). Ascending signal that survives
              = DN-collateral leak; signal that dies = motor-borne echo.
  mnvolley    direct MN volley (leg extensor+flexor+TTMn pools, AMP 8,
              20 steps) on the PLAIN graph (no amplification) = pure
              efference arm, no DN confound.
  mnv_null0-4 destination-swap null on the motor-OUT block (weights travel
              with the source MN, out-degree per source + destination
              multiset preserved exactly; L14/L20 form) for the efference
              claim.

Estimand labels (tick-37 amendment): all dynamic arms re-apply real-tuned
gains where used = P1-form; the EXISTENCE claim is carried by anatomy
(motor-out census, motor->ascending abs-reachability, provenance tables).
SNR gate FIRST on every pool we read (L19 rule).

DESCRIPTIVE ONLY (owner movement law). CPU-only (8 threads) — the live
duck keeps the GPU.
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
SETTLE, EVENT, POST = 300, 20, 220
T = EVENT + POST
GAIN = 0.8846            # op point bisected in L11
G = 200.0                # per-class pathway gain (L13b)
AMP_EV = 8.0
SEEDS = [11, 22, 33]
NDRAW = 5
TAU_DEACT, RATIO = 0.051, 5.0   # L18 Arm A lit5x

os.makedirs("l26", exist_ok=True)
t0 = time.time()
ck = torch.load("male_graph.pt", map_location="cpu")
W, ids = ck["W"], ck["ids"].numpy()
N = W.shape[0]
ann = pd.read_feather("data/body-annotations-male-cns-v1.0-minconf-0.5.feather")
lab = ann[ann["superclass"].notna()].reset_index(drop=True)
assert (lab["bodyId"].to_numpy(np.uint64) == ids).all()
sup = lab["superclass"].astype(str).to_numpy()
typ = lab["type"].astype(str).to_numpy()
cls = lab["class"].astype(str).to_numpy()
side = lab["somaSide"].astype(str).to_numpy()

# --- census: who lives here? ------------------------------------------------
census = {k: int(v) for k, v in pd.Series(sup).value_counts().items()}
print("superclass census:", json.dumps(census), flush=True)
# ascending pool = the cord->brain interactor class (census printed above;
# sensory_ascending/efferent_ascending noted but kept out of the pool)
asc = np.where(np.isin(sup, ["ascending_neuron"]))[0]
motor = np.where(np.isin(sup, ["vnc_motor", "cb_motor"]))[0]
dn = np.where(sup == "descending_neuron")[0]
dn_typ = typ[dn]
loom = np.where(np.isin(typ, ["LC4", "LC16", "LC11", "LC12"]))[0]
leg_dns = dn[np.isin(dn_typ, [f"DNp{i:02d}" for i in range(1, 5)])]
neck_dns = dn[np.isin(dn_typ, ["DNc01", "DNc02"])]
assert len(asc) > 0 and len(leg_dns) == 8 and len(neck_dns) == 4
typm = typ[motor]
typa = typ[asc]
M, A = len(motor), len(asc)
POOL_F = np.where(np.isin(typm, ["Ti flexor MN", "Acc. ti flexor MN",
                                 "Tr flexor MN", "Acc. tr flexor MN"]))[0]
POOL_E = np.where(typm == "Ti extensor MN")[0]
TTM = np.where(np.array([str(t).startswith("TTMn") for t in typm]))[0]
LEG_ALL = np.unique(np.concatenate([POOL_E, POOL_F, TTM]))
print(f"motor {M} | ascending {A} | loom {len(loom)} | legDN {len(leg_dns)} "
      f"| MN pools ext {len(POOL_E)} flex {len(POOL_F)} TTMn {len(TTM)} "
      f"| volley {len(LEG_ALL)} MNs", flush=True)

# --- edge bookkeeping (W[dst, src]: rows=dst, cols=src) ----------------------
crow = W.crow_indices().clone()
cols_all = W.col_indices().numpy()
rows_all = np.repeat(np.arange(N), np.diff(crow.numpy()))
vals_all = W.values().numpy()
mrow = np.zeros(N, bool); mrow[motor] = True
arow = np.zeros(N, bool); arow[asc] = True
leg_src = np.zeros(N, bool); leg_src[leg_dns] = True
neck_src = np.zeros(N, bool); neck_src[neck_dns] = True
emask_leg = torch.from_numpy(mrow[rows_all] & leg_src[cols_all])
emask_neck = torch.from_numpy(mrow[rows_all] & neck_src[cols_all])
Wg = W.clone()
v = Wg.values()
v[emask_leg] = W.values()[emask_leg] * G
v[emask_neck] = W.values()[emask_neck] * G
print(f"amplified x{G:.0f}: leg {int(emask_leg.sum())} + neck "
      f"{int(emask_neck.sum())} DN->motor edges", flush=True)

# --- STATIC ANATOMY (the claim-carrier) --------------------------------------
print("\n--- static anatomy ---", flush=True)
mout = mrow[cols_all]                       # src is motor
a_dst = arow[rows_all]
static = {}
static["motor_out"] = dict(
    edges=int(mout.sum()),
    abs_w=float(np.abs(vals_all[mout]).sum()),
    unique_dst=int(len(np.unique(rows_all[mout]))),
    dst_asc_direct_edges=int((mout & a_dst).sum()),
    dst_asc_direct_abs_w=float(np.abs(vals_all[mout & a_dst]).sum()),
    frac_w_to_asc=float(np.abs(vals_all[mout & a_dst]).sum()
                        / (np.abs(vals_all[mout]).sum() + 1e-12)))
print(f"motor-OUT edges {static['motor_out']['edges']} "
      f"(abs_w {static['motor_out']['abs_w']:.0f}) -> "
      f"{static['motor_out']['unique_dst']} unique dsts; DIRECT "
      f"motor->ascending {static['motor_out']['dst_asc_direct_edges']} "
      f"edges (abs_w {static['motor_out']['dst_asc_direct_abs_w']:.0f}, "
      f"{static['motor_out']['frac_w_to_asc']*100:.1f}% of motor-out weight)",
      flush=True)

# abs-reachability motor -> ascending (L21 form: ABS weights)
src_is_motor = mrow[cols_all]
reach = mrow.copy()                          # hop 0 = the MNs themselves
reach_asc_by_hop = []
for hop in range(1, 7):
    newly = np.zeros(N, bool)
    # cells receiving an edge from the current frontier
    sel = reach[cols_all]
    if sel.any():
        newly[rows_all[sel]] = True
    newly &= ~reach
    reach |= newly
    n_a = int((newly & arow).sum())
    reach_asc_by_hop.append(n_a)
    if n_a == 0 and not newly.any():
        break
static["reach_asc_by_hop"] = reach_asc_by_hop
static["asc_total_reachable"] = int((reach & arow).sum())
print(f"abs-reachability motor->ascending by hop: {reach_asc_by_hop} "
      f"| total reachable asc {static['asc_total_reachable']}/{A}",
      flush=True)

# ascending IN-edge provenance (share of abs weight by src superclass)
ain = a_dst
prov = {}
w_in = np.abs(vals_all[ain])
sup_src = sup[cols_all[ain]]
for s in np.unique(sup_src):
    prov[str(s)] = [float(w_in[sup_src == s].sum()),
                    float((sup_src == s).mean())]
prov = dict(sorted(prov.items(), key=lambda kv: -kv[1][0])[:8])
static["asc_in_provenance_abs_w_frac"] = {k: round(v[0] / (w_in.sum() + 1e-12), 4)
                                          for k, v in prov.items()}
print("ascending IN-edge src (abs-w share):",
      static["asc_in_provenance_abs_w_frac"], flush=True)

# ascending OUT-edge recipients (where the echo would land brain-side)
aout = arow[cols_all]
recip = {}
w_out = np.abs(vals_all[aout])
sup_dst = sup[rows_all[aout]]
for s in np.unique(sup_dst):
    recip[str(s)] = float(w_out[sup_dst == s].sum())
recip = dict(sorted(recip.items(), key=lambda kv: -kv[1])[:8])
static["asc_out_recipients_abs_w_frac"] = {k: round(vv / (w_out.sum() + 1e-12), 4)
                                           for k, vv in recip.items()}
print("ascending OUT-edge dst (abs-w share):",
      static["asc_out_recipients_abs_w_frac"], flush=True)


# --- dynamics ----------------------------------------------------------------
def tau_vec(arm):
    tv = np.full(N, TAU_BASE, np.float32)
    if arm == "lit5x":
        tv[motor[POOL_E]] = TAU_DEACT
        tv[motor[POOL_F]] = TAU_DEACT * RATIO
    return tv


def run_chain(channel, seed, W_use, arm="lit5x", clamp=None):
    """One rollout; records motor + ascending pools. clamp = abs indices."""
    tau = torch.from_numpy(tau_vec(arm)).unsqueeze(1)
    gen = torch.Generator().manual_seed(seed)
    X = (BG + NOISE * torch.randn(N, 1, generator=gen)).clamp(0, 1)

    def step(I):
        nonlocal X
        drive = torch.sparse.mm(W_use, X) + I      # [N,1] operands
        t = torch.relu(GAIN * drive + BG)
        t = (t + NOISE * torch.randn(N, 1, generator=gen)).clamp(max=RMAX)
        X = X + (DT / tau) * (t - X)
        if clamp is not None:
            X[clamp] = 0.0

    Z = torch.zeros(N, 1)
    I0 = Z.clone(); I0[channel] = AMP_EV
    for _ in range(SETTLE):
        step(Z)
    af = float((X > 0.05).float().mean())
    base_m = X[motor].squeeze(1).numpy().copy()
    base_a = X[asc].squeeze(1).numpy().copy()
    # noise floor: last 60 settle steps of the ascending pool mean
    a_noise = []
    for _ in range(60):
        step(Z)
        a_noise.append(float(X[asc].mean()))
    a_mu, a_sd = float(np.mean(a_noise)), float(np.std(a_noise))
    m_pk, a_pk = -1.0, -1.0
    dm_pk = np.zeros(M, np.float32)
    da_pk = np.zeros(A, np.float32)
    for k in range(T):
        step(I0 if k < EVENT else Z)
        ma, aa = float(X[motor].mean()), float(X[asc].mean())
        if ma > m_pk:
            m_pk = ma
            dm_pk = X[motor].squeeze(1).numpy() - base_m
        if aa > a_pk:
            a_pk = aa
            da_pk = X[asc].squeeze(1).numpy() - base_a
    snr_a = (a_pk - a_mu) / (a_sd + 1e-12)
    return dict(af=af, dm_pk=dm_pk, da_pk=da_pk, a_pk=a_pk, a_mu=a_mu,
                a_sd=a_sd, snr_a=float(snr_a), m_pk=m_pk)


def cos(a, b):
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    return float(a @ b / (na * nb + 1e-12)) if na > 1e-9 and nb > 1e-9 else 0.0


def pair_self(vecs):
    return float(np.mean([cos(vecs[i], vecs[j])
                          for i in range(len(vecs)) for j in range(i + 1, len(vecs))]))


ARMS = {}
for arm, ch, clamp, W_use, tarm in [
    ("jump", loom, None, Wg, "lit5x"),
    ("jump_clampM", loom, torch.from_numpy(motor), Wg, "lit5x"),
    ("mnvolley", motor[LEG_ALL], None, W, "homog"),
]:
    ARMS[arm] = [run_chain(ch, s, W_use, arm=tarm, clamp=clamp) for s in SEEDS]
    r = ARMS[arm]
    print(f"{arm:12s} af {np.mean([x['af'] for x in r]):.4f} "
          f"motor_pk {np.mean([x['m_pk'] for x in r]):.4f} "
          f"asc_pk {np.mean([x['a_pk'] for x in r]):.4f} (base "
          f"{np.mean([x['a_mu'] for x in r]):.4f}+/-{np.mean([x['a_sd'] for x in r]):.4f}) "
          f"asc_SNR {np.mean([x['snr_a'] for x in r]):8.1f}x "
          f"asc_self {pair_self([x['da_pk'] for x in r]):+.3f} "
          f"| {time.time() - t0:.0f}s", flush=True)

# --- destination-swap null on the motor-OUT block (mnvolley claim) -----------
block = np.where(mrow[cols_all])[0]
assert len(block) == static["motor_out"]["edges"] and len(block) > 0
rng = np.random.default_rng(20261111 + 26)
NULL = []
for d in range(NDRAW):
    perm = rng.permutation(len(block))
    cols2 = cols_all.copy()
    cols2[block] = cols_all[block][perm]        # dst multiset preserved
    # rows (dst slots) unchanged; weights stay at their src positions
    # dst multiset must be preserved exactly (in-degree conservation)
    assert np.array_equal(np.sort(cols2[block]), np.sort(cols_all[block]))
    Wn = torch.sparse_csr_tensor(crow, torch.from_numpy(cols2).long(),
                                 W.values().clone(), W.shape)
    runs = [run_chain(motor[LEG_ALL], s, Wn, arm="homog") for s in SEEDS]
    NULL.append(runs)
    print(f"mnv_null{d}    asc_SNR {np.mean([x['snr_a'] for x in runs]):8.1f}x "
          f"asc_self {pair_self([x['da_pk'] for x in runs]):+.3f} "
          f"| {time.time() - t0:.0f}s", flush=True)

# --- metrics -----------------------------------------------------------------
print("\n--- verdicts ---", flush=True)
J, C, V = ARMS["jump"], ARMS["jump_clampM"], ARMS["mnvolley"]
jv = np.mean([r["da_pk"] for r in J], axis=0)
cv = np.mean([r["da_pk"] for r in C], axis=0)
vv = np.mean([r["da_pk"] for r in V], axis=0)
res_dyn = {
    "jump": {"snr_a": float(np.mean([r["snr_a"] for r in J])),
             "asc_self": pair_self([r["da_pk"] for r in J])},
    "jump_clampM": {"snr_a": float(np.mean([r["snr_a"] for r in C])),
                    "asc_self": pair_self([r["da_pk"] for r in C]),
                    "cos_vs_jump": float(cos(cv, jv))},
    "mnvolley": {"snr_a": float(np.mean([r["snr_a"] for r in V])),
                 "asc_self": pair_self([r["da_pk"] for r in V])},
}
null_self = [pair_self([r["da_pk"] for r in NULL[d]]) for d in range(NDRAW)]
res_dyn["mnv_null_self"] = null_self
res_dyn["mnv_null_snr"] = [float(np.mean([r["snr_a"] for r in NULL[d]]))
                           for d in range(NDRAW)]
# top-loading (L14 form): top-10 |dm| mass share of the asc peak vector
mass = np.abs(vv)
top10 = np.argsort(-mass)[:10]
res_dyn["mnv_top10_share"] = float(mass[top10].sum() / (mass.sum() + 1e-12))
res_dyn["mnv_top10_names"] = [str(typa[t]) for t in top10]
null_shares = []
for d in range(NDRAW):
    m2 = np.abs(np.mean([r["da_pk"] for r in NULL[d]], axis=0))
    t2 = np.argsort(-m2)[:10]
    null_shares.append(float(m2[t2].sum() / (m2.sum() + 1e-12)))
res_dyn["mnv_null_top10_share"] = null_shares
chance10 = 10.0 / A
print(f"jump      asc SNR {res_dyn['jump']['snr_a']:8.1f}x "
      f"self {res_dyn['jump']['asc_self']:+.3f}", flush=True)
print(f"clampM    asc SNR {res_dyn['jump_clampM']['snr_a']:8.1f}x "
      f"self {res_dyn['jump_clampM']['asc_self']:+.3f} "
      f"cos_vs_jump {res_dyn['jump_clampM']['cos_vs_jump']:+.3f}", flush=True)
print(f"mnvolley  asc SNR {res_dyn['mnvolley']['snr_a']:8.1f}x "
      f"self {res_dyn['mnvolley']['asc_self']:+.3f} | top-10 mass "
      f"{res_dyn['mnv_top10_share']:.4f} vs null "
      f"{np.mean(null_shares):.4f}+/-{np.std(null_shares):.4f} "
      f"chance {chance10:.4f}", flush=True)
print("top-10 asc responders (mnvolley):", res_dyn["mnv_top10_names"], flush=True)

res = {
    "config": dict(DT=DT, EVENT=EVENT, POST=POST, T=T, settle=SETTLE,
                   gain=GAIN, g_path=G, amp_ev=AMP_EV, seeds=SEEDS,
                   ndraw=NDRAW, motor=M, asc=A, volley=len(LEG_ALL),
                   tau_arm="lit5x (jump arms) / homog (volley arms)",
                   estimand="dynamics P1-form (real-tuned gains re-applied); "
                            "existence claims carried by static anatomy"),
    "static": static,
    "dynamic": res_dyn,
    "af": {a: float(np.mean([r["af"] for r in ARMS[a]])) for a in ARMS},
}
json.dump(res, open("l26/results_l26.json", "w"), indent=1, default=float)
np.savez_compressed("l26/asc_vectors.npz", jump=jv, clampM=cv, mnvolley=vv,
                    top10=top10, asc_idx=asc)
print(f"\ndone {time.time() - t0:.0f}s -> l26/results_l26.json", flush=True)
