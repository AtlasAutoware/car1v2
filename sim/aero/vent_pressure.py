"""Surface pressure where the car breathes: the side pods' outer walls (the vent slots are in them), the front
of the body under the camera, the canopy's top and the rear face. From the no-wing CFD case.

    python3 sim/aero/vent_pressure.py            # writes sim/aero/out/vent_pressure.json

The CFD body is closed (no slots, no flow through the car), so this says which way the outside air would push
through an opening at each place and how hard, not how much air flows.
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'mech'))
import foam_forces

U = 8.0
geom = json.load(open(os.path.join(HERE, 'out', 'geom', 'geometry.json')))
zg = -geom['z_ground_mm_in_kit_frame'] / 1000.0          # kit z = 0 (deck top) in the CFD frame, m
import kit
P = kit.POD
x0, x1, yo, h = P['x0'] / 1000, P['x1'] / 1000, P['y_out'] / 1000, P['h'] / 1000
(bx0, by0, bz0), (bx1, by1, bz1) = geom['body']['bounds_m']
regions = {
    'pod_outer_left': dict(box=((x0, yo - 0.004, zg + 0.008), (x1, yo + 0.004, zg + h - 0.018)), axis=1, sign=+1),
    'pod_outer_right': dict(box=((x0, -yo - 0.004, zg + 0.008), (x1, -yo + 0.004, zg + h - 0.018)), axis=1, sign=-1),
    'front_faces_above_deck': dict(box=((0.10, -0.10, zg), (bx1 + 0.01, 0.10, bz1 + 0.01)), axis=0, sign=+1),
    'rear_faces_above_deck': dict(box=((bx0 - 0.01, -0.10, zg), (-0.05, 0.10, bz1 + 0.01)), axis=0, sign=-1),
    'top_faces_above_deck': dict(box=((-0.12, -0.08, zg + 0.06), (0.12, 0.08, bz1 + 0.01)), axis=2, sign=+1),
}
case = os.path.join(HERE, 'out', 'cases', 'nowing')
res = foam_forces.region_cp(case, U, regions)
q = {v: round(0.5 * 1.2 * v * v, 2) for v in (2.0, 5.0, 8.0)}
out = dict(case='nowing', speed_mps=U, deck_top_z_m=round(zg, 4), dynamic_pressure_Pa=q, regions=res)
json.dump(out, open(os.path.join(HERE, 'out', 'vent_pressure.json'), 'w'), indent=1)
print(json.dumps(out, indent=1))
