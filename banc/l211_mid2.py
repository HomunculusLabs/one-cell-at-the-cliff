# ================= L211 MID2 (bridge; l211_mid2.py) =======================
# The ONLY code between CERT-HEAD4 and CERT-HEAD5: the stdlib import that
# L206's search-information block needs (l206_tail.py line 8, which sits
# ABOVE the certified 22-263 slice and is therefore not inherited).
import heapq
assert hasattr(heapq, "heappop") and hasattr(heapq, "heappush")
log("[MID2] heapq available for the certified SI block")
