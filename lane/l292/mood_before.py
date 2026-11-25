"""
peabrain — moods that linger.

Fast neural transients (seconds) become slow mood axes (a minute+) via
exponential integrators with axis-specific time constants. Homeostatic drives
(hunger, sleep pressure) live here too: they rise on their own clocks and
fall on real events. Trust is asymmetric, like in ducks and people: it builds
slowly with kindness and drops fast with meanness.

    fear      <- LC4/16 looming activity + octopamine     (tau ~45 s)
    food_joy  <- serotonin + DAN slow component           (tau ~90 s)
    trust     <- kindness up (slow), meanness down (fast) (asymmetric)
    salience  <- dopamine                                  (tau ~15 s)
    hunger    <- homeostat, rises ~4%/min, eats when peas arrive
    sleep     <- homeostat, rises all day, dips on novelty

The duck's eight moods (her talking layer's vocabulary) are a readout of
these axes, not a state machine.
"""
import datetime
import math
import os

import torch

AXIS_TAU = {"fear": 45.0, "food_joy": 90.0, "salience": 15.0}

def darkness_now():
    """0 at high noon, 1 in the dead of night (smooth shoulders at dusk/dawn)."""
    forced = os.environ.get("PEBRAIN_FORCE_HOUR")
    hour = float(forced) if forced is not None else \
        datetime.datetime.now().hour + datetime.datetime.now().minute / 60.0
    # sun factor: 1 at noon, 0 at midnight; widen the dark band for duck hours
    day = 0.5 + 0.5 * math.cos((hour - 12.0) / 12.0 * math.pi)
    day = min(1.0, max(0.0, (day - 0.15) / 0.7))
    return 1.0 - day


class MoodState:
    def __init__(self, senses):
        self.s = senses
        self.fear = 0.0
        self.food_joy = 0.0
        self.trust = 0.3          # wary-neutral start, like the rules duck
        self.salience = 0.0
        self.hunger = 0.35
        self.sleep = 0.1
        self.clock_s = 0.0
        self.last_peas_s = -600.0
        self.last_peak = None      # neural peak of the last event (see observe)
        self.learn_pressure = 0.0  # learning-dependent sleep drive (Dag 2019)

    def observe(self, seconds, event=None):
        """Advance the brain `seconds` of sim time with an optional stimulus.
        Mood axes PEAK-HOLD: they jump to what the neurons measured at the
        stimulus and then decay on their own slow clocks (a scared duck stays
        scared for a while; that is the point of a mood)."""
        b = self.s.brain
        gain = getattr(b, "op_gain", None) or (0.95 / b.rho)
        I_event = self.s.input_for(event) if event else None
        # the sun drives her clock circuit — but it is body-state, not news:
        # the circadian tonic NEVER counts toward the event peak readout
        # (else darkness leaks into dopamine and reads as salience)
        dark = darkness_now()
        I_circ = None
        if dark > 0.05:
            I_circ = torch.zeros(b.N, device=b.device)
            I_circ[self.s.probes["CX"]] = 0.30 * dark
        steps = int(seconds / 0.01)
        stim_steps = min(steps, 20) if I_event is not None else 0

        peak = {}
        if I_event is not None:
            combined = I_event if I_circ is None else I_event + I_circ
            for _ in range(stim_steps):
                b.step(I=combined, gain=gain)
            # read the neural state right at the stimulus
            X = b.X
            peak = {
                "lc": X[self.s.probes["LC"]].mean().item(),
                "dan": X[self.s.probes["DAN"]].mean().item(),
                "kc": X[self.s.probes["KC"]].mean().item(),
                "oct": b.X[b.mod_idx["octopamine"]].mean().item(),
                "ser": b.X[b.mod_idx["serotonin"]].mean().item(),
                "dop": b.X[b.mod_idx["dopamine"]].mean().item(),
                # L7: the motor port at the same instant — DN transients die
                # before post-decay readouts, so locomotion is read at the
                # stimulus like every other fast population
                "dn": X[self.s.dn["all"]].mean().item(),
                "dn_l": X[self.s.dn["left"]].mean().item(),
                "dn_r": X[self.s.dn["right"]].mean().item(),
                "at": self.clock_s + 0.2,
            }
        self.last_peak = peak or None   # acquisition-time read for the night
        for _ in range(steps - stim_steps):
            b.step(I=I_circ, gain=gain)
        self.clock_s += seconds

        def hold(cur, target, tau, dt):
            """peak-hold: decay on the slow clock, but never below the target."""
            decayed = cur * __import__("math").exp(-dt / tau)
            return max(decayed, min(target, 1.0))

        t_fear = 0.0
        t_joy = 0.0
        t_sal = 0.0
        if peak:
            # looming-gated fear readout (Lane A finding: lamina sparkle leaks
            # into LC and read as fear of a GIFT — the bridge knows which
            # channel fired, so LC only counts toward fear on looming events).
            # Octopamine is arousal, not fear: it amplifies but cannot alone
            # cross the fear threshold (a gift excites her; it does not
            # frighten her).
            lc = peak["lc"] if event in ("rake", "umbrella") else 0.05
            t_fear = max(0.0, lc - 0.05) * 1.2 + max(0.0, peak["oct"] - 0.06) * 1.5
            t_joy = max(0.0, peak["ser"] - 0.04) * 2.5 + max(0.0, peak["dan"] - 0.07) * 2.0
            t_sal = max(0.0, peak["dop"] - 0.05) * 4.0
        # body semantics: some loves live in the body, not the circuits
        if event == "water":
            t_joy = max(t_joy, 0.35)           # rain and pools, always
        elif event == "shiny":
            t_joy = max(t_joy, 0.15)
            t_sal = max(t_sal, 0.25)
        elif event == "hold":
            t_fear = max(t_fear, 0.30)         # lifted off the ground:
                                               # uncomfortable, not terrified
        self.fear = hold(self.fear, t_fear, AXIS_TAU["fear"], seconds)
        self.food_joy = hold(self.food_joy, t_joy, AXIS_TAU["food_joy"], seconds)
        self.salience = hold(self.salience, t_sal, AXIS_TAU["salience"], seconds)

        # drives
        self.hunger = min(1.0, self.hunger + 0.0007 * seconds)      # ~4%/min
        # circadian sleep: relax toward what sun + calendar + awake-time say
        # (tau ~20 min of sim time; CX is already carrying the night drive)
        night_target = 0.12 + 0.70 * dark
        awake_pressure = min(0.18, 0.18 * (1 - math.exp(-self.clock_s / 5400.0)))
        # learning-dependent sleep pressure (Dag 2019): a day with salient
        # events deepens the following night's sleep, capped at +0.2
        sleep_target = min(1.0, night_target + awake_pressure + self.learn_pressure)
        k = 1.0 - math.exp(-seconds / 1200.0)
        self.sleep = self.sleep + k * (sleep_target - self.sleep)
        # novelty wakes her, but can only shave a little per window — it is a
        # nudge, not an insomnia engine (owner of this bug: 600s windows used
        # to erase up to 4.0 sleep through this term)
        self.sleep = max(0.0, self.sleep - min(0.10, 0.4 * self.salience * seconds / 60.0))

        # trust: asymmetric, event-driven
        if event in ("pet", "greet", "goats"):
            self.trust = min(1.0, self.trust + 0.04)
        elif event in ("peas", "slug"):
            self.trust = min(1.0, self.trust + 0.07)
            self.last_peas_s = self.clock_s
            self.hunger = max(0.0, self.hunger - 0.5)   # eating, not hearing
        elif event == "tin":
            self.trust = min(1.0, self.trust + 0.07)    # anticipation only
        elif event == "water":
            self.trust = min(1.0, self.trust + 0.03)    # splash joy
        elif event == "shiny":
            self.trust = min(1.0, self.trust + 0.05)    # a gift remembered
        elif event in ("swat", "hose"):
            self.trust = max(0.0, self.trust - 0.20)
        elif event == "hold":
            self.trust = max(0.0, self.trust - 0.03)   # unsettling, not unkind
        elif event == "rake":
            self.trust = max(0.0, self.trust - 0.02)
        elif event == "umbrella":
            self.trust = max(0.0, self.trust - 0.01)
        return self.axes()

    def axes(self):
        return {"fear": round(self.fear, 3), "food_joy": round(self.food_joy, 3),
                "trust": round(self.trust, 3), "salience": round(self.salience, 3),
                "hunger": round(self.hunger, 3), "sleep": round(self.sleep, 3)}

    def mood_tag(self):
        """Map the axes onto the duck's trained mood vocabulary."""
        if self.fear > 0.25:
            return ("scared", "high" if self.fear > 0.5 else "low")
        if self.trust < 0.15 and self.salience > 0.3:
            return ("angry", "high")
        if self.trust < 0.2 and self.fear > 0.08:
            return ("angry", "low")
        if self.hunger > 0.75:
            return ("hungry", "high" if self.hunger > 0.9 else "low")
        if self.food_joy > 0.35:
            return ("happy", "high" if self.food_joy > 0.6 else "low")
        if self.sleep > 0.75:
            return ("sleepy", "low")
        if self.trust > 0.55:
            return ("happy", "low")
        if self.salience > 0.15:
            return ("curious", "low")
        return ("neutral", "low")

if __name__ == "__main__":
    from brain import FlyBrain
    from senses import DuckSenses
    b = FlyBrain()
    b.op_gain = 0.95 / b.rho
    s = DuckSenses(b)
    m = MoodState(s)
    m.observe(30.0)                       # 30 s of calm
    print("calm      ", m.axes(), m.mood_tag())
    m.observe(2.0, event="rake")
    print("RAKE      ", m.axes(), m.mood_tag())
    m.observe(20.0)
    print("+20s      ", m.axes(), m.mood_tag())
    m.observe(40.0)
    print("+60s      ", m.axes(), m.mood_tag())
    m.observe(2.0, event="peas")
    print("PEAS      ", m.axes(), m.mood_tag())
    m.observe(20.0)
    print("+20s      ", m.axes(), m.mood_tag())
    m.observe(2.0, event="swat")
    print("SWAT      ", m.axes(), m.mood_tag())
    m.observe(10.0)
    print("+10s      ", m.axes(), m.mood_tag())
