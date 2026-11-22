"""L164 PRE-MEASUREMENT (registered in l164/PREREG.md BEFORE this output):
is the random-onset intervention admissible at all? Computes the drive
scalar s[k] added to drive[mech] under fix (o_s=0) and under the 16 drawn
offsets, and reports bin-6 power + PLV_drive. HALTING GATE: PLV_drive(rnd)
>= 0.4 => B_VACUOUS_DESIGN, rollouts not run as primary.
Zero rollouts, no graph build, deterministic.
"""
import json
import math

import numpy as np

WIN, DT = 6000, 0.01
SEGB = [(0, 2000, 0.7), (2000, 4000, 1.4), (4000, 6000, 0.7)]
SEG = 2000
ENT_AMP = 0.1
BIN_FULL = 6
B42 = list(range(4201, 4217))
CHOP_P, CHOP_ON = 900, 500

fr = np.fft.rfftfreq(WIN, DT)
assert abs(fr[BIN_FULL] - 0.1) < 1e-12, "CERT-bin FAIL"
print(f"CERT-bin fr[{BIN_FULL}] = {fr[BIN_FULL]!r} == 0.1: PASS")


def target(k):
    for a, b, f in SEGB:
        if a <= k < b:
            return f
    return SEGB[-1][2]


def drive_series(o):
    """The exact scalar added to drive[mech,0] at each step k, for a
    per-seed onset offset o (o=0 reproduces l154_run.py VERBATIM)."""
    amp = np.zeros(WIN, np.float64)
    for seg0, _, _ in SEGB:
        # periodic continuation of l154's 900/500 chop train, phase-shifted
        # by o; at o = 0 this is bit-identical to l154_run.py's AMPA loop
        # (asserted below), because that loop lays 0-500 / 900-1400 /
        # 1800-2000 inside each 2000-sample segment.
        for k in range(seg0, seg0 + SEG):
            amp[k] = ENT_AMP if ((k - seg0 + o) % CHOP_P) < CHOP_ON else 0.0
    amp[2000:4000] = ENT_AMP            # l154_run.py: segment 1 fully on
    ph = 2 * math.pi * 0.7 * DT * o     # onset phase of the carrier
    s = np.zeros(WIN, np.float64)
    for k in range(WIN):
        ph += 2 * math.pi * target(k) * DT
        s[k] = ENT_AMP * (0.5 + 0.5 * math.sin(ph)) if amp[k] > 0 else 0.0
    return s, amp


# --- fix-arm identity against l154_run.py's own construction ---------------
amp_ref = np.zeros(WIN, np.float64)
for seg0, _, _ in SEGB:
    c = 0
    while seg0 + c * CHOP_P < seg0 + SEG:
        lo = seg0 + c * CHOP_P
        amp_ref[lo:min(lo + CHOP_ON, seg0 + SEG)] = ENT_AMP
        c += 1
amp_ref[2000:4000] = ENT_AMP
ph = 0.0
PHI = np.empty(WIN, np.float64)
for i in range(WIN):
    ph += 2 * math.pi * target(i) * DT
    PHI[i] = ph
s_ref = np.where(amp_ref > 0,
                 ENT_AMP * (0.5 + 0.5 * np.sin(PHI)), 0.0)
s0, amp0 = drive_series(0)
assert np.array_equal(amp0, amp_ref), "o=0 gate != l154 AMPA (STOP)"
assert float(np.abs(s0 - s_ref).max()) == 0.0, "o=0 drive != l154 (STOP)"
print("CERT-fix o_s=0 reproduces l154_run.py AMPA + sin_t EXACTLY "
      "(max|d| 0.0): PASS")

rng = np.random.default_rng(164)
OFF = [int(x) for x in rng.integers(0, CHOP_P, size=len(B42))]
print(f"offsets o_s (rng 164) = {OFF}")


def bin6(x):
    return np.fft.rfft(x - x.mean())[BIN_FULL]


def plv(ph_):
    return float(abs(np.mean(np.exp(1j * np.asarray(ph_)))))


Xf = [bin6(s0) for _ in B42]
Xr = [bin6(drive_series(o)[0]) for o in OFF]
ph_f = [float(np.angle(v)) for v in Xf]
ph_r = [float(np.angle(v)) for v in Xr]
pw_f = float(abs(Xf[0]) ** 2)
pw_r = [float(abs(v) ** 2) for v in Xr]
plv_f, plv_r = plv(ph_f), plv(ph_r)
n = len(B42)
floor = math.sqrt(math.pi / (4 * n))
spread = float(np.degrees(math.sqrt(-2 * math.log(plv_r)))) if plv_r > 0 else 1e9

gate_ok = plv_r < 0.4
verdict = "WELL_POSED" if gate_ok else "B_VACUOUS_DESIGN"
out = dict(card="L164 drive pre-measurement", win=WIN, dt=DT,
           bin_full=BIN_FULL, f_bin=float(fr[BIN_FULL]),
           chop_period=CHOP_P, chop_on=CHOP_ON, ent_amp=ENT_AMP,
           seeds=B42, offsets=OFF,
           d1_power_fix=pw_f, d1_power_rnd_med=float(np.median(pw_r)),
           d1_power_rnd_min=float(min(pw_r)), d1_power_rnd_max=float(max(pw_r)),
           d2_plv_drive_fix=plv_f, d2_plv_drive_rnd=plv_r,
           d2_plv_floor_n16=floor,
           d3_phase_fix_deg=float(np.degrees(ph_f[0])),
           d3_phase_rnd_deg=[float(np.degrees(p)) for p in ph_r],
           d3_circ_spread_rnd_deg=spread,
           gate_bar=0.4, gate_pass=bool(gate_ok), verdict=verdict)
json.dump(out, open("l164/drive_static.json", "w"), indent=1)

print(f"\nD1 drive bin-6 power  fix {pw_f:.6g} | rnd med {np.median(pw_r):.6g} "
      f"[{min(pw_r):.6g}, {max(pw_r):.6g}]")
print(f"D2 PLV_drive          fix {plv_f:.6f} (1.0 by construction) | "
      f"rnd {plv_r:.6f}  (free-phase floor at n=16: {floor:.4f})")
print(f"D3 arg S[6]           fix {np.degrees(ph_f[0]):+8.2f} deg | "
      f"rnd circular spread {spread:.1f} deg")
print(f"\nGATE (PLV_drive(rnd) < 0.4): {'PASS' if gate_ok else 'FAIL'} "
      f"-> {verdict}")
assert gate_ok, "GATE FAIL — design vacuous, amendment required before rollouts"
