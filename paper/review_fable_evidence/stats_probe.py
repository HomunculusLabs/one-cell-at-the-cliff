import math
def wilson(k, n, z=1.959963984540054):
    p = k / n; d = 1 + z*z/n; c = (p + z*z/(2*n)) / d; h = z * math.sqrt((p*(1-p) + z*z/(4*n)) / n) / d
    return (round(c - h, 3), round(c + h, 3))
def fisher(a, n1, b, n2):
    K = a + b; N = n1 + n2
    def pmf(x): return math.comb(n1, x) * math.comb(n2, K - x) / math.comb(N, K)
    p0 = pmf(a); lo, hi = max(0, K - n2), min(n1, K)
    return sum(pmf(x) for x in range(lo, hi + 1) if pmf(x) <= p0 * (1 + 1e-9))
def show(lbl, a, n1, b, n2):
    print(f"{lbl:58s} {a}/{n1}={a/n1:.3f} {wilson(a,n1)} vs {b}/{n2}={b/n2:.3f} {wilson(b,n2)} diff {a/n1-b/n2:+.3f} Fisher p={fisher(a,n1,b,n2):.3g}")
show("twin (reported pool B25+B26) vs cutwA 9-batch", 12, 32, 43, 144)
show("twin incl. un-jittered B28 vs cutwA all 12 batches", 21, 48, 55, 192)
show("twin vs cutwA, same three batches (B25,B26,B28)", 21, 48, 14, 48)
show("carrier (8-batch) vs twin (B25+B26)", 124, 128, 12, 32)
show("carrier incl. B28 vs twin incl. B28", 138, 144, 21, 48)
show("eMotTop5 pooled vs cutwA 9-batch", 14, 32, 43, 144)
show("eMotBot5 pooled vs cutwA 9-batch", 8, 32, 43, 144)
show("eOutMot (all 10) pooled vs eMotTop5 pooled", 21, 32, 14, 32)
show("eOutMot (all 10) pooled vs eMotBot5 pooled", 21, 32, 8, 32)
show("eOutMot (all 10) pooled vs cutwA 9-batch", 21, 32, 43, 144)
show("eOutMot (all 10) pooled vs carrier 8-batch", 21, 32, 124, 128)
show("silW pooled vs cutng25 same batches B30+B33", 28, 32, 32, 32)
show("silW pooled vs cutwA same batches B30+B33", 28, 32, 10, 32)
show("rank-24 step: cutng23 (5 batches) vs cutwA all", 0, 80, 55, 192)
show("full baseline (B16-B26) vs cutwA all 12", 66, 176, 55, 192)
for k, n in ((5, 5), (4, 5), (0, 5), (0, 64), (449, 449), (518, 518), (348, 433), (361, 500), (26, 36), (24, 34), (26, 34), (25, 34)):
    print(f"Wilson {k}/{n}: {wilson(k, n)}")
print("motor-edge dose rates (0, bot5, top5, all10):", [round(x, 3) for x in (43/144, 8/32, 14/32, 21/32)])
print("ratio band/eOutInt mass:", round(0.0544 / 0.005599, 2), "| extra beyond k19: wA", round(0.2286 - 0.1946, 4), "ng25", round(0.2350 - 0.1946, 4), "25p", round(0.2346 - 0.1946, 4))
g = dict(cutng25=0.1454454553127289, cutng25p=0.1435265743732452, eOutInt=0.1455211400985718, eOutMot=0.14284219264984138, eOutAll=0.1454361426830292, eIn=0.14522001743316648, eAll=0.1454454553127289, eMotTop5=0.1436134350299835, eMotBot5=0.14367126345634465, eMotIn=0.1451841366291046, cutng23=0.14696856379508969, cutng29=0.1442639136314392, cutng19=0.15025991678237915, cut58=0.15417299151420596, cutk5=0.13981970071792604, full=0.153125)
print("re-matched gain relative to cutwA (0.143658):", {k: f"{(v / 0.14365819573402408 - 1)*100:+.2f}%" for k, v in g.items()})
