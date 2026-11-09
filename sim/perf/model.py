"""Straight-line and lap model of a 1/10-scale four-wheel-drive car with a brushless motor.

What is in it
    - tyre grip as one number mu, shared between cornering and accelerating or braking (friction circle)
    - the motor as Kv, a winding resistance and a current limit; the battery as a voltage behind a resistance with a
      current limit; the ESC's maximum duty cycle. Top speed comes out of these: back-EMF meets the sagging battery
    - gearing, tyre size, drivetrain efficiency, rolling resistance, aerodynamic drag from the CFD
    - braking through the motor, limited by grip, by the motor current and by what the battery may take back (regen)
What is not
    - weight transfer, suspension, tyre slip angles, tyre load sensitivity, slopes, wheelspin dynamics
    - how well a controller can follow the plan: this is what the hardware could do, not what the software does today
    - motor heating
"""
import math
import numpy as np
from params import G, RHO, SLASH, COMMON, val


class Car:
    def __init__(self, spec, mass_kg, pinion=None, spur=None, mu=None, v_cell=None, i_regen=None, i_motor=None,
                 i_batt=None, r_motor=None, r_supply=None, v_cap=None):
        g = val(spec['gearing'])
        self.name = spec['name']
        self.m = float(mass_kg)
        self.pinion = pinion or g[0]
        self.spur = spur or g[1]
        self.ratio = self.spur / self.pinion * val(SLASH['diff_ratio'])
        self.r = val(SLASH['tyre_d_m']) / 2.0
        self.kv = val(spec['kv_rpm_per_v'])
        self.kt = 60.0 / (2.0 * math.pi * self.kv)                 # N m per amp
        self.rpm_max = val(spec['motor_rpm_max'])
        self.pp = val(spec['pole_pairs'])
        self.rm = r_motor if r_motor is not None else val(spec['r_motor_ohm'])
        self.rs = r_supply if r_supply is not None else val(spec['r_supply_ohm'])
        self.voc = spec['cells'] * (v_cell if v_cell is not None else val(spec['v_cell_nominal']))
        self.im = i_motor if i_motor is not None else val(spec['i_motor_max'])
        self.ib = i_batt if i_batt is not None else val(spec['i_batt_max'])
        self.ireg = i_regen if i_regen is not None else val(spec['i_regen_max'])
        self.pmax = val(spec['p_mech_max_w']) if 'p_mech_max_w' in spec else None
        self.mu = mu if mu is not None else val(COMMON['mu'])
        self.eta = val(COMMON['drivetrain_eff'])
        self.crr = val(COMMON['crr'])
        self.duty = val(COMMON['duty_max'])
        self.cda = val(COMMON['cda_m2'])
        self.v_cap = v_cap                                         # speed limit set in the ESC (max ERPM), m/s

    # ------------------------------------------------------------------ helpers
    def motor_rpm(self, v):
        return v / (2.0 * math.pi * self.r) * 60.0 * self.ratio

    def erpm(self, v):
        return self.motor_rpm(v) * self.pp

    def resist(self, v):
        return 0.5 * RHO * self.cda * v * v + self.crr * self.m * G

    def grip(self):
        return self.mu * self.m * G

    def _feasible(self, i_m, e):
        """Can the supply deliver motor current i_m at back-EMF e? Returns (ok, battery current)."""
        p = (e + i_m * self.rm) * i_m                               # electrical power into the motor
        disc = self.voc * self.voc - 4.0 * self.rs * p              # V_bus = Voc - Ib Rs, Ib = p / V_bus
        if disc < 0:
            return False, None
        vbus = 0.5 * (self.voc + math.sqrt(disc))
        ib = p / vbus
        return (e + i_m * self.rm <= self.duty * vbus) and ib <= self.ib, ib

    def motor_current(self, v):
        if self.v_cap is not None and v >= self.v_cap:
            return 0.0
        rpm = self.motor_rpm(v)
        if rpm >= self.rpm_max:
            return 0.0
        e = rpm / self.kv
        lo, hi = 0.0, self.im
        if self._feasible(hi, e)[0]:
            return hi
        if not self._feasible(0.0, e)[0]:
            return 0.0
        for _ in range(40):
            mid = 0.5 * (lo + hi)
            if self._feasible(mid, e)[0]:
                lo = mid
            else:
                hi = mid
        return lo

    def drive_force(self, v):
        """Largest forward force at the tyres the power train can make at speed v (before the grip limit)."""
        f = self.kt * self.motor_current(v) * self.ratio * self.eta / self.r
        if self.pmax is not None and v > 0.1:
            f = min(f, self.pmax / v)
        return f

    def brake_force(self, v):
        """Largest braking force at the tyres from the motor (before the grip limit). Drag is added by the caller."""
        f_im = self.kt * self.im * self.ratio / (self.eta * self.r)      # motor current limit
        if v < 0.3:
            return f_im
        def regen_ok(f):
            i_m = f * self.eta * self.r / (self.kt * self.ratio)
            p_el = self.eta * f * v - i_m * i_m * self.rm               # electrical power sent back
            return p_el <= self.ireg * self.voc
        if regen_ok(f_im):
            return f_im
        lo, hi = 0.0, f_im
        for _ in range(40):
            mid = 0.5 * (lo + hi)
            if regen_ok(mid):
                lo = mid
            else:
                hi = mid
        return lo

    def accel(self, v, a_lat=0.0):
        cap = self.mu * G
        room = math.sqrt(max(0.0, 1.0 - (a_lat / cap) ** 2)) if cap > 0 else 0.0
        f = min(self.drive_force(v), self.grip() * room)
        return (f - self.resist(v)) / self.m

    def decel(self, v, a_lat=0.0):
        cap = self.mu * G
        room = math.sqrt(max(0.0, 1.0 - (a_lat / cap) ** 2)) if cap > 0 else 0.0
        f = min(self.brake_force(v), self.grip() * room)
        return (f + self.resist(v)) / self.m

    def top_speed(self):
        """Steady speed on an endless straight: where the drive force falls to the resistance."""
        lo, hi = 0.5, 60.0
        if self.accel(lo) <= 0:
            return 0.0
        for _ in range(60):
            mid = 0.5 * (lo + hi)
            if self.accel(mid) > 0:
                lo = mid
            else:
                hi = mid
        return lo


def straight(car, length, v_in, v_out=None, ds=0.02):
    """Speed along a straight of the given length: enter at v_in, be down to v_out at the end. Returns (s, v)."""
    v_out = v_in if v_out is None else v_out
    n = int(round(length / ds)) + 1
    s = np.linspace(0.0, length, n)
    up = np.empty(n); dn = np.empty(n)
    up[0] = v_in
    for i in range(n - 1):
        up[i + 1] = math.sqrt(max(0.0, up[i] ** 2 + 2.0 * car.accel(up[i]) * ds))
    dn[-1] = v_out
    for i in range(n - 1, 0, -1):
        dn[i - 1] = math.sqrt(dn[i] ** 2 + 2.0 * car.decel(dn[i]) * ds)
    return s, np.minimum(up, dn)


def load_track(path, ds=0.10):
    """A closed centre line from a CSV of x, y in metres. Returns arc length, curvature and the total length."""
    from scipy.interpolate import CubicSpline
    xy = np.loadtxt(path, delimiter=',', skiprows=1)
    if np.hypot(*(xy[0] - xy[-1])) > 1e-6:
        xy = np.vstack([xy, xy[0]])
    d = np.hypot(np.diff(xy[:, 0]), np.diff(xy[:, 1]))
    t = np.concatenate([[0.0], np.cumsum(d)])
    cx = CubicSpline(t, xy[:, 0], bc_type='periodic'); cy = CubicSpline(t, xy[:, 1], bc_type='periodic')
    s = np.arange(0.0, t[-1], ds)
    dx, dy, ddx, ddy = cx(s, 1), cy(s, 1), cx(s, 2), cy(s, 2)
    kappa = (dx * ddy - dy * ddx) / np.power(dx * dx + dy * dy, 1.5)
    return s, kappa, float(t[-1])


def rounded_box(straight_x, straight_y, radius, ds=0.10):
    """A synthetic closed track: a rectangle with round corners. Returns arc length, curvature, total length."""
    seg = [(straight_x, 0.0), (0.5 * math.pi * radius, 1.0 / radius), (straight_y, 0.0), (0.5 * math.pi * radius, 1.0 / radius)] * 2
    total = sum(l for l, _ in seg)
    s = np.arange(0.0, total, ds)
    kappa = np.zeros_like(s)
    edges = np.cumsum([0.0] + [l for l, _ in seg])
    for (a, b), (_, k) in zip(zip(edges[:-1], edges[1:]), seg):
        kappa[(s >= a) & (s < b)] = k
    return s, kappa, total


def lap(car, s, kappa, total, v_ceiling=None):
    """Quasi-steady lap: corner speed from grip, then a forward pass (drive) and a backward pass (brake)."""
    n = len(s)
    ds = total / n
    k = np.abs(kappa)
    cap = car.mu * G
    v_c = np.sqrt(cap / np.maximum(k, 1e-6))
    ceiling = min(x for x in (v_ceiling, car.v_cap, 60.0) if x is not None)
    v = np.minimum(v_c, ceiling)
    for _ in range(3):                                   # go round a few times so the start point does not matter
        for i in range(n):
            j = (i + 1) % n
            a = car.accel(v[i], v[i] * v[i] * k[i])
            v[j] = min(v[j], math.sqrt(max(0.0, v[i] ** 2 + 2.0 * a * ds)))
        for i in range(n - 1, -1, -1):
            j = (i + 1) % n
            a = car.decel(v[j], v[j] * v[j] * k[j])
            v[i] = min(v[i], math.sqrt(v[j] ** 2 + 2.0 * a * ds))
    t = float(np.sum(ds / np.maximum(0.5 * (v + np.roll(v, -1)), 0.05)))
    return dict(lap_s=round(t, 2), v_max=round(float(v.max()), 2), v_mean=round(total / t, 2),
                v_min=round(float(v.min()), 2), length_m=round(total, 1)), v
