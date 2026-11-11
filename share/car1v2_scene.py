"""Whole-car scene of car 1 v2 (stage 1) for the renders.

    python3 share/car1v2_scene.py                 writes share/scene_car1v2/*.stl and scene.json (about 1 minute)
    python3 share/render_car.py -- --scene scene_car1v2 --prefix car1v2_ car_front_left car_rear_right car_side car_top car_exploded

Built from the same models as mech/car1v2_assembly.py: the printed kit (mech/kit.py), the canopy (mech/extras.py)
and the car 1 v2 mounts (mech/car1v2.py). The chassis is the stand-in drawn in share/car_scene.py. The power board
is its KiCad 3D model (boards/power/out/render/atlas_power.glb, from `boards/tools/run_kicad.sh "" glb-power`);
without that file the kit's plain board outline stands in. On the team laptop that export carries the board, its
copper and its silkscreen but no components (kicad-cli did not find the footprints' 3D models), so the board is
bare in these pictures apart from the FET heatsink bar. boards/power/out/render/power_iso.png shows it populated.

Stand-ins, NOT models of the real parts: the Slash 4x4 chassis, the RPLidar C1 (its 55.6 x 55.6 x 41.3 mm
envelope), the OAK-D Pro (97 x 29.5 x 22.9 mm), the Jetson dev kit with its heatsink and fan, the FSESC case and
the fan. Lens positions, fins and blades are drawn to look right, not measured.

Not in the scene, as in the assembly, because nobody has measured where they go yet: the LiPo pack, the JK BMS,
the fuse, the XT90-S, the UBEC and every cable. The E-stop bracket's place is the builders' choice.
"""
import json
import math
import os
import sys

import cadquery as cq

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, 'mech'))
sys.path.insert(0, HERE)
import kit  # noqa: E402
import extras  # noqa: E402
import car1v2  # noqa: E402
import car_scene as cs  # noqa: E402  (the chassis stand-in and the small helpers)
from kit import P, box, cylz, cyl  # noqa: E402

SCENE = os.path.join(HERE, 'scene_car1v2')
add, comp = cs.add, cs.comp


def bbox(shape):
    v = shape.vals()
    return (v[0] if len(v) == 1 else shape.combine().val()).BoundingBox()


def rplidar_c1(pinfo):
    """Slamtec RPLidar C1 envelope: a square base with a round scanning head on top"""
    w, d, h = car1v2.C['C1_BODY']
    xc, z0, z1 = pinfo['centre_x'], pinfo['base_z'], pinfo['top_z']
    zb = z0 + 0.46 * h
    base = box(xc - d / 2, xc + d / 2, -w / 2, w / 2, z0, zb).edges('|Z').fillet(9.0)
    add('c1_base', base, 'sensor_dark', 'sensors')
    head = cylz(xc, 0, zb, z1, w - 4.0).edges('>Z').fillet(3.0)
    add('c1_head', head, 'optics_black', 'sensors')
    add('c1_ring', cylz(xc, 0, zb, zb + 1.6, w - 2.4), 'sensor_grey', 'sensors')


def oak_d_pro(cinfo):
    """Luxonis OAK-D Pro envelope: a bar with two stereo lenses, the colour lens between them and the IR parts"""
    ow, oh, od = car1v2.C['OAKD']
    xb, xf = cinfo['camera_back_x'], cinfo['camera_front_x']
    zb = cinfo['camera_bottom_z']
    zc = zb + oh / 2
    body = box(xb, xf - 1.2, -ow / 2, ow / 2, zb, zb + oh).edges('|X').fillet(6.0)
    add('oakd_body', body, 'anodized_dark', 'sensors')
    face = box(xf - 1.2, xf, -ow / 2 + 2.5, ow / 2 - 2.5, zb + 2.5, zb + oh - 2.5).edges('|X').fillet(4.0)
    add('oakd_face', face, 'optics_black', 'sensors')
    rings, glass = [], []
    for y, dia in ((37.5, 13.0), (-37.5, 13.0), (0.0, 14.5)):
        rings.append(cyl((xf, y, zc), dia, 1.6, (1, 0, 0)).cut(cyl((xf - 0.5, y, zc), dia - 3.0, 3.0, (1, 0, 0))))
        glass.append(cyl((xf, y, zc), dia - 3.0, 0.9, (1, 0, 0)))
    for y in (17.0, -17.0):                                    # IR dot projector and flood LED windows
        glass.append(cyl((xf, y, zc), 5.0, 0.6, (1, 0, 0)))
    add('oakd_lens_rings', comp(*rings), 'lens_black', 'sensors')
    add('oakd_lens_glass', comp(*glass), 'glass', 'sensors')


def devkit(comps):
    """NVIDIA's Orin Nano dev kit: carrier, module under its heatsink and fan, the I/O edge and the header"""
    add('devkit_pcb', comps['devkit_pcb'], 'pcb_black', 'jetson')
    add('devkit_bottom_parts', comps['devkit_bottom_parts'], 'plastic_black', 'jetson')
    add('devkit_headers', comps['devkit_headers'], 'plastic_black', 'jetson')
    add('devkit_io', comps['devkit_io'], 'nickel', 'jetson')
    b = bbox(comps['jetson_module_and_sink'])
    x0, x1, y0, y1, z0, z1 = b.xmin, b.xmax, b.ymin, b.ymax, b.zmin, b.zmax
    add('module_pcb', box(x0, x1, y0, y1, z0 + 4.5, z0 + 5.7), 'pcb_dark', 'jetson')
    add('sodimm_socket', box(x0 - 3, x1 + 3, y1 - 6, y1 + 4, z0, z0 + 5.5), 'plastic_black', 'jetson')
    zf = z1 - 9.0                                               # fins up to here, the fan frame above
    plate = box(x0 + 2, x1 - 2, y0 + 1, y1 - 1, z0 + 5.7, z0 + 10.0).edges('|Z').fillet(1.5)
    n = int((x1 - x0 - 6) / 2.2)
    fins = [box(x0 + 3 + 2.2 * i, x0 + 4.2 + 2.2 * i, y0 + 1.5, y1 - 1.5, z0 + 10.0, zf) for i in range(n)]
    add('jetson_heatsink', comp(plate, *fins), 'anodized_dark', 'jetson')
    fx, fy = (x0 + x1) / 2, (y0 + y1) / 2
    shroud = box(fx - 21, fx + 21, y0 + 2, y1 - 2, zf, z1).edges('|Z').fillet(3)
    shroud = shroud.cut(cylz(fx, fy, zf + 0.5, z1 + 1, 38.0))
    add('jetson_fan_frame', shroud, 'plastic_black', 'jetson')
    blades = [box(4.0, 18.5, -3.2, 3.2, 0, 1.2).rotate((0, 0, 0), (1, 0, 0), 25).rotate((0, 0, 0), (0, 0, 1), 360 / 7 * i)
              .translate((fx, fy, z1 - 5.0)) for i in range(7)]
    add('jetson_fan_rotor', comp(cylz(fx, fy, z1 - 7.0, z1 - 2.5, 14.0), *blades), 'plastic_black', 'jetson')


def build():
    kb = kit.build()
    S, comps, parts, ex_k, info = kb
    ex = extras.build(kb)
    cs.chassis()                                                # the detailed stand-in, group 'chassis'
    # printed parts (PETG-CF)
    for k in ('deck_rear', 'deck_mid', 'deck_front', 'splice_rear_left', 'splice_rear_right', 'splice_front_left',
              'splice_front_right', 'bumper', 'side_pod_left', 'side_pod_right', 'camera_arch', 'esc_cradle', 'canopy_leg'):
        add(k, parts[k], 'petg_cf', 'deck')
    add('devkit_tray', parts['devkit_tray'], 'petg_cf', 'jetson')
    add('stack_canopy', ex[1]['stack_canopy'], 'petg_cf', 'canopy')
    plinth, pinfo = car1v2.c1_plinth()
    cradle, cinfo = car1v2.oakd_cradle(kit.ARCH_TOP)
    add('c1_plinth', plinth, 'petg_cf', 'deck')
    add('oakd_cradle', cradle, 'petg_cf', 'deck')
    eb = car1v2.estop_bracket()
    eb = eb[0] if isinstance(eb, tuple) else eb
    b, rb = eb.val().BoundingBox(), parts['deck_rear'].val().BoundingBox()
    add('estop_bracket', eb.translate((rb.xmin + 14 - b.xmin, -(b.ymin + b.ymax) / 2, rb.zmax - b.zmin)), 'petg_cf', 'deck')
    # sensors moved over from car 1
    rplidar_c1(pinfo)
    oak_d_pro(cinfo)
    # power board: the plain outline only when there is no KiCad model
    glb = os.path.join(ROOT, 'boards', 'power', 'out', 'render', 'atlas_power.glb')
    have_glb = os.path.exists(glb)
    if not have_glb:
        add('power_pcb', comps['power_pcb'], 'pcb_dark', 'power')
        add('power_parts_tall', comps['power_parts_tall'], 'plastic_black', 'power')
    add('fet_bar', comps['fet_bar'], 'alu', 'power')            # the FET heatsink bar, with or without the KiCad model
    add('fet_shield_acrylic', parts['laser_fet_shield'], 'clear_plastic', 'power')
    add('power_standoffs_7mm', comps['power_standoffs_7mm'], 'brass', 'power')
    add('tray_standoffs_25mm', comps['tray_standoffs_25mm'], 'brass', 'power')
    add('canopy_standoffs', comps['canopy_standoffs'], 'brass', 'jetson')
    devkit(comps)
    add('fsesc_case', comps['esc_case'].edges('|Z').fillet(2.0), 'alu_dark', 'deck')
    cs.side_fan()                                               # the 40 mm pod fan (Noctua colours)
    pb = bbox(comps['power_pcb'])
    return dict(have_glb=have_glb, power_at=[kit.POWER[0], kit.POWER[2], P['POWER_Z']])


def export():
    os.makedirs(SCENE, exist_ok=True)
    inf = build()
    man = {'objects': [], 'cables': [], 'boards': {}, 'units': 'mm'}
    for name, shape, mat, group in cs.OBJ:
        cq.exporters.export(shape, os.path.join(SCENE, name + '.stl'), tolerance=0.08, angularTolerance=0.12)
        man['objects'].append(dict(name=name, file=name + '.stl', material=mat, group=group))
    if inf['have_glb']:
        man['boards'] = {'power': dict(glb='boards/power/out/render/atlas_power.glb', at=inf['power_at'])}
    man['exploded'] = {'power': 45, 'jetson': 120, 'canopy': 195}      # lift per group in the exploded view, mm
    man['ground_z'] = cs.Z_GROUND
    man['focus'] = [10.0, 0.0, -40.0]
    json.dump(man, open(os.path.join(SCENE, 'scene.json'), 'w'), indent=1)
    print(len(man['objects']), 'objects ->', SCENE, '| power board model:', inf['have_glb'])


if __name__ == '__main__':
    export()
