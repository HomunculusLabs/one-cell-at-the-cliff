"""
peabrain — the marriage: fly nervous system + duck talking layer.

Per visitor message:
  1. the duck's original rules ENGINE (~/critters/puddle/engine.py) routes the
     text to a situation — we keep its trigger routing and discard its mood
     logic; moods now come from the brain
  2. the situation becomes a sensory event; the fly brain runs 2 s of sim;
     the peak-hold mood axes update
  3. the mood TAG (her trained vocabulary) is read out of the axes
  4. one synthetic preamble turn in that mood (voice pools) primes her
     8-turn context — in-distribution mood momentum, exactly how the
     storybook taught her moods to carry
  5. the 12M talking layer speaks

The gate question this answers: does the talking layer AGREE with the brain?
We measure tag agreement on a scripted conversation.
"""
import random
import re
import sys
from contextlib import contextmanager

sys.path.append("/home/t3rpz/critters/puddle")

import sentencepiece as spm
import torch
from transformers import LlamaForCausalLM

import voice                                   # puddle voice pools
from brain import FlyBrain
from engine import PuddleMind                  # puddle routing only
from mood import MoodState
from senses import DuckSenses

CARD = "Bill, bold, female, loves peas"
NAME = "Bill"
DUCK = "/home/t3rpz/critters/puddle/out/hf"
TOKENIZER = f"{DUCK}/tokenizer.model"

SIT_TO_EVENT = {
    "feeding": "peas", "tin": "tin", "eat_q": None, "empty_bowl": None,
    "rake": "rake", "umbrella": "umbrella", "hose": "hose",
    "picked_up": "hold", "put_down": "pet", "swat": "swat",
    "pet_ok": "pet", "pet_shy": "pet", "greet": "greet",
    "greet_again": "greet", "goats": "goats", "gift_shiny": "shiny",
    "name_ask": "greet", "name_wrong": "greet", "mislabel": "greet",
    "kind": "pet", "lovebomb": "pet", "sorry": None, "rain": "water",
    "water": "water", "night": None, "gibberish": None, "foreign": None,
    "how_are_you": None, "off_topic": None, "home_q": None,
    "what_are_you": None,
}
KIND_EVENTS = ("pet", "greet", "goats", "peas", "tin", "water", "shiny", "slug")
MEAN_EVENTS = ("swat", "hose")
PLAS_ETA = 0.01      # Hebbian learning rate on DAN-input synapses
PLAS_CAP = 0.5       # per-edge weight change cap

# ---- sleep consolidation (L3; Dag 2019 eLife.42786, Berry 2015 Cell) ----
NIGHT_ETA = 0.02     # replay potentiation ~= 2x the day eta (vFB arm)
NIGHT_CAP = 0.75     # replayed edges may grow deeper than day-written ones
DREAM_GAIN = 0.3     # replay fires the senses at reduced, dreamlike gain
TOP_FRAC = 0.10      # only the day's top-decile salience is admitted to LTM
MAX_REPLAYS = 5      # bound on one night's pass
NIGHT_DOWNSCALE = 0.98   # global dFB-style downscale, per consolidation pass
                         # (NOT per 45 s world tick: 0.98^640 ~ 3e-6 would
                         # erase every delta by dawn — a pass is the unit)

# ---- curiosity actions (L5) ----
# Salience is dopamine, tau 15 s -- always decayed by the next 45 s world
# tick. Interesting moments therefore bank into a slow per-session curiosity
# drive (tau ~30 min at tick cadence, spent only when drives are low).
CURIOSITY_EVENT = {"shiny": 0.50, "slug": 0.30}   # what a forage find banks
CURIOSITY_GATE = 0.35        # above this (and drives low), she investigates
INVESTIGATE_P = 0.6          # chance a curious tick becomes a walk
INVESTIGATE = {
    "goats": ("to_fence",
              "waddled to the fence to study the goats -- Cinnamon stared right back"),
    "fence": ("to_fence",
              "paced the fence line, checking every gap for interesting noises"),
    "boot":  ("to_boot",
              "circled the rubber boot at the fence post, neck low, one eye on it"),
}

# ---- dream theater (L4; rides on the L3 replay pass) ----
DREAM_P = 0.35       # chance a deep-night tick surfaces a dream — the small
                     # hours hold a few dreams, not one per 45 s tick
MAX_DREAMS = 3       # nightly cap
DREAM_PARTNERS = ("the goats", "Cinnamon", "Chichi", "the boot",
                  "the pond reeds", "the treat tin", "a kind stranger")
DREAM_PARTNER = {"goats": "the goats", "tin": "the treat tin"}  # never
                     # re-pair an event with its own native partner
DREAM_TPL = {        # the day replayed, recombined (partner slot {p})
    "peas":     "dreamed of a rain of peas, {p} catching them in a leaf",
    "tin":      "dreamed of the treat tin rattling somewhere far, {p} shaking it like a song",
    "slug":     "dreamed of a slug as big as the boot, {p} riding it past the reeds",
    "rake":     "dreamed of the rake, but it swept itself while {p} watched politely",
    "umbrella": "dreamed of the umbrella opening like a slow black flower over {p}",
    "pet":      "dreamed of being petted by {p}, every stroke a warm tide",
    "swat":     "dreamed of the swat, but it landed soft as a leaf, and {p} looked sorry",
    "hose":     "dreamed of the hose coiled up asleep like a friendly snake, {p} hushing it",
    "goats":    "dreamed of the goats, and {p} translated their grumbles into compliments",
    "greet":    "dreamed of being greeted first, {p} bowing like an old friend",
    "water":    "dreamed of rain on the pond, {p} counting the rings out loud",
    "shiny":    "dreamed of the shiny thing still shiny underwater, {p} diving for it",
    "hold":     "dreamed of being lifted by {p}, drifting slow as a dandelion seed",
}
DREAM_DEFAULT = "dreamed of it all again, and {p} was there too"

# where she goes: decided here (brain/rules), rendered by the client.
# The app never moves her on its own — movement she didn't earn is a puppet.
INTENTS = {
    "tin": "to_you", "feeding": "to_bowl", "eat_q": "to_bowl",
    "empty_bowl": "to_bowl", "goats": "to_fence", "rake": "to_boot",
    "umbrella": "to_boot", "water": "to_pond", "rain": "to_pond",
    "night": "settle", "pet_ok": "stay", "pet_shy": "back_away",
    "swat": "back_away", "hose": "back_away", "picked_up": "stay",
    "greet": "to_you", "greet_again": "to_you",
}

def mend_tag(raw):
    """The garden's tag-mending, minimal: a truncated or missing mood tag
    becomes a valid one (sampled `[hun quack...` -> mended line), so a
    mid-token sampling hiccup can never ship a broken tag."""
    m = re.match(r"^\s*\[[a-z]+:[a-z]+\]\s*", raw)
    if m:
        return raw
    stripped = re.sub(r"^\s*\[[a-z:\s]*", "", raw).strip()
    good = re.search(r"\[([a-z]+):([a-z]+)\]", raw)
    if good:
        return f"[{good.group(1)}:{good.group(2)}] {stripped}"
    return f"[neutral:low] {stripped}"


class Session:
    """One visitor's private inner life: their own mood axes, trust, drives,
    their own snapshot of the brain's activity vector, and their own learned
    synaptic changes on the reward circuit. The wiring is shared hardware;
    the trajectory -- and the relationship -- are theirs alone."""
    def __init__(self, senses, card=CARD, seed=0):
        self.mood = MoodState(senses)
        self.mood.observe(30.0)                    # arrive settled
        self.mind = PuddleMind(card, random.Random(seed))
        self.memory = []
        self.X = None                              # brain state snapshot
        self.last_seen = None                      # wall clock, for idle decay
        self.plas_d = None                         # DAN-synapse deltas (set by host)
        self.last_reply_tag = None                 # her own last mood tag (Lane A lever)
        self.diary = []                            # her life log (world session)
        self.day_log = []                          # today's events, DAN-at-acquisition
        self.night_stamp = None                    # last date a night pass ran
        self.curiosity = 0.0                       # banked salience (L5)
        self.curious_at = None                     # where it last pointed her
        self.hoard = 0                             # shinies she kept (L10)
        self.parade_ticks = 0                      # showing them off, a few beats


class DuckBridge:
    def __init__(self, device="cuda"):
        self.brain = FlyBrain(device=device)
        self.brain.op_gain = 0.95 / self.brain.rho
        self.senses = DuckSenses(self.brain)
        self.rng = random.Random(20261108)
        self.sp = spm.SentencePieceProcessor(model_file=TOKENIZER)
        self.llm = LlamaForCausalLM.from_pretrained(
            DUCK, torch_dtype=torch.float32).to(device).eval()
        self.bos, self.eos = self.sp.bos_id(), self.sp.eos_id()
        self.user, self.bee = self.sp.piece_to_id("<|user|>"), self.sp.piece_to_id("<|bee|>")
        self.agree = [0, 0]
        # every edge INTO a dopaminergic reward neuron: the substrate where
        # each visitor's trust is written as synaptic weight change
        W = self.brain.W
        crow = W.crow_indices().to(torch.long)
        col = W.col_indices().to(torch.long)
        dan_rows = self.senses.probes["DAN"]
        idx = torch.cat([torch.arange(s, e, device=self.brain.device)
                         for s, e in zip(crow[dan_rows].tolist(),
                                         crow[dan_rows + 1].tolist())])
        self.dan_src = col[idx]
        self.dan_dst = torch.repeat_interleave(
            dan_rows, crow[dan_rows + 1] - crow[dan_rows])
        print(f"plasticity substrate: {len(self.dan_src)} synapses "
              f"into {len(dan_rows)} DAN neurons")

    def open_session(self, seed=0):
        s = Session(self.senses, seed=seed)
        s.plas_d = torch.zeros(len(self.dan_src), device=self.brain.device)
        return s

    def _hebbian(self, session, event):
        """Write this visitor's relationship into the reward synapses:
        correlated pre/post activity potentiates, meanness erodes."""
        if event in KIND_EVENTS:
            X = self.brain.X
            session.plas_d += PLAS_ETA * X[self.dan_src] * X[self.dan_dst]
            session.plas_d = session.plas_d.clamp(-PLAS_CAP, PLAS_CAP)
        elif event in MEAN_EVENTS:
            session.plas_d *= 0.75

    def synapse_trust(self, session):
        return round(float((session.plas_d.mean() * 200).clamp(0, 1)), 3)

    def _log_event(self, session, event):
        """Record today's event with its acquisition-time neural read — the
        raw material the night pass selects its top decile from (Dag 2019:
        dopamine at encoding predicts what sleep reactivates)."""
        if not event:
            return
        pk = session.mood.last_peak or {}
        import time as _t
        session.day_log.append({
            "ev": event, "t": _t.time(),
            "dan": round(pk.get("dan", 0.0), 4),
            "kc": round(pk.get("kc", 0.0), 4),
            "dop": round(pk.get("dop", 0.0), 4),
            "sal": session.mood.salience,
        })
        session.day_log = session.day_log[-100:]

    def consolidate_night(self, session):
        """vFB-style sleep consolidation (L3; Dag 2019, Berry 2015).

        At deep night, once, the brain re-fires the day's top-decile
        salience events at dreamlike gain and writes the co-active DAN
        synapses deeper (eta 2x day), then applies ONE global dFB-style
        downscale — homeostatic, ranking-preserving. Forgetting stays
        arousal-gated: nothing erodes passively while she sleeps, and an
        aversive replay writes nothing (its waking response was erosion;
        asleep, there is no arousal to gate it, so it is dream content
        only). A day with salient events deepens tonight's sleep target.
        Returns the diary entry (or None)."""
        from mood import darkness_now
        import datetime as _dt
        s = session
        log = getattr(s, "day_log", None) or []
        today = _dt.date.today()
        # drop stale entries: replay is same-night only (their 7-10 h window)
        log = [e for e in log if _dt.datetime.fromtimestamp(e["t"]).date() == today]
        if (darkness_now() < 0.6 or s.mood.sleep <= 0.6
                or getattr(s, "night_stamp", None) == today or not log):
            s.day_log = log
            return None
        s.night_stamp = today
        # select the top decile by dopamine AT ACQUISITION, >=1, capped
        ranked = sorted(log, key=lambda e: -e["dop"])
        n = max(1, min(MAX_REPLAYS, int(len(ranked) * TOP_FRAC + 0.999)))
        chosen = ranked[:n]
        dreamed, written = [], []
        with self.session_turn(s):
            for e in chosen:
                ev = e["ev"]
                I = self.senses.input_for(ev) * DREAM_GAIN
                for _ in range(20):                    # re-fire, dreamlike
                    self.brain.step(I=I, gain=self.brain.op_gain)
                X = self.brain.X
                if ev in KIND_EVENTS:                  # reward co-fires ->
                    s.plas_d += NIGHT_ETA * X[self.dan_src] * X[self.dan_dst]
                    s.plas_d = s.plas_d.clamp(-NIGHT_CAP, NIGHT_CAP)
                    written.append(ev)
                dreamed.append(ev)                     # everything else: a dream
            s.plas_d *= NIGHT_DOWNSCALE                # dFB arm: one pass
        # learning-dependent sleep pressure (rule 5)
        s.mood.learn_pressure = min(0.2, 0.05 * len(chosen))
        s.day_log = []                                 # consumed, same-night
        s.dream_pool = list(dict.fromkeys(dreamed))    # L4: what tonight may
        s.dreams_tonight = 0                           # dream about, capped
        names = ", ".join(dict.fromkeys(dreamed))
        entry = (f"slept deep as the day played back -- {names}; "
                 "the good of it settled in for good")
        s.diary.append({"t": 0.5, "act": "consolidate", "text": entry})
        s.diary = s.diary[-50:]
        return entry

    def dream(self, session, rng):
        """Deep-night dream theater (L4). The events the consolidation pass
        replayed surface again through the small hours, recombined with a
        shuffled partner, as diary dreams. READ-ONLY by design: no synapse
        writes, no mood shift — asleep there is no arousal to gate a write
        (L3 rule 4), so a dream must never deepen or heal anything. Returns
        the dream text (or None)."""
        from mood import darkness_now
        s = session
        pool = getattr(s, "dream_pool", None) or []
        if (darkness_now() < 0.6 or s.mood.sleep <= 0.8 or not pool
                or getattr(s, "dreams_tonight", 0) >= MAX_DREAMS
                or rng.random() > DREAM_P):
            return None
        ev = rng.choice(pool)
        home = DREAM_PARTNER.get(ev)
        cast = [p for p in DREAM_PARTNERS if p != home] or list(DREAM_PARTNERS)
        text = DREAM_TPL.get(ev, DREAM_DEFAULT).format(p=rng.choice(cast))
        s.dreams_tonight = getattr(s, "dreams_tonight", 0) + 1
        s.diary.append({"t": rng.random(), "act": "dream", "text": text})
        s.diary = s.diary[-50:]
        return text

    def preamble_for(self, sit, mood, level, session):
        """One of her own lines to prime the context. Lane A finding
        (2026-11-08, ~/critters/peabrain-lab): priming her own conversational
        momentum beats priming the brain's mood — voice the preamble in the
        mood of her LAST REAL reply, falling back to the brain tag on turn 1.
        +3.0 pts family agreement, variety intact."""
        own = {"neutral", "happy", "curious", "sleepy", "hungry",
               "angry", "scared", "confused"}
        if session.last_reply_tag in own:
            mood, level = session.last_reply_tag, "low"
        sit = sit if sit in voice.SITUATIONS else "off_topic"
        line = voice.reply(sit, mood, level, {"name", "no", "peas", "hi"},
                           NAME, self.rng)
        return line

    @contextmanager
    def session_turn(self, session):
        """Swap this visitor's neural trajectory and synaptic state into the
        shared brain, advance idle time for their drives, and swap everything
        back out after."""
        if session.X is not None:
            self.brain.X.copy_(session.X)
        if session.plas_d is not None and float(session.plas_d.abs().sum()) > 0:
            self.brain.active_delta = (self.dan_src, self.dan_dst, session.plas_d)
        import time as _time
        now = _time.time()
        if session.last_seen is not None:
            idle = min(now - session.last_seen, 600.0)
            if idle > 1.0:
                session.mood.observe(idle)
        session.last_seen = now
        try:
            yield
        finally:
            session.X = self.brain.X.clone()
            self.brain.active_delta = None

    def world_tick(self, session, rng=None):
        """One beat of her solo life: drives speak, she acts on them herself.
        Hand policy for now (Layer 2 replaces it with DAN-critic learning).
        Self-care relieves the need; it never grants joy or trust — that is
        what visitors are for. Returns the diary entry (or None)."""
        import random as _r
        rng = rng or _r.Random()
        s = session
        self.consolidate_night(s)             # deep night writes the day in, once
        if self.dream(s, rng):                # ...and sometimes dreams it (L4)
            return "dream"
        with self.session_turn(s):
            a = s.mood.axes()
            parade = False
            s.curiosity *= 0.975               # tau ~30 min at the 45 s cadence
            if a["fear"] > 0.4:
                s.mood.fear *= 0.7
                entry = "hid behind the planter until the fright faded"
                act = "hide"
            elif a["sleep"] > 0.75:
                s.mood.food_joy = min(1.0, s.mood.food_joy + 0.05)
                entry = "curled up at the reeds and napped"
                act = "nest"
            elif a["hunger"] > 0.7:
                s.mood.hunger = max(0.0, s.mood.hunger - 0.25 - 0.1 * rng.random())
                s.mood.observe(5.0, event="water")     # dabbling, neurally
                self._log_event(s, "water")
                if rng.random() < 0.12:
                    entry = "dabbled at the pond -- found something SHINY"
                    s.shiny_found = True
                    s.hoard += 1               # L10: this one she keeps
                    parade = True
                    find = "shiny"
                else:
                    entry = "dabbled at the pond and found a slug"
                    find = "slug"
                # the pond gave her something interesting: it banks (L5)
                s.curiosity = min(1.0, s.curiosity + CURIOSITY_EVENT[find])
                act = "forage_pond"
            elif s.curiosity > CURIOSITY_GATE and rng.random() < INVESTIGATE_P:
                # drives are low here (fear/sleep/hunger branches all missed)
                # and something interesting is still on her mind
                tgt = rng.choice(("goats", "fence", "boot"))
                if tgt == "boot" and a["fear"] > 0.2:
                    tgt = "goats"             # a wary duck does not poke the boot
                intent, entry = INVESTIGATE[tgt]
                s.curiosity *= 0.5            # checked it out; satisfied for now
                s.curious_at = intent
                act = "investigate_" + tgt
            elif a["food_joy"] < 0.15 and rng.random() < 0.4:
                s.mood.food_joy = min(1.0, s.mood.food_joy + 0.10)
                entry = "splashed in the shallows for the fun of it"
                act = "dabble"
            else:
                entry = None
                act = "idle"
        if entry:
            s.diary.append({"t": _r.uniform(0, 1), "act": act, "text": entry})
            s.diary = s.diary[-50:]
        if getattr(s, "parade_ticks", 0) > 0:
            s.parade_ticks -= 1                 # the strut wears off on its own
        if parade:
            # L10: a new shiny deserves a lap of honor -- motion she earned,
            # rendered through the same intent channel, no joy/trust granted
            s.parade_ticks = 3
            s.diary.append({"t": _r.uniform(0, 1), "act": "parade",
                            "text": f"paraded the shiny past the goats "
                                    f"(hoard: {s.hoard})"})
            s.diary = s.diary[-50:]
        return act

    # ---- L7: locomotor readout from the descending population ----
    # DNs are the brain's motor port (Eon: DNa01/02 steer, oDN1 forward
    # velocity); CX normalizes rather than selects (Nanni&Lee 2607.18969),
    # so SELECTION stays at the drive ladder and this is a readout only.
    # Anchors measured on the live graph (lane/l7_preflight.out.txt):
    # spontaneous DN mean .0394, greet peak .0652, swat peak .0891; LA
    # sparkle (shiny) moves DN ~0 — broad visual input cannot fake a
    # locomotor command, the wiring gates for free. The sleep gate is
    # body-level (like the water-joy floor): a sleeping duck settles.
    CX_BASE, CX_SPAN = 0.035, 0.055

    def cx_intent(self, session):
        m = session.mood
        p = getattr(m, "last_peak", None) or {}
        fresh = bool(p) and (m.clock_s - p.get("at", -1e9)) < 30.0
        if fresh:                          # DN read AT the stimulus peak
            dn_mean, L, R = p["dn"], p["dn_l"], p["dn_r"]
        else:                              # ambient: her resting DN hum
            X = self.brain.X
            dn_mean = float(X[self.senses.dn["all"]].mean())
            L = float(X[self.senses.dn["left"]].mean())
            R = float(X[self.senses.dn["right"]].mean())
        gate = max(0.0, min(1.0, 1.0 - 1.2 * m.axes()["sleep"]))
        move = max(0.0, min(1.0, (dn_mean - self.CX_BASE) / self.CX_SPAN))
        turn = (R - L) / (R + L + 1e-6) * min(move, 1.0)
        return {"move": round(move * gate, 3),
                "turn": round(turn * gate, 3),
                "arousal": round(dn_mean, 4),
                "gate_sleep": round(gate, 3),
                "source": "dn_population_v1" + ("+peak" if fresh else "")}

    def needs(self, session):
        """Her current needs and mood, no conversation required (the poll).
        Also an ambient intent: where her body wants to be, from her drives —
        the client may move her ONLY when this or a reply intent says so."""
        with self.session_turn(session):
            mood, level = session.mood.mood_tag()
            a = session.mood.axes()
            if a["hunger"] > 0.75:
                # she asks, when she trusts you enough to beg
                ambient = "beg" if session.mood.trust > 0.30 else "to_bowl"
            elif a["sleep"] > 0.7:
                ambient = "settle"
            elif a["fear"] > 0.4:
                ambient = "to_boot"
            elif getattr(session, "parade_ticks", 0) > 0:
                ambient = "parade"              # L10: fresh shiny, must show off
            elif a["food_joy"] > 0.6:
                ambient = "to_pond"
            elif getattr(session, "curiosity", 0.0) > CURIOSITY_GATE \
                    and session.curious_at:
                ambient = session.curious_at   # unspent curiosity points her body
            else:
                ambient = "stay"
            return {"mood": f"{mood}:{level}", "axes": a,
                    "synapse": self.synapse_trust(session),
                    "trust": round(0.5 * session.mood.trust
                                   + 0.5 * self.synapse_trust(session), 3),
                    "intent": ambient,
                    "cx": self.cx_intent(session)}

    @torch.no_grad()
    def reply(self, text, session):
        with self.session_turn(session):
            return self._reply_inside(text, session)

    def _reply_inside(self, text, session):
        low = text.lower()
        # the bridge knows things the keyword router doesn't: an apology is an
        # apology even when it mentions the rake; night is night
        is_sorry = any(w in low for w in ("sorry", "my bad", "apolog", "forgive"))
        is_night = any(w in low for w in ("goodnight", "good night", "sleep well",
                                          "time for bed", "night night"))
        sit, _route_mood, _lvl = session.mind.react(text)
        if is_sorry:
            sit = "sorry"
        if is_night:
            sit = "night"
        event = SIT_TO_EVENT.get(sit)
        if sit == "sorry":                      # an apology actively soothes
            session.mood.trust = min(1.0, session.mood.trust + 0.10)
            session.mood.salience *= 0.4
            session.mood.fear *= 0.4
        if sit == "night":                      # the body knows bedtime
            session.mood.sleep = min(1.0, session.mood.sleep + 0.6)
        if sit == "eat_q":                      # interoception: thinking about
            session.mood.hunger = min(1.0, session.mood.hunger + 0.05)  # peas
        if sit == "empty_bowl":                 # and seeing the empty bowl
            session.mood.hunger = min(1.0, session.mood.hunger + 0.10)  # is worse
        session.mood.observe(2.0, event=event)
        self._hebbian(session, event)          # write this moment into synapses
        self._log_event(session, event)        # ...and remember it for tonight
        mood, level = session.mood.mood_tag()
        intent = INTENTS.get(sit, "stay")
        # begging: hungry enough + trusting enough + you didn't bring food
        # -> she comes to YOU and asks (solicited care beats self-care)
        if (intent in ("stay",) and event is None
                and session.mood.hunger > 0.75 and session.mood.trust > 0.30):
            intent = "beg"
        pre = self.preamble_for(sit, mood, level, session)

        memory = session.memory
        ids = [self.bos]
        # synthetic memory turn: a sense-style moment + her reaction in the
        # brain's mood (this is the mood-momentum lever)
        sense_txt = f"*{event}*" if event else "*a quiet moment*"
        ids += [self.user] + self.sp.encode(f"{CARD}: {sense_txt}") \
               + [self.bee] + self.sp.encode(pre) + [self.eos]
        for you, them in memory:
            ids += [self.user] + self.sp.encode(f"{CARD}: {you}") \
                   + [self.bee] + self.sp.encode(them) + [self.eos]
        ids += [self.user] + self.sp.encode(f"{CARD}: {text}") + [self.bee]

        out = self.llm.generate(
            torch.tensor([ids], device=self.brain.device), do_sample=True,
            temperature=0.8, top_k=40, top_p=0.95, max_new_tokens=64,
            eos_token_id=[self.eos, self.user, self.bee],
            pad_token_id=self.eos)
        new = [t for t in out[0, len(ids):].tolist()
               if t not in (self.eos, self.user, self.bee)]
        raw = self.sp.decode(new).split("\n")[0].strip()
        raw = mend_tag(raw)

        session.memory.append((text, raw))
        session.memory = session.memory[-7:]
        import re as _re
        _m = _re.match(r"\[([a-z]+):([a-z]+)\]", raw)
        session.last_reply_tag = _m.group(1) if _m else None

        gen_tag = raw[1:].split(":", 1)[0] if raw.startswith("[") else "?"
        self.agree[0] += int(gen_tag == mood)
        self.agree[1] += 1
        syn = self.synapse_trust(session)
        return {"brain_mood": f"{mood}:{level}", "axes": session.mood.axes(),
                "synapse": syn,
                "trust": round(0.5 * session.mood.trust + 0.5 * syn, 3),
                "intent": intent,
                "cx": self.cx_intent(session),
                "preamble": pre, "reply": raw,
                "agree": f"{self.agree[0]}/{self.agree[1]}"}

SCENARIO = [
    "hello Bill!",
    "*shakes the pea tin*",
    "here, peas for you",
    "careful -- there's a rake right there",
    "i'm sorry about the rake, sweet duck",
    "*gently strokes your back*",
    "goodnight Bill",
]

def demo():
    b = DuckBridge()
    session = b.open_session()
    print(f"\n=== a duck's afternoon (brain-driven) ===")
    for t in SCENARIO:
        r = b.reply(t, session)
        print(f"\n> {t}")
        print(f"  brain: {r['brain_mood']:13} axes {r['axes']}")
        print(f"  her:   {r['reply']}")
    print(f"\ntalking layer agreed with the brain on mood: {b.agree[0]}/{b.agree[1]}")

if __name__ == "__main__":
    demo()
