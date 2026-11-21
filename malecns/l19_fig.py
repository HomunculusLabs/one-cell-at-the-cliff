"""L19 figure v2: the escape gesture, descriptive (owner movement law — lab
evidence only, never app-side motion).

Three panels (v1 lesson: TTMn at 239x noise flattened the leg pools —
split scales):
  A  : leg antagonist pool traces (own scale) + lead annotation
  A2 : TTMn jump family (own scale, the gesture's dominant target)
  B  : tibia joint-extension command theta(t) = ext - flex (Ti)

Reads l19/gesture_mean.npz + l19/results_l19.json + l19/pool_amplitudes.json;
writes l19/gesture.svg and (rsvg-convert) l19/gesture.png.
"""
import json
import subprocess

import numpy as np

d = np.load("l19/gesture_mean.npz")
res = json.load(open("l19/results_l19.json"))
res["pool_amp"] = json.load(open("l19/pool_amplitudes.json"))
tens = d["tensor"]
T = tens.shape[1]
EVENT = res["config"]["EVENT"]
DT = res["config"]["DT"]

leg_tr = {
    "Ti ext": tens[d["Ti_e"]].mean(0),
    "Ti flex": tens[d["Ti_f"]].mean(0),
    "Tr ext": tens[d["Tr_e"]].mean(0),
    "Tr flex": tens[d["Tr_f"]].mean(0),
}
COLORS = {"Ti ext": "#ffb454", "Ti flex": "#e06c75", "Tr ext": "#98c379",
          "Tr flex": "#c678dd"}
ttm_tr = tens[d["ttm"]].mean(0)
theta = leg_tr["Ti ext"] - leg_tr["Ti flex"]

MX, W_P = 80, 880
H_A, H_T, H_B = 280, 130, 160
Y_A = 56
Y_T = Y_A + H_A + 56
Y_B = Y_T + H_T + 52
TOT_W = MX + W_P + 300
TOT_H = Y_B + H_B + 66
ymA = max(float(np.abs(v).max()) for v in leg_tr.values()) * 1.25
ymT = float(np.abs(ttm_tr).max()) * 1.15
ymB = float(np.abs(theta).max()) * 1.2


def xpx(k):
    return MX + W_P * k / (T - 1)


def ym(y0, h, v, m):
    return y0 + h * (1 - (v / (2 * m) + 0.5))


def poly(y, f):
    return " ".join(f"{xpx(k):.1f},{f(y[k]):.1f}" for k in range(0, T, 2))


svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{TOT_W}" '
       f'height="{TOT_H}" viewBox="0 0 {TOT_W} {TOT_H}">',
       '<rect width="100%" height="100%" fill="#1b2129"/>',
       '<style>text{font-family:monospace}.t{fill:#abb2bf}.s{fill:#5c6370}'
       '.l{font-size:13px}.b{font-size:15px;fill:#e5e9f0}</style>',
       '<text x="24" y="28" class="b">L19 full-chain escape gesture: '
       'looming &#8594; DN port &#8594; DNp01-04 &#215;200 &#8594; lit5x '
       'taus &#8594; motor (seed-mean, DESCRIPTIVE)</text>']


def frame(y0, h, ym_v, tag):
    svg.append(f'<rect x="{MX}" y="{y0}" width="{W_P}" height="{h}" '
               f'fill="#21272f" stroke="#3a4152"/>')
    svg.append(f'<rect x="{xpx(0)}" y="{y0}" width="{xpx(EVENT)-xpx(0)}" '
               f'height="{h}" fill="#3a4150" opacity="0.55"/>')
    zy = y0 + h * 0.5
    svg.append(f'<line x1="{MX}" y1="{zy}" x2="{MX+W_P}" y2="{zy}" '
               f'stroke="#3a4152" stroke-dasharray="4 4"/>')
    for s_ in (-1, 1):
        y = ym(y0, h, s_ * ym_v, ym_v)
        svg.append(f'<text x="{MX-8}" y="{y+4}" class="s" font-size="11" '
                   f'text-anchor="end">{s_*ym_v:+.3f}</text>')
    for k in range(0, T, 40):
        svg.append(f'<text x="{xpx(k)}" y="{y0+h+16}" class="s" '
                   f'font-size="11" text-anchor="middle">{k}</text>')
    svg.append(f'<text x="{MX+W_P//2}" y="{y0+h+32}" class="s" font-size="11"'
               f' text-anchor="middle">steps (DT {DT*1000:.0f} ms) {tag}</text>')


# --- panel A: leg pools ------------------------------------------------------
svg.append(f'<text x="{MX}" y="{Y_A-10}" class="l t">A &#183; leg antagonist '
           f'pools (seed-mean dX, own scale)</text>')
frame(Y_A, H_A, ymA, "")
for name, yv in leg_tr.items():
    svg.append(f'<polyline points="{poly(yv, lambda v: ym(Y_A, H_A, v, ymA))}"'
               f' fill="none" stroke="{COLORS[name]}" stroke-width="2"/>')
pe, pf = leg_tr["Ti ext"], leg_tr["Ti flex"]
ke, kf = int(np.argmax(pe)), int(np.argmax(pf))
lead = res["phasing"]["loom"]["Ti"]["mean"]
svg.append(f'<line x1="{xpx(ke)}" y1="{ym(Y_A,H_A,pe[ke],ymA)}" x2="{xpx(ke)}"'
           f' y2="{Y_A}" stroke="#ffb454" stroke-width="1" opacity="0.5"/>')
svg.append(f'<line x1="{xpx(kf)}" y1="{ym(Y_A,H_A,pf[kf],ymA)}" x2="{xpx(kf)}"'
           f' y2="{Y_A}" stroke="#e06c75" stroke-width="1" opacity="0.5"/>')
svg.append(f'<text x="{xpx(ke)+4}" y="{Y_A+18}" fill="#ffb454" font-size="12">'
           f'Ti ext t_pk {ke}</text>')
svg.append(f'<text x="{xpx(kf)+4}" y="{Y_A+36}" fill="#e06c75" font-size="12">'
           f'Ti flex t_pk {kf} (lead {lead:+.0f}, NOT sc &#8212; flex '
           f'{res["pool_amp"]["Ti flex"]["snr"]:.1f}&#215;noise)</text>')
lx = MX + W_P + 14
svg.append(f'<text x="{lx}" y="{Y_A-10}" class="l t">pool SNR vs noise</text>')
for i, name in enumerate(leg_tr):
    y = Y_A + 14 + i * 22
    svg.append(f'<line x1="{lx}" y1="{y-4}" x2="{lx+22}" y2="{y-4}" '
               f'stroke="{COLORS[name]}" stroke-width="3"/>')
    svg.append(f'<text x="{lx+28}" y="{y}" class="l t">{name} &#183; '
               f'{res["pool_amp"][name]["snr"]:.1f}&#215;</text>')

# --- panel A2: TTMn ---------------------------------------------------------
svg.append(f'<text x="{MX}" y="{Y_T-10}" class="l t">A2 &#183; TTMn jump '
           f'family &#183; {res["pool_amp"]["TTMn (jump)"]["snr"]:.0f}&#215; '
           f'noise &#183; t_pk {res["jump_timing"]["ttm"]} vs leg '
           f'{res["jump_timing"]["leg"]} = jump-first (direct DNp path)</text>')
frame(Y_T, H_T, ymT, "")
svg.append(f'<polyline points="{poly(ttm_tr, lambda v: ym(Y_T, H_T, v, ymT))}"'
           f' fill="none" stroke="#61afef" stroke-width="2.5"/>')

# --- panel B: theta ---------------------------------------------------------
svg.append(f'<text x="{MX}" y="{Y_B-10}" class="l t">B &#183; tibia '
           f'joint-extension command &#952;(t) = ext &#8722; flex (Ti) '
           f'&#8212; monophasic stroke, phasing not expressed in this route'
           f'</text>')
frame(Y_B, H_B, ymB, "")
svg.append(f'<polyline points="{poly(theta, lambda v: ym(Y_B, H_B, v, ymB))}"'
           f' fill="none" stroke="#e5c07b" stroke-width="2.5"/>')
kt = int(np.argmax(np.abs(theta)))
svg.append(f'<circle cx="{xpx(kt)}" cy="{ym(Y_B,H_B,theta[kt],ymB)}" r="4" '
           f'fill="#e5c07b"/>')
svg.append(f'<text x="{xpx(kt)+8}" y="{ym(Y_B,H_B,theta[kt],ymB)+18}" '
           f'class="l t">peak ext-command @ {kt}</text>')
svg.append(f'<text x="24" y="{TOT_H-18}" class="s" font-size="11">'
           f'chain: LC4/16/11/12 volley &#8594; DN port (self-cos '
           f'{res["dn_port"]["self_cos"]:+.2f}) &#8594; DNp01-04&#215;200 '
           f'&#8594; motor (peak self-cos '
           f'{res["motor_peak"]["loom_self"]:+.2f}, clamp kills '
           f'{res["motor_peak"]["clamp_self"]:+.2f}) &#8212; lab evidence '
           f'only, never app-side motion</text>')
svg.append("</svg>")
open("l19/gesture.svg", "w").write("\n".join(svg))
subprocess.run(["rsvg-convert", "-o", "l19/gesture.png", "l19/gesture.svg"],
               check=True)
print(f"wrote l19/gesture.svg + gesture.png ({TOT_W}x{TOT_H})")
