"""Turn sim/aero/out/results.json into the tables docs/AERO.md quotes: forces at 2, 5 and 8 m/s, the wing's
effect, a flat-plate hand estimate to judge the CFD against, and the cooling-air numbers.

    python3 sim/aero/summarize.py        # writes sim/aero/out/summary.json and summary.md, and wing_sweep.png
"""
import json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'out')
sys.path.insert(0, os.path.join(HERE, '..', '..', 'mech'))

RHO, NU, G = 1.2, 1.5e-5, 9.81
V_CFD = 8.0
SPEEDS = (2.0, 5.0, 8.0)                 # today's speed cap, a fast lap, the CFD speed
MASS_RANGE_KG = (3.0, 4.0)               # NOT weighed. A bracket for "how big is this against the car's weight"
HEAT_W = dict(jetson=25.0, esc_and_board=10.0)     # Jetson: its 25 W mode. The rest: a round allowance, not measured
DT_AIR_K = 10.0                          # air temperature rise allowed through the electronics bay
CP_AIR = 1005.0

res = json.load(open(os.path.join(OUT, 'results.json')))
geom = json.load(open(os.path.join(OUT, 'geom', 'geometry.json')))
vent = json.load(open(os.path.join(OUT, 'vent_pressure.json')))
order = [('nowing', None), ('wing_0', 0), ('wing_m12', 12), ('wing_m20', 20)]

rows = []
base = res['nowing@8']['total']
for name, ang in order:
    r = res[f'{name}@8']
    w = r.get('wing') or {}
    rows.append(dict(case=name, wing_angle_deg=ang, cells=r['cells'],
                     drag_N=r['total']['drag_N'], lift_N=r['total']['lift_N'],
                     wing_drag_N=w.get('drag_N'), wing_downforce_N=(-w['lift_N'] if w else None),
                     d_drag_N=round(r['total']['drag_N'] - base['drag_N'], 4),
                     d_downforce_N=round(base['lift_N'] - r['total']['lift_N'], 4),
                     sd_drag_N=r['body']['sd_drag_N'], sd_lift_N=r['body']['sd_lift_N'],
                     Cd=r['total']['Cd'], CdA_m2=r['total']['CdA_m2']))

scale = {v: (v / V_CFD) ** 2 for v in SPEEDS}
weight = [m * G for m in MASS_RANGE_KG]
by_speed = []
for v in SPEEDS:
    s = scale[v]
    best = rows[-1]
    by_speed.append(dict(speed_mps=v, q_Pa=round(0.5 * RHO * v * v, 2),
                         reynolds_length=round(v * geom['length_m'] / NU, -3),
                         drag_no_wing_N=round(base['drag_N'] * s, 3), drag_power_W=round(base['drag_N'] * s * v, 2),
                         lift_no_wing_N=round(base['lift_N'] * s, 3),
                         lift_pct_of_weight=[round(100 * base['lift_N'] * s / w, 2) for w in weight],
                         wing20_extra_downforce_N=round(best['d_downforce_N'] * s, 4),
                         wing20_pct_of_weight=[round(100 * best['d_downforce_N'] * s / w, 3) for w in weight]))

# Hand estimate for the blade alone in clean air (no car in front of it): finite-wing lift slope, flat plate.
AR = geom['wing']['span_m'] / geom['wing']['chord_m']
hand = []
for ang in (12, 20):
    cl = min(2 * math.pi * math.radians(ang) / (1 + 2 / AR), 0.9)      # a flat plate stalls: cap at about 0.9
    hand.append(dict(angle_deg=ang, CL=round(cl, 2),
                     downforce_N_at_8=round(0.5 * RHO * V_CFD ** 2 * geom['wing']['area_m2'] * cl, 3)))
# speed at which the wing's whole effect reaches 5 % of the car's weight
target = [0.05 * w for w in weight]
v5_cfd = [round(V_CFD * math.sqrt(t / rows[-1]['d_downforce_N']), 0) for t in target]
v5_hand = [round(V_CFD * math.sqrt(t / hand[0]['downforce_N_at_8']), 0) for t in target]

# Cooling air
import kit
slot_mm2 = 12.0 * (kit.POD['h'] - 20 - 10)
x0 = kit.POD['x0']
outer_w = [(xc - w / 2, xc + w / 2) for (_, xc, w, _, _, wl) in kit.pod_windows() if wl in ('both', 'outer')]
n_left = 7
n_right = sum(1 for i in range(7) if not any(a < x0 + 30 + i * 22 + 12 and x0 + 30 + i * 22 < b for (a, b) in outer_w))
vent_cm2 = (n_left + n_right) * slot_mm2 / 100.0
heat = sum(HEAT_W.values())
q_air = heat / (RHO * CP_AIR * DT_AIR_K)                     # m3/s
cp_front = vent['regions']['front_faces_above_deck']['cp']
cp_side = (vent['regions']['pod_outer_left']['cp'] + vent['regions']['pod_outer_right']['cp']) / 2
cool = dict(heat_W=HEAT_W, heat_total_W=heat, air_rise_K=DT_AIR_K,
            air_needed_L_per_s=round(q_air * 1000, 2), air_needed_cfm=round(q_air * 2118.88, 1),
            pod_slots=dict(left=n_left, right=n_right, each_mm2=slot_mm2, total_cm2=round(vent_cm2, 1)),
            slot_velocity_mps=round(q_air / (vent_cm2 / 1e4), 2),
            cp_front=cp_front, cp_pod_sides=round(cp_side, 3), cp_top=vent['regions']['top_faces_above_deck']['cp'],
            cp_rear=vent['regions']['rear_faces_above_deck']['cp'],
            front_to_side_pressure_Pa={str(v): round((cp_front - cp_side) * 0.5 * RHO * v * v, 1) for v in SPEEDS},
            side_suction_Pa={str(v): round(-cp_side * 0.5 * RHO * v * v, 1) for v in SPEEDS})

summary = dict(speed_cfd_mps=V_CFD, frontal_area_m2=geom['frontal_area_m2'], wing=geom['wing'], aspect_ratio=round(AR, 2),
               blockage_pct=round(100 * geom['frontal_area_m2']['no_wing'] / (1.2 * 0.7), 1),
               cases=rows, by_speed=by_speed, mass_range_kg=MASS_RANGE_KG, hand_estimate_clean_air=hand,
               speed_for_5pct_of_weight_mps=dict(cfd=v5_cfd, clean_air_hand=v5_hand), cooling=cool)
json.dump(summary, open(os.path.join(OUT, 'summary.json'), 'w'), indent=1)

L = []
A = L.append
A('| case | cells | drag N | lift N (+ is up) | drag change N | downforce gained N | on the wing alone: drag N, downforce N |')
A('| --- | ---: | ---: | ---: | ---: | ---: | --- |')
names = {'nowing': 'no wing', 'wing_0': 'wing flat (0 deg)', 'wing_m12': 'wing nose down 12 deg', 'wing_m20': 'wing nose down 20 deg'}
for r in rows:
    wtxt = '-' if r['wing_drag_N'] is None else f"{r['wing_drag_N']:.3f}, {r['wing_downforce_N']:.3f}"
    A(f"| {names[r['case']]} | {r['cells']:,} | {r['drag_N']:.2f} | {r['lift_N']:+.2f} | {r['d_drag_N']:+.3f} | {r['d_downforce_N']:+.3f} | {wtxt} |")
A('')
A('| speed | drag, no wing | power to push the air | lift, no wing | lift as a share of the weight | what the 20 deg wing adds |')
A('| --- | ---: | ---: | ---: | --- | --- |')
for b in by_speed:
    A(f"| {b['speed_mps']:.0f} m/s | {b['drag_no_wing_N']:.2f} N | {b['drag_power_W']:.1f} W | {b['lift_no_wing_N']:+.3f} N | "
      f"{b['lift_pct_of_weight'][1]:.2f} to {b['lift_pct_of_weight'][0]:.2f} % | {b['wing20_extra_downforce_N']:.3f} N "
      f"({b['wing20_pct_of_weight'][1]:.2f} to {b['wing20_pct_of_weight'][0]:.2f} %) |")
open(os.path.join(OUT, 'summary.md'), 'w').write('\n'.join(L) + '\n')
print('\n'.join(L))
print(json.dumps(dict(hand=hand, v5=summary['speed_for_5pct_of_weight_mps'], cooling=cool, blockage=summary['blockage_pct'],
                      AR=summary['aspect_ratio']), indent=1))

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    ang = [r['wing_angle_deg'] for r in rows[1:]]
    fig, ax = plt.subplots(figsize=(6.4, 3.6), dpi=150)
    ax.plot(ang, [r['d_downforce_N'] for r in rows[1:]], 'o-', color='#1f5fa8', label='downforce gained, whole car (CFD)')
    ax.plot(ang, [r['wing_downforce_N'] for r in rows[1:]], 's--', color='#1f5fa8', alpha=0.6, label='downforce on the blade alone (CFD)')
    ax.plot(ang, [r['d_drag_N'] for r in rows[1:]], '^-', color='#b5482a', label='drag added, whole car (CFD)')
    ax.plot([h['angle_deg'] for h in hand], [h['downforce_N_at_8'] for h in hand], 'x:', color='#555555',
            label='blade alone in clean air (hand estimate)')
    ax.set_xlabel('wing angle, degrees nose down'); ax.set_ylabel('force at 8 m/s, N')
    ax.set_title('Rear wing at 8 m/s: car weight is about 29 to 39 N', fontsize=10)
    ax.set_xticks(ang); ax.grid(alpha=0.3); ax.legend(fontsize=7, frameon=False)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, 'wing_sweep.png'))
    print('wrote wing_sweep.png')
except Exception as e:
    print('no plot:', e)
