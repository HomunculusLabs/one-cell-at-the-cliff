#!/usr/bin/env python3
"""Fig. 6 — the circuit: three characters, asymmetric necessity (BRIEF_fig6.md).

House style = l152_clamp_cut_grid.svg / fig5_threepanel.py: #282c34 ground,
#21252b panels, #abb2bf title/labels, #5c6370 / #9aa3b2 sub-text, #3e4451 grid,
five-colour accent palette (#98c379 #e5c07b #c678dd #61afef #d19a66), stroke 1-2,
no font-family (renderer default), footer assert line.

STORED ARTIFACTS ONLY (no rollout, no recomputation beyond one point ratio and
one subtraction, both declared as expressions):
  l184e  banc/l184/edges.csv              carrier partner list (L184 Q2)
  l190r  banc/l190/results_l190.json      single-edge cut 1110->75494 (L190)
  l198s  banc/l198/static.json            relay wiring (L198)
  l200a4 banc/l200/a4_wiring.json         carrier / ru2 laterality + overlap (L200 A4)
  l200s  banc/l200/selection.json         premotor pool sizes (L200)
  l200r  banc/l200/results_l200.json      arm duties, 1.4-Hz panel, contrasts (L200)
  l199p  banc/l199/results_primary.json   phase Parts B/C (L199)
Every drawn number carries data-src (artifact pointer) + data-v (value) +
data-fmt on its SVG element; fig6_verify.py resolves each pointer itself.
L202 (registered replicate) has NOT landed: its slot is drawn as pending and
the generator refuses to run silently if results_l202.json appears.
"""
import csv, json, math, os, subprocess

P = os.path.expanduser("~/critters/peabrain-lab")
OUT = f"{P}/paper/figures"
FILES = {
    "l184e": f"{P}/banc/l184/edges.csv",
    "l190r": f"{P}/banc/l190/results_l190.json",
    "l198s": f"{P}/banc/l198/static.json",
    "l200a4": f"{P}/banc/l200/a4_wiring.json",
    "l200s": f"{P}/banc/l200/selection.json",
    "l200r": f"{P}/banc/l200/results_l200.json",
    "l199p": f"{P}/banc/l199/results_primary.json",
}
L202 = f"{P}/banc/l202/results_l202.json"
if os.path.exists(L202):
    raise SystemExit("L202 results landed: extend Panel B with the replicate before regenerating (BRIEF_fig6)")

J = {k: json.load(open(v)) for k, v in FILES.items() if v.endswith(".json")}
EDGES = list(csv.DictReader(open(FILES["l184e"])))


def A(c, m):
    if not c:
        raise AssertionError(m)


def resolve(src):
    """Pointer grammar: alias/key/key/idx ; csv:  l184e?col=val&col=val#count|#field"""
    if src.startswith("ratio(") or src.startswith("sub("):
        op, body = src.split("(", 1)
        a, b = body[:-1].split(";")
        va, vb = resolve(a), resolve(b)
        return va / vb if op == "ratio" else va - vb
    if src.startswith("l184e?"):
        q, out = src[6:].split("#")
        conds = [c.split("=", 1) for c in q.split("&")]
        rows = [r for r in EDGES if all(r[k] == v for k, v in conds)]
        if out == "count":
            return len(rows)
        A(len(rows) == 1, f"csv pointer {src} must select one row")
        return int(rows[0][out])
    alias, *path = src.split("/")
    x = J[alias]
    for p in path:
        x = x[int(p)] if isinstance(x, list) else x[p]
    return x


def fmt(v, f):
    if f == "d":
        s = f"{int(v)}"
    elif f == "comma":
        s = f"{int(v):,}"
    elif f == "pct":
        s = f"{round(v * 100)}%"
    elif f.startswith("s"):        # signed: s3 / s1 / s0
        s = f"{v:+.{int(f[1:])}f}"
    else:                          # f3 / f1 / f0
        s = f"{v:.{int(f[1:])}f}"
    return s.replace("-", "\u2212")


REG = []   # (id, src, value, fmt) for the caption table


def T(x, y, text_tmpl, srcs=(), fs=12, fill="#abb2bf", anchor="start", bold=False, eid=None, extra=""):
    """Text whose {} slots are filled from artifact pointers (fmt per slot)."""
    vals = [resolve(s) for s, _ in srcs]
    txt = text_tmpl.format(*[fmt(v, f) for v, (_, f) in zip(vals, srcs)])
    txt = txt.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    attrs = f'x="{x:.1f}" y="{y:.1f}" fill="{fill}" font-size="{fs}"'
    if anchor != "start":
        attrs += f' text-anchor="{anchor}"'
    if bold:
        attrs += ' font-weight="bold"'
    if srcs:
        eid = eid or f"t{len(REG)}"
        attrs += f' id="{eid}" data-src="{"|".join(s for s, _ in srcs)}" data-v="{"|".join(repr(v) for v in vals)}" data-fmt="{"|".join(f for _, f in srcs)}"'
        for (s, f), v in zip(srcs, vals):
            REG.append((eid, s, v, f))
    return f"<text {attrs}{extra}>{txt}</text>"


# ---------------- identity asserts (what the cartoon claims) ----------------
a4 = J["l200a4"]["cells"]
A(a4["carrier"]["gi"] == 1110 and a4["carrier"]["cell_type"] == "DNp33" and a4["carrier"]["side"] == "left", "carrier = DNp33-L gi 1110")
A(a4["ru2"]["gi"] == 70994 and a4["ru2"]["cell_type"] == "IN07B031" and a4["ru2"]["side"] == "right", "ru2 = IN07B031-R gi 70994")
rel = J["l198s"]["relay"]
A(rel["cell"]["gi"] == 75494 and rel["cell"]["cell_type"] == "IN06B033" and rel["cell"]["side"] == "left", "relay = IN06B033-L gi 75494")
A(rel["cell"]["eff_sign"] == -1.0 and a4["ru2"]["eff_sign"] == -1.0 and a4["carrier"]["eff_sign"] == 1.0, "signs")
A(J["l190r"]["selection"]["E-edge"]["source"] == 1110 and J["l190r"]["selection"]["E-edge"]["target"] == 75494, "L190 edge = 1110->75494")
A(J["l190r"]["selection"]["E-edge"]["syn"] == rel["carrier_to_relay"]["syn"] == resolve("l184e?direction=out&dst=75494#syn") == 21, "21 syn in three artifacts")
A(resolve("l184e?direction=out#count") == a4["carrier"]["out_edges"] == 80, "80 outputs, csv == a4")
A(set(r["dst"] for r in EDGES if r["target_class"] == "direct right-Ti premotor") == {"69410", "72158", "75494"}, "3 direct R-Ti premotor incl relay")
A(a4["carrier"]["one_hop"]["shared"]["edges"] == 0, "carrier has no edge into PM_L∩PM_R")
A(all(a4[c]["direct_onto"][p]["n_edges"] == 0 for c in ("carrier", "ru2") for p in ("Ti_fR", "Ti_eR", "Ti_fL", "Ti_eL")), "neither carrier nor ru2 touches a Ti MN directly")
A(rel["direct_onto"]["Ti_fR"]["n_edges"] == 1 and rel["direct_onto"]["Ti_eR"]["n_edges"] == 0, "relay: one direct Ti_fR edge")
R = J["l200r"]
A(R["status"] == "FINAL" and R["gi"] == {"ru2": 70994, "carrier": 1110, "lt1": 71926, "lt2": 68609, "l2h": 67738}, "l200 final + gi map")
ARMS = [("cutwA", "base"), ("sc25", "carrier cut"), ("l2", "ru2 cut"), ("l2k", "ru2 cut · carrier clamped"), ("l2c", "carrier + ru2 cut")]
REMOVED = {"sc25": [1110], "l2": [70994], "l2k": [70994], "l2c": [70994, 1110]}
for a, rm in REMOVED.items():
    A(R["arms"][a]["removed"] == rm, f"{a} removed {rm}")
A(R["base"]["arm"] == "cutwA" and R["base"]["removed"] is None, "base")
A(R["arms"]["l2k"]["x_carrier"] == R["base"]["x_carrier"], "l2k carrier replay == base rate")
A(J["l199p"]["status"] == "FINAL", "l199 final")
S = J["l199p"]["datasets"]["S"]
A(S["n"] == 96 and S["W"] == 150 and S["pulse"] == 500, "L199 S dataset")
A(all(x is not None for g in ("cutwA", "sc25") for x in S["B"]["octants"][g]), "no empty octant")

COL = {"cutwA": "#d19a66", "sc25": "#98c379", "l2": "#c678dd", "l2k": "#61afef", "l2c": "#e5c07b"}
W, H = 1400, 1012
s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" data-figure="fig6" data-l202="pending">',
     '<defs><marker id="arr" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#abb2bf"/></marker>'
     '<marker id="arrg" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#98c379"/></marker>'
     '<marker id="arrp" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#c678dd"/></marker></defs>',
     f'<rect width="{W}" height="{H}" fill="#282c34"/>',
     '<text x="30" y="34" fill="#abb2bf" font-size="19" font-weight="bold">Fig. 6 — the circuit: a carrier, a relay, and a cord interneuron the carrier\'s phenotype needs</text>',
     '<text x="30" y="56" fill="#9aa3b2" font-size="13">BANC female cord, k=24 cutwA base · rate model, certified matched operating point · every number below is read from a stored artifact (pointer on its SVG element; table in fig6_caption.md)</text>',
     '<text x="30" y="76" fill="#9aa3b2" font-size="13">A wiring (schematic — positions arbitrary, counts real) · B asymmetric necessity (L200 batch B44, 16 seeds/arm) · C phase rotation under carrier removal (L199 S, 96 seeds)</text>']

# ======================= Panel A — wiring cartoon =======================
s.append('<rect x="24" y="92" width="676" height="472" fill="#21252b" rx="6"/>')
s.append('<text x="40" y="116" fill="#abb2bf" font-size="15" font-weight="bold">A</text>')
s.append('<text x="60" y="116" fill="#abb2bf" font-size="13">wiring, schematic (one-hop static edges, model-true signs)</text>')


def node(x, y, w, h, col, l1, l2=None, srcs1=(), srcs2=(), nid=None):
    out = [f'<rect class="node" data-node="{nid}" x="{x}" y="{y}" width="{w}" height="{h}" rx="7" fill="#282c34" stroke="{col}" stroke-width="2"/>']
    out.append(T(x + w / 2, y + (19 if l2 else h / 2 + 5), l1, srcs1, fs=12.5, fill=col, anchor="middle", bold=True))
    if l2:
        out.append(T(x + w / 2, y + 36, l2, srcs2, fs=10.5, fill="#9aa3b2", anchor="middle"))
    return out


# nodes
s += node(44, 150, 178, 46, "#98c379", "DNp33-L · gi {}", "carrier · descending · excit. · {} out",
          [("l200a4/cells/carrier/gi", "d")], [("l200a4/cells/carrier/out_edges", "d")], "carrier")
s += node(282, 150, 178, 46, "#61afef", "IN06B033-L · gi {}", "relay · cord IN · inhib. · {} out",
          [("l198s/relay/cell/gi", "d")], [("l198s/relay/out_edges", "d")], "relay")
s += node(44, 400, 178, 46, "#c678dd", "IN07B031-R · gi {}", "ru2 · cord IN · inhib. · {} out",
          [("l200a4/cells/ru2/gi", "d")], [("l200a4/cells/ru2/out_edges", "d")], "ru2")
s += node(528, 134, 156, 40, "#abb2bf", "Ti flexor R · {} MN", None, [("l198s/relay/direct_onto/Ti_fR/targets", "d")], nid="TifR")
s += node(528, 186, 156, 40, "#abb2bf", "Ti extensor R · {} MN", None, [("l198s/relay/direct_onto/Ti_eR/targets", "d")], nid="TieR")
s += node(528, 300, 156, 40, "#5c6370", "premotor R · {} cells", None, [("l200s/PM_R_n", "comma")], nid="PMR")
s += node(528, 486, 156, 40, "#5c6370", "premotor L · {} cells", None, [("l200s/PM_L_n", "comma")], nid="PML")
s.append(T(606, 360, "(Ti MN-L: flexor {} · extensor {})", [("l200a4/cells/ru2/direct_onto/Ti_fL/targets", "d"), ("l200a4/cells/ru2/direct_onto/Ti_eL/targets", "d")], fs=10, fill="#5c6370", anchor="middle"))
# premotor pools feed their own motor pools (definition of PM: >=1 edge onto that side's Ti MNs)
s.append('<line x1="606" y1="300" x2="606" y2="230" stroke="#5c6370" stroke-width="1" stroke-dasharray="3 3" marker-end="url(#arr)"/>')

# carrier -> relay (the 21-syn bottleneck edge)
s.append('<line class="edge" data-edge="carrier-relay" x1="222" y1="173" x2="278" y2="173" stroke="#98c379" stroke-width="3.2" marker-end="url(#arrg)"/>')
s.append(T(250, 143, "{} syn", [("l198s/relay/carrier_to_relay/syn", "d")], fs=12, fill="#98c379", anchor="middle", bold=True))
# relay -> Ti flexor R (its one direct motor edge)
s.append('<line class="edge" data-edge="relay-TifR" x1="460" y1="168" x2="524" y2="155" stroke="#61afef" stroke-width="2" marker-end="url(#arr)"/>')
s.append(T(492, 145, "{} edge · {} syn", [("l198s/relay/direct_onto/Ti_fR/n_edges", "d"), ("l198s/relay/direct_onto/Ti_fR/syn", "d")], fs=10.5, fill="#61afef", anchor="middle"))
# carrier one-hop onto premotor R (3 edges; the relay is one: it has a direct Ti_fR edge)
s.append('<path class="edge" data-edge="carrier-PMR" d="M 215 196 C 235 300, 420 320, 524 320" fill="none" stroke="#98c379" stroke-width="1.6" marker-end="url(#arrg)"/>')
s.append(T(440, 300, "{} edges onto premotor R", [("l200a4/cells/carrier/one_hop/PM_R/edges", "d")], fs=10.5, fill="#98c379", anchor="middle"))
s.append('<text x="440" y="287" fill="#98c379" font-size="10.5" text-anchor="middle">(the relay is one)</text>')
# edge-cut result on the bottleneck edge (L190)
s.append(T(392, 214, "cut only this edge (L190): {}", [("l190r/summary/E-edge/delta", "s3")], fs=10.5, fill="#9aa3b2", anchor="middle"))
s.append(T(392, 228, "vs carrier removal {} = {}", [("l190r/summary/sc25/delta", "s3"),
                                                         ("ratio(l190r/summary/E-edge/delta;l190r/summary/sc25/delta)", "pct")], fs=10.5, fill="#9aa3b2", anchor="middle"))
s.append(T(392, 242, "point ratio, no interval · its 1.4 Hz {}", [("l190r/summary/E-edge/mid", "f3")], fs=10.5, fill="#9aa3b2", anchor="middle"))
# the carrier's wide fan (the other outputs)
fan_n = 14
for i in range(fan_n):
    s.append(f'<line class="fan" x1="120" y1="196" x2="{50 + i * 11.0:.1f}" y2="{250 + (i % 3) * 5:.1f}" stroke="#98c379" stroke-width="1" opacity="0.45"/>')
s.append(T(130, 282, "{} other outputs = {} − {}", [("sub(l184e?direction=out#count;l184e?target_class=direct right-Ti premotor#count)", "d"),
                                                   ("l184e?direction=out#count", "d"), ("l184e?target_class=direct right-Ti premotor#count", "d")], fs=11, fill="#98c379", anchor="middle", bold=True))
s.append(T(130, 297, "{} → cord interneurons", [("l184e?target_class=ventral_nerve_cord_intrinsic#count", "d")], fs=10, fill="#9aa3b2", anchor="middle"))
s.append(T(130, 310, "{} → other motor neurons", [("l184e?target_class=other motor#count", "d")], fs=10, fill="#9aa3b2", anchor="middle"))
s.append('<text x="130" y="326" fill="#9aa3b2" font-size="10" text-anchor="middle">candidate substrate of the 1.4-Hz</text>')
s.append('<text x="130" y="339" fill="#9aa3b2" font-size="10" text-anchor="middle">signature, by elimination (relay cut</text>')
s.append('<text x="130" y="352" fill="#9aa3b2" font-size="10" text-anchor="middle">and edge cut leave it at base)</text>')
# ru2 -> both premotor pools, even
s.append('<path class="edge" data-edge="ru2-PMR" d="M 222 414 C 380 414, 440 322, 524 322" fill="none" stroke="#c678dd" stroke-width="2" marker-end="url(#arrp)"/>')
s.append('<path class="edge" data-edge="ru2-PML" d="M 222 432 C 380 432, 440 506, 524 506" fill="none" stroke="#c678dd" stroke-width="2" marker-end="url(#arrp)"/>')
s.append(T(262, 406, "{} edges", [("l200a4/cells/ru2/one_hop/PM_R/edges", "d")], fs=11, fill="#c678dd", anchor="middle", bold=True))
s.append(T(262, 450, "{} edges", [("l200a4/cells/ru2/one_hop/PM_L/edges", "d")], fs=11, fill="#c678dd", anchor="middle", bold=True))
s.append(T(44, 474, "two-hop → extensors: {} L · {} R", [("l200a4/cells/ru2/two_hop/Ti_eL/signed", "f1"), ("l200a4/cells/ru2/two_hop/Ti_eR/signed", "f1")], fs=10.5, fill="#c678dd"))
s.append(T(44, 488, "LI2 laterality: ru2 {} · carrier {}", [("l200a4/LI2_ru2", "s3"), ("l200a4/LI2_carrier", "s3")], fs=10.5, fill="#9aa3b2"))
s.append(T(44, 502, "shared direct targets {} of {} / {} (J {})",
           [("l200a4/overlap/n_shared", "d"), ("l200a4/overlap/n_targets_carrier", "d"), ("l200a4/overlap/n_targets_ru2", "d"),
            ("l200a4/overlap/J_same", "f3")], fs=10.5, fill="#9aa3b2"))
s.append(T(44, 516, "premotor mirror overlap J {}", [("l200a4/overlap/premotor/J_mirror", "f1")], fs=10.5, fill="#9aa3b2"))
s.append(T(362, 550, "base rates x̄: carrier {} · ru2 {} · relay {} — no direct Ti motor edge from carrier or ru2",
           [("l200a4/cells/carrier/x_mean", "f2"), ("l200a4/cells/ru2/x_mean", "f2"), ("l198s/relay/census_x_mean_3seed", "f2")], fs=10.5, fill="#5c6370", anchor="middle"))

# ======================= Panel B — asymmetric necessity =======================
s.append('<rect x="716" y="92" width="660" height="472" fill="#21252b" rx="6"/>')
s.append('<text x="732" y="116" fill="#abb2bf" font-size="15" font-weight="bold">B</text>')
s.append('<text x="752" y="116" fill="#abb2bf" font-size="13">asymmetric necessity: mean duty per arm (bars) · seeds (dots) · base-gain form (◇)</text>')
YB0, YB1 = 456.0, 176.0     # duty 0 / duty 1


def YB(v):
    return YB0 - v * (YB0 - YB1)


GX = [790.0, 990.0, 1190.0]
BW, BP = 26.0, 34.0
GROUPS = [("R", "meanR", "dutyR", "kR", "right Ti · chopped 0.7 Hz"),
          ("R14", "mean14R", "duty14R", "k14R", "right Ti · 1.4-Hz signature"),
          ("L", "meanL", "dutyL", "kL", "left Ti · chopped 0.7 Hz")]
for v in (0.0, 0.2, 0.4, 0.6, 0.8, 1.0):
    s.append(f'<line x1="772" y1="{YB(v):.1f}" x2="1366" y2="{YB(v):.1f}" stroke="#3e4451" stroke-width="1"/>')
    s.append(f'<text class="ytick" x="766" y="{YB(v) + 4:.1f}" fill="#5c6370" font-size="11" text-anchor="end">{v:.1f}</text>')
s.append(f'<text x="742" y="{(YB0 + YB1) / 2:.1f}" fill="#abb2bf" font-size="12" text-anchor="middle" transform="rotate(-90 742 {(YB0 + YB1) / 2:.1f})">mean duty</text>')
bands = R["bands"]
for gi, (gk, mk, dk, kk, gl) in enumerate(GROUPS):
    gx = GX[gi]
    s.append(f'<text x="{gx + 2 * BP + BW / 2:.1f}" y="148" fill="#abb2bf" font-size="12" font-weight="bold" text-anchor="middle">{gl}</text>')
    thr, thr_src = (bands["signature_mean14_min"], "l200r/bands/signature_mean14_min") if gk == "R14" else (bands["super_mean_min"], "l200r/bands/super_mean_min")
    s.append(f'<line class="thr" data-group="{gk}" data-src="{thr_src}" data-v="{thr!r}" x1="{gx - 6:.1f}" y1="{YB(thr):.1f}" x2="{gx + 4 * BP + BW + 6:.1f}" y2="{YB(thr):.1f}" stroke="#abb2bf" stroke-width="1" stroke-dasharray="5 4" opacity="0.7"/>')
    s.append(T(gx + 4 * BP + BW + 4, YB(thr) - 4, "{}", [(thr_src, "f2")], fs=9.5, fill="#9aa3b2", anchor="end"))
    for i, (arm, _) in enumerate(ARMS):
        base = arm == "cutwA"
        pre = "l200r/base" if base else f"l200r/arms/{arm}"
        v = resolve(f"{pre}/{mk}")
        x = gx + i * BP
        s.append(f'<rect class="bar" data-group="{gk}" data-arm="{arm}" data-src="{pre}/{mk}" data-v="{v!r}" x="{x:.1f}" y="{YB(v):.1f}" width="{BW}" height="{YB0 - YB(v):.2f}" fill="{COL[arm]}" opacity="0.85"/>')
        for j, d in enumerate(resolve(f"{pre}/{dk}")):
            dx = x + BW / 2 + ((j % 4) - 1.5) * 4.6
            s.append(f'<circle class="seed" data-group="{gk}" data-arm="{arm}" data-j="{j}" data-src="{pre}/{dk}/{j}" data-v="{d!r}" cx="{dx:.1f}" cy="{YB(d):.1f}" r="1.7" fill="#dcdfe4" opacity="0.6"/>')
        top = min(YB(v), YB(max(resolve(f"{pre}/{dk}"))))
        if arm in ("l2", "l2k", "l2c"):
            top = min(top, YB(resolve(f"l200r/arms/{arm}F/{mk}")) - 5)
        s.append(T(x + BW / 2, top - 5, "{}", [(f"{pre}/{mk}", "f2")], fs=9.5, fill=COL[arm], anchor="middle"))
        s.append(T(x + BW / 2, YB0 + 14, "{}", [(f"{pre}/{kk}", "d")], fs=9.5, fill="#9aa3b2", anchor="middle"))
        if arm in ("l2", "l2k", "l2c"):
            vf = resolve(f"l200r/arms/{arm}F/{mk}")
            cx, cy = x + BW / 2, YB(vf)
            s.append(f'<polygon class="fixed" data-group="{gk}" data-arm="{arm}F" data-src="l200r/arms/{arm}F/{mk}" data-v="{vf!r}" points="{cx:.1f},{cy - 5:.1f} {cx + 5:.1f},{cy:.1f} {cx:.1f},{cy + 5:.1f} {cx - 5:.1f},{cy:.1f}" fill="none" stroke="#ffffff" stroke-width="1.4"/>')
s.append(f'<text x="770" y="{YB0 + 14:.1f}" fill="#5c6370" font-size="9.5" text-anchor="end">k</text>')
# arm legend
for i, (arm, lab) in enumerate(ARMS):
    lx = 740 + (i % 3) * 210
    ly = 492 + (i // 3) * 16
    s.append(f'<rect x="{lx}" y="{ly - 9}" width="11" height="11" fill="{COL[arm]}"/>')
    s.append(f'<text x="{lx + 16}" y="{ly}" fill="#abb2bf" font-size="11">{arm} · {lab}</text>')
s.append('<polygon points="1166,499 1171,504 1166,509 1161,504" fill="none" stroke="#ffffff" stroke-width="1.4"/><text x="1178" y="508" fill="#abb2bf" font-size="11">same arm, base gain</text>')
s.append(T(740, 530, "right: carrier+ru2 − carrier {} [{}, {}] · 1.4 Hz {} → {}",
           [("l200r/contrasts/R_l2c_minus_sc25/mean", "s3"), ("l200r/contrasts/R_l2c_minus_sc25/ci95/0", "s3"), ("l200r/contrasts/R_l2c_minus_sc25/ci95/1", "s3"),
            ("l200r/arms/sc25/mean14R", "f3"), ("l200r/arms/l2c/mean14R", "f3")], fs=11, fill="#e5c07b"))
s.append(T(740, 546, "left: ru2 cut {} [{}, {}] vs base; carrier clamped {} · carrier also cut {} — carrier not needed",
           [("l200r/arms/l2/L_vs_base/mean", "s3"), ("l200r/arms/l2/L_vs_base/ci95/0", "s3"), ("l200r/arms/l2/L_vs_base/ci95/1", "s3"),
            ("l200r/arms/l2k/L_vs_base/mean", "s3"), ("l200r/arms/l2c/L_vs_base/mean", "s3")], fs=11, fill="#c678dd"))
s.append('<rect id="l202-slot" x="1210" y="122" width="158" height="18" rx="3" fill="none" stroke="#5c6370" stroke-dasharray="3 3"/>')
s.append('<text x="1289" y="135" fill="#9aa3b2" font-size="10" text-anchor="middle">L202 replicate: pending</text>')

# ======================= Panel C — phase rotation =======================
s.append('<rect x="24" y="580" width="1352" height="384" fill="#21252b" rx="6"/>')
s.append('<text x="40" y="604" fill="#abb2bf" font-size="15" font-weight="bold">C</text>')
s.append('<text x="60" y="604" fill="#abb2bf" font-size="13">phase rotation: cross-seed right-Ti duty vs the partners\' tone offset (octants, L199 Part B) · pool peak phases vs the tone (Part C)</text>')
XC0, XC1, YC0, YC1, VC = 110.0, 750.0, 912.0, 650.0, 0.6


def XC(d):
    return XC0 + d / 360.0 * (XC1 - XC0)


def YC(v):
    return YC0 - v / VC * (YC0 - YC1)


for v in (0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6):
    s.append(f'<line x1="{XC0:.1f}" y1="{YC(v):.1f}" x2="{XC1:.1f}" y2="{YC(v):.1f}" stroke="#3e4451" stroke-width="1"/>')
    s.append(f'<text class="yctick" x="{XC0 - 6:.1f}" y="{YC(v) + 4:.1f}" fill="#5c6370" font-size="11" text-anchor="end">{v:.1f}</text>')
for d in (0, 90, 180, 270, 360):
    s.append(f'<line x1="{XC(d):.1f}" y1="{YC1:.1f}" x2="{XC(d):.1f}" y2="{YC0:.1f}" stroke="#3e4451" stroke-width="1"/>')
    s.append(f'<text class="xctick" x="{XC(d):.1f}" y="{YC0 + 16:.1f}" fill="#5c6370" font-size="11" text-anchor="middle">{d}°</text>')
s.append(f'<text x="{(XC0 + XC1) / 2:.1f}" y="{YC0 + 32:.1f}" fill="#abb2bf" font-size="12" text-anchor="middle">tone offset between the two seeds\' pair-segments (deg; octant centres, 360° = 0°)</text>')
s.append(f'<text x="58" y="{(YC0 + YC1) / 2:.1f}" fill="#abb2bf" font-size="12" text-anchor="middle" transform="rotate(-90 58 {(YC0 + YC1) / 2:.1f})">cross-seed duty</text>')
for g, col in (("cutwA", COL["cutwA"]), ("sc25", COL["sc25"])):
    th = S["B"]["graphs"][g]["theta"]
    xs, se = th["value"] % 360.0, th["se"]
    s.append(f'<rect class="thband" data-graph="{g}" data-src="l199p/datasets/S/B/graphs/{g}/theta/se" data-v="{se!r}" x="{XC(xs - se):.1f}" y="{YC1:.1f}" width="{XC(xs + se) - XC(xs - se):.2f}" height="{YC0 - YC1:.1f}" fill="{col}" opacity="0.13"/>')
    s.append(f'<line class="theta" data-graph="{g}" data-src="l199p/datasets/S/B/graphs/{g}/theta/value" data-v="{th["value"]!r}" x1="{XC(xs):.1f}" y1="{YC1:.1f}" x2="{XC(xs):.1f}" y2="{YC0:.1f}" stroke="{col}" stroke-width="1.6" stroke-dasharray="6 4"/>')
    oc = S["B"]["octants"][g]
    pts = [(XC(k * 45.0), YC(oc[k % 8])) for k in range(9)]
    s.append(f'<path class="octline" data-graph="{g}" d="M ' + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts) + f'" fill="none" stroke="{col}" stroke-width="2"/>')
    for k in range(9):
        s.append(f'<circle class="oct" data-graph="{g}" data-k="{k}" data-src="l199p/datasets/S/B/octants/{g}/{k % 8}" data-v="{oc[k % 8]!r}" cx="{pts[k][0]:.1f}" cy="{pts[k][1]:.1f}" r="{5 if k < 8 else 3.5}" fill="{col}"/>')
s.append(T(XC(S["B"]["graphs"]["cutwA"]["theta"]["value"]) + 6, YC1 + 14, "θ base {}° (SE {})", [("l199p/datasets/S/B/graphs/cutwA/theta/value", "s0"), ("l199p/datasets/S/B/graphs/cutwA/theta/se", "f0")], fs=11, fill=COL["cutwA"], bold=True))
s.append(T(XC(S["B"]["graphs"]["sc25"]["theta"]["value"]) + 6, YC1 + 14, "θ carrier cut {}° (SE {})", [("l199p/datasets/S/B/graphs/sc25/theta/value", "s0"), ("l199p/datasets/S/B/graphs/sc25/theta/se", "f0")], fs=11, fill=COL["sc25"], bold=True))
s.append(T(XC(S["B"]["graphs"]["sc25"]["theta"]["value"]) + 6, YC1 + 28, "Δθ {}° [{}, {}] · label " + S["B"]["label"],
           [("l199p/datasets/S/B/dtheta/value", "s0"), ("l199p/datasets/S/B/dtheta/ci95/0", "s0"), ("l199p/datasets/S/B/dtheta/ci95/1", "s0")], fs=11, fill="#9aa3b2"))
# (label string is categorical, copied verbatim from the artifact)
s.append('<text x="750" y="958" fill="#5c6370" font-size="10" text-anchor="end">S batch: W150 window, 500-step pulse · octants descriptive, θ registered</text>')

# phase dial (Part C)
CX, CY, RD = 1000.0, 772.0, 118.0
for rr in (0.5, 1.0):
    s.append(f'<circle cx="{CX}" cy="{CY}" r="{RD * rr:.1f}" fill="none" stroke="#3e4451" stroke-width="1"/>')
for d, lab, dx, dy in ((0, "0°", 8, 4), (90, "90°", 0, -6), (180, "180°", -8, 4), (270, "−90°", 0, 16)):
    xa, ya = CX + RD * math.cos(math.radians(d)), CY - RD * math.sin(math.radians(d))
    s.append(f'<line x1="{CX}" y1="{CY}" x2="{xa:.1f}" y2="{ya:.1f}" stroke="#3e4451" stroke-width="1"/>')
    s.append(f'<text x="{xa + dx:.1f}" y="{ya + dy:.1f}" fill="#5c6370" font-size="10.5" text-anchor="{"start" if d == 0 else "end" if d == 180 else "middle"}">{lab}</text>')
s.append(f'<text x="{CX}" y="{CY + RD + 34:.1f}" fill="#9aa3b2" font-size="10.5" text-anchor="middle">peak phase vs the 0.7-Hz tone · arrow length = R (1 = ring)</text>')
C = S["C"]
for g, col in (("cutwA", COL["cutwA"]), ("sc25", COL["sc25"])):
    for pool, dash in (("Ti_fR", ""), ("Ti_eR", ' stroke-dasharray="5 3"')):
        a = C[g]["alpha"][pool]
        xa = CX + RD * a["R"] * math.cos(math.radians(a["mean_deg"]))
        ya = CY - RD * a["R"] * math.sin(math.radians(a["mean_deg"]))
        s.append(f'<line class="phase" data-graph="{g}" data-pool="{pool}" data-src="l199p/datasets/S/C/{g}/alpha/{pool}/mean_deg|l199p/datasets/S/C/{g}/alpha/{pool}/R" data-v="{a["mean_deg"]!r}|{a["R"]!r}" x1="{CX}" y1="{CY}" x2="{xa:.2f}" y2="{ya:.2f}" stroke="{col}" stroke-width="2.4"{dash}/>')
        s.append(f'<circle cx="{xa:.1f}" cy="{ya:.1f}" r="4" fill="{col}"/>')
LX = 1150
s.append(f'<text x="{LX}" y="672" fill="#abb2bf" font-size="12" font-weight="bold">pool peak phases (S, n=96)</text>')
s.append(f'<line x1="{LX}" y1="690" x2="{LX + 26}" y2="690" stroke="#abb2bf" stroke-width="2.4"/><text x="{LX + 32}" y="694" fill="#abb2bf" font-size="11">flexor R</text>')
s.append(f'<line x1="{LX + 100}" y1="690" x2="{LX + 126}" y2="690" stroke="#abb2bf" stroke-width="2.4" stroke-dasharray="5 3"/><text x="{LX + 132}" y="694" fill="#abb2bf" font-size="11">extensor R</text>')
s.append(T(LX, 720, "base: flex {}° (R {})", [("l199p/datasets/S/C/cutwA/alpha/Ti_fR/mean_deg", "f0"), ("l199p/datasets/S/C/cutwA/alpha/Ti_fR/R", "f2")], fs=11, fill=COL["cutwA"]))
s.append(T(LX, 735, "      ext {}° (R {})", [("l199p/datasets/S/C/cutwA/alpha/Ti_eR/mean_deg", "f0"), ("l199p/datasets/S/C/cutwA/alpha/Ti_eR/R", "f2")], fs=11, fill=COL["cutwA"]))
s.append(T(LX, 760, "carrier cut: flex {}° (R {})", [("l199p/datasets/S/C/sc25/alpha/Ti_fR/mean_deg", "f0"), ("l199p/datasets/S/C/sc25/alpha/Ti_fR/R", "f2")], fs=11, fill=COL["sc25"]))
s.append(T(LX, 775, "      ext {}° (R {})", [("l199p/datasets/S/C/sc25/alpha/Ti_eR/mean_deg", "f0"), ("l199p/datasets/S/C/sc25/alpha/Ti_eR/R", "f2")], fs=11, fill=COL["sc25"]))
s.append(T(LX, 802, "flex − ext: {}° → {}°", [("l199p/datasets/S/C/cutwA/Delta/mean_deg", "s0"), ("l199p/datasets/S/C/sc25/Delta/mean_deg", "s0")], fs=12, fill="#abb2bf", bold=True))
s.append(f'<text x="{LX}" y="820" fill="#9aa3b2" font-size="11">the extensor moves; the flexor stays —</text>')
s.append(f'<text x="{LX}" y="835" fill="#9aa3b2" font-size="11">about a third of a period, not antiphase</text>')
s.append(f'<text x="{LX}" y="860" fill="#5c6370" font-size="11">Part C {C["label"]} · base {C["cutwA"]["label"]} · cut {C["sc25"]["label"]}</text>')

# footer + legend
s.append('<text x="30" y="986" fill="#9aa3b2" font-size="11.5">orange = base cutwA · green = carrier DNp33-L removed (sc25) · purple = ru2 IN07B031-R · blue = relay IN06B033-L (A) / ru2 cut with carrier replay-clamped at base (B) · yellow = carrier + ru2 removed</text>')
s.append('<text x="30" y="1002" fill="#9aa3b2" font-size="11">one model class, one base (k=24), chopped 0.7-Hz classifier + 1.4-Hz panel · Panel B is one batch (L200 B44); its right-side wipe is post hoc pending L202</text>')
s.append('<text x="1370" y="1002" fill="#9aa3b2" font-size="10.5" text-anchor="end">every number asserted vs stored JSON/CSV · fig6_verify.py · L184/L190/L198/L199/L200</text>')
s.append("</svg>")
svg = "\n".join(s) + "\n"
open(f"{OUT}/fig6_circuit.svg", "w").write(svg)
subprocess.run(["rsvg-convert", "-w", str(W), "-o", f"{OUT}/fig6_circuit.png", f"{OUT}/fig6_circuit.svg"], check=True)

# ---------------- caption with the per-number pointer table ----------------
# Prose numbers are written as «pointer|fmt» and resolved here, so the caption
# can only state stored values; each one is also logged for fig6_verify.py.
PROSE = """**Figure 6 — the circuit: a carrier, a relay, and a cord interneuron the carrier's phenotype needs.** BANC female cord, k=24 cutwA base, rate model at the certified matched operating point. Every number in the figure and in this caption is read from a stored artifact; the table below gives the pointer for each one, and `fig6_verify.py` resolves every pointer against the files themselves.

**(A) Wiring, schematic.** Node positions are arbitrary; counts and signs are not. The carrier DNp33-L (gi «l200a4/cells/carrier/gi|d», descending, excitatory) has «l200a4/cells/carrier/out_edges|d» output edges and none onto a tibia motor neuron. «l184e?target_class=direct right-Ti premotor#count|d» of them land on direct right-tibia premotor cells (L184 Q2). One of those is the inhibitory relay IN06B033-L (gi «l198s/relay/cell/gi|d»), reached by a «l198s/relay/carrier_to_relay/syn|d»-synapse edge. The relay has «l198s/relay/direct_onto/Ti_fR/n_edges|d» direct edge («l198s/relay/direct_onto/Ti_fR/syn|d» synapses) onto the right tibia flexor pool («l198s/relay/direct_onto/Ti_fR/targets|d» motor neurons). Cutting only the carrier-to-relay edge raised the right chopped duty by «l190r/summary/E-edge/delta|s3». Removing the carrier on the same seeds raised it by «l190r/summary/sc25/delta|s3», so the edge cut gives «ratio(l190r/summary/E-edge/delta;l190r/summary/sc25/delta)|pct» of the carrier's shift. That is a point ratio with no interval. The edge cut's 1.4-Hz duty was «l190r/summary/E-edge/mid|f3» (L190). The carrier's other «sub(l184e?direction=out#count;l184e?target_class=direct right-Ti premotor#count)|d» outputs («l184e?target_class=ventral_nerve_cord_intrinsic#count|d» onto cord interneurons, «l184e?target_class=other motor#count|d» onto other motor neurons) are drawn as a fan. They are the candidate substrate of the 1.4-Hz signature by elimination only, because relay removal and the edge cut both leave that signature at base (L187, L190). The inhibitory cord interneuron ru2, IN07B031-R (gi «l200a4/cells/ru2/gi|d», «l200a4/cells/ru2/out_edges|d» outputs), sends «l200a4/cells/ru2/one_hop/PM_L/edges|d» edges into the left tibia premotor pool («l200s/PM_L_n|comma» cells) and «l200a4/cells/ru2/one_hop/PM_R/edges|d» into the right one («l200s/PM_R_n|comma»). Its signed two-hop weight goes mostly onto both extensor pools («l200a4/cells/ru2/two_hop/Ti_eL/signed|f1» left, «l200a4/cells/ru2/two_hop/Ti_eR/signed|f1» right). Its two-hop laterality index LI2 is «l200a4/LI2_ru2|s3», against the carrier's «l200a4/LI2_carrier|s3». The two cells share «l200a4/overlap/n_shared|d» of «l200a4/overlap/n_targets_carrier|d» / «l200a4/overlap/n_targets_ru2|d» direct targets (Jaccard «l200a4/overlap/J_same|f3»), and their mirrored premotor target sets do not overlap (J «l200a4/overlap/premotor/J_mirror|f1»). The base rates are carrier «l200a4/cells/carrier/x_mean|f2», ru2 «l200a4/cells/ru2/x_mean|f2» and relay «l198s/relay/census_x_mean_3seed|f2» (L200 A4, L198).

**(B) Asymmetric necessity.** L200 batch B44: 16 seeds per arm, fresh seeds «l200r/seeds/0|d»–«l200r/seeds/15|d». Bars show mean duty, dots individual seeds, and open diamonds the same arm at the base gain (`l2F`, `l2kF`, `l2cF`). Removing the carrier raises the right chopped duty to «l200r/arms/sc25/meanR|f3», with a 1.4-Hz signature of «l200r/arms/sc25/mean14R|f3». Removing ru2 as well brings the right duty down to «l200r/arms/l2c/meanR|f3» and the signature to «l200r/arms/l2c/mean14R|f3». On paired seeds the double removal minus carrier removal is «l200r/contrasts/R_l2c_minus_sc25/mean|s3» [«l200r/contrasts/R_l2c_minus_sc25/ci95/0|s3», «l200r/contrasts/R_l2c_minus_sc25/ci95/1|s3»]. On the left, removing ru2 flips the duty to «l200r/arms/l2/meanL|f3», «l200r/arms/l2/L_vs_base/mean|s3» [«l200r/arms/l2/L_vs_base/ci95/0|s3», «l200r/arms/l2/L_vs_base/ci95/1|s3»] above base («l200r/base/meanL|f3»). The flip stays intact when the carrier's whole rate trajectory is replay-clamped at its base value («l200r/arms/l2k/meanL|f3», carrier rate «l200r/arms/l2k/x_carrier|f2» = base «l200r/base/x_carrier|f2») and when the carrier is removed outright («l200r/arms/l2c/meanL|f3»). So ru2's left effect does not need the carrier, while the carrier's right-side regime needs ru2. Dashed lines mark the registered bars: SUPER mean «l200r/bands/super_mean_min|f2» on the chopped readouts and signature mean «l200r/bands/signature_mean14_min|f2» on the 1.4-Hz readout. The k row counts seeds with duty ≥ .5. Limits: the right-side wipe (item 6 of L200) is post hoc and comes from one batch. Its registered replicate, L202, which also supplies the base-gain carrier comparator sc25F and the ru2 activity clamp, had not landed when this figure was drawn, so its slot is marked pending. The carrier-only arm has no base-gain form in this batch.

**(C) Phase rotation.** L199 dataset S: «l199p/datasets/S/n|d» seeds, W«l199p/datasets/S/W|d» window, «l199p/datasets/S/pulse|d»-step pulse. Left: mean cross-seed duty of right-tibia pair-segments, binned by the tone offset between the two seeds' segments into eight octants. The octants are descriptive, and 360° repeats 0°. Dashed lines and shading show the registered first-harmonic preferred offset θ ± SE: base «l199p/datasets/S/B/graphs/cutwA/theta/value|s0»° (SE «l199p/datasets/S/B/graphs/cutwA/theta/se|f0»), carrier removed «l199p/datasets/S/B/graphs/sc25/theta/value|s0»° (SE «l199p/datasets/S/B/graphs/sc25/theta/se|f0»). The rotation is Δθ «l199p/datasets/S/B/dtheta/value|s0»° [«l199p/datasets/S/B/dtheta/ci95/0|s0», «l199p/datasets/S/B/dtheta/ci95/1|s0»]. The registered label is Hq: the removed graph falls outside the 0 ± 45° band, so the pools do not go to antiphase. Right: tone phase of the right flexor and extensor peaks (first harmonic; arrow length = resultant R). In the base graph the two pools peak together: flexor «l199p/datasets/S/C/cutwA/alpha/Ti_fR/mean_deg|f0»°, extensor «l199p/datasets/S/C/cutwA/alpha/Ti_eR/mean_deg|f0»°, difference «l199p/datasets/S/C/cutwA/Delta/mean_deg|s0»°. With the carrier removed the flexor barely moves («l199p/datasets/S/C/sc25/alpha/Ti_fR/mean_deg|f0»°) while the extensor moves to «l199p/datasets/S/C/sc25/alpha/Ti_eR/mean_deg|f0»° and loosens its locking (R «l199p/datasets/S/C/cutwA/alpha/Ti_eR/R|f2» → «l199p/datasets/S/C/sc25/alpha/Ti_eR/R|f2»). The difference becomes «l199p/datasets/S/C/sc25/Delta/mean_deg|s0»°, about a third of a period. Scope: under the 250-step pulse (dataset W) the rotation is only «l199p/datasets/W/B/dtheta/value|s0»°, so the phrase "500-step pulse" must travel with this panel.

Scope of the whole figure: one model class, one base (k=24), the chopped 0.7-Hz classifier plus the 1.4-Hz panel. The wiring in A is one-hop and two-hop static weight, not a measured transfer function.
"""
import re
CAP_PTRS = []


def _sub(m):
    src, f = m.group(1).rsplit("|", 1)
    v = resolve(src)
    CAP_PTRS.append({"id": f"cap{len(CAP_PTRS)}", "src": src, "v": v, "fmt": f})
    return fmt(v, f)


prose = re.sub(r"«([^»]+)»", _sub, PROSE)
rows = ["| element | value (stored) | shown as | artifact pointer |", "|---|---|---|---|"]
for eid, src, v, f in REG:
    rows.append(f"| `{eid}` | {v!r} | {fmt(v, f)} | `{src}` |")
crow = ["| # | value (stored) | shown as | artifact pointer |", "|---|---|---|---|"]
for c in CAP_PTRS:
    crow.append(f"| `{c['id']}` | {c['v']!r} | {fmt(c['v'], c['fmt'])} | `{c['src']}` |")
FILE_KEY = "\n".join(f"- `{k}` = `{os.path.relpath(v, P)}`" for k, v in FILES.items())
open(f"{OUT}/fig6_caption.md", "w").write(
    prose + "\n### Per-number artifact pointers\n\nPointer aliases:\n" + FILE_KEY +
    "\n\n`ratio(a;b)` and `sub(a;b)` are the only derived values (a/b, a−b of two stored numbers). Bar heights, seed dots, base-gain diamonds, octant points, θ lines and phase arrows carry their pointers as `data-src` on the SVG element; the first table lists every number printed as text in the figure, the second every number in the caption prose, in order of appearance.\n\n#### Figure text\n\n" +
    "\n".join(rows) + "\n\n#### Caption prose\n\n" + "\n".join(crow) + "\n")
json.dump({"figure": [{"id": e, "src": s_, "v": v, "fmt": f} for e, s_, v, f in REG], "caption": CAP_PTRS},
          open(f"{OUT}/fig6_pointers.json", "w"), indent=1)
print(f"fig6 drawn: {len(REG)} text-borne figure numbers + {len(CAP_PTRS)} caption numbers resolved; svg {len(svg)} bytes; png rendered")
