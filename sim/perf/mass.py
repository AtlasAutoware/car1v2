"""Mass budget of car 1 v2, stage 1. Bottom-up, every line with its basis.

    python3 sim/perf/mass.py        # prints the table and writes sim/perf/out/mass.json

The car has not been weighed (checklist B10). 'page' lines were read on a maker's or seller's page, 'cad' lines come
from the solid volume of the printed parts, 'est' lines are estimates. Each estimated line is taken as good to 25 % (printed parts 15 %, the chassis 10 %); the
low and high totals are twice the root-sum-square of those.
"""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
PETGCF_FILL = 0.80          # printed mass over solid mass: decks are nearly solid, pods and mounts are not (est)

PRINTED_KIT = ['deck_rear', 'deck_mid', 'deck_front', 'splice_rear_right', 'splice_rear_left', 'splice_front_right',
               'splice_front_left', 'bumper', 'camera_arch', 'side_pod_left', 'side_pod_right', 'devkit_tray',
               'canopy_leg', 'stack_canopy', 'esc_cradle']
PRINTED_C1V2 = ['c1_plinth', 'oakd_cradle', 'estop_bracket', 'bms_fence_jk']


def printed_solid_g():
    kit = json.load(open(os.path.join(ROOT, 'mech', 'out', 'kit_report.json')))['parts']
    kit.update(json.load(open(os.path.join(ROOT, 'mech', 'out', 'extras_report.json')))['parts'])     # the canopy
    c1 = json.load(open(os.path.join(ROOT, 'mech', 'out', 'car1v2', 'car1v2_report.json')))['parts']
    g = sum(kit[n]['mass_g_solid_petgcf'] for n in PRINTED_KIT) + sum(c1[n]['mass_g_solid_petgcf'] for n in PRINTED_C1V2)
    return float(g)


def items():
    solid = printed_solid_g()
    return [
        # what, grams, basis, note
        ('Slash 4x4 rolling chassis: tub, drivetrain, suspension, wheels and tyres', 2000, 'est',
         'Traxxas gives 2,640 g ready to run (page). Less the Velineon motor 262 g and VXL-3s 90 g (page), and about '
         '290 g for the body, servo and receiver (est)'),
        ('Holmes Puller Pro 540 motor with wires', 210, 'page', 'Holmes Hobbies: 210 g'),
        ('Flipsky FSESC with leads', 110, 'est', 'which of the two units is the spare is not known (checklist A3)'),
        ('INJORA INJS235 servo and horn', 80, 'est', ''),
        ('Jetson Orin Nano dev kit with heat sink, fan and NVMe', 190, 'est', ''),
        ('Power board, populated, with Pico, hub, FET bar and shield', 150, 'est', 'bare board about 32 g by its size'),
        ('4S LiPo pack', 520, 'est', 'a 5000 mAh hard-case pack is about this. The team\'s packs are not recorded (checklist A1)'),
        ('JK-B1A8S10P BMS with leads', 300, 'est', 'the listing size is 151 x 105 x 15.5 mm; its mass was not read (checklist B4)'),
        ('Hobbywing UBEC 10A', 40, 'est', ''),
        ('MIDI fuse and holder, XT90-S, 10 AWG leads, harnesses, USB leads', 260, 'est', ''),
        ('RPLidar C1 with its USB adapter', 125, 'est', 'Slamtec\'s figure for the lidar was not re-read today'),
        ('OAK-D Pro', 95, 'est', 'the mount check in mech/car1v2.py uses 100 g'),
        ('Printed parts (PETG-CF)', round(solid * PETGCF_FILL), 'cad',
         f'{solid:.0f} g if every part were solid (mech/out reports), times {PETGCF_FILL} for infill'),
        ('Standoffs, screws, inserts, E-stop button, fan, Wi-Fi adapter, joystick receiver', 190, 'est', ''),
    ]


UNCERTAINTY = {'page': 0.0, 'cad': 0.15, 'est': 0.25}       # fraction of each line; the chassis line is 0.10 (it starts from a page figure)


def budget():
    it = items()
    total = sum(g for _, g, _, _ in it)
    soft = sum(g for _, g, b, _ in it if b != 'page')
    sig = [(0.10 if w.startswith('Slash') else UNCERTAINTY[b]) * g for w, g, b, _ in it]
    spread = 2.0 * sum(x * x for x in sig) ** 0.5            # twice the root-sum-square of the per-line uncertainties
    lo, hi = total - spread, total + spread
    return dict(items=[dict(what=w, grams=g, basis=b, note=n) for w, g, b, n in it],
                total_kg=round(total / 1000, 2), low_kg=round(lo / 1000, 2), high_kg=round(hi / 1000, 2),
                read_on_a_page_g=total - soft, estimated_g=soft, printed_solid_g=printed_solid_g())


if __name__ == '__main__':
    b = budget()
    os.makedirs(os.path.join(HERE, 'out'), exist_ok=True)
    json.dump(b, open(os.path.join(HERE, 'out', 'mass.json'), 'w'), indent=1)
    for i in b['items']:
        print(f"{i['grams']:6d} g  {i['basis']:4s}  {i['what']}")
    print(f"total {b['total_kg']} kg (range {b['low_kg']} to {b['high_kg']}); {b['read_on_a_page_g']} g of it read on a page")
