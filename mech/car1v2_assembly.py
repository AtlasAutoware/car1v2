"""One 3D assembly of car 1 v2, stage 1, for the people building it.

    python3 mech/car1v2_assembly.py     # mech/out/car1v2/assembly/car1v2_assembly.step, .png and parts.json

Everything comes from the same models the parts are printed from: the chassis stand-in and the printed kit (kit.py),
the canopy (extras.py) and the car 1 v2 mounts (car1v2.py). The STEP file opens in SOLIDWORKS, Fusion, Onshape and
FreeCAD with every part named.

Not in the assembly, because nobody has measured where they go yet: the LiPo pack, the JK BMS and its holder, the
fuse, the XT90-S and the UBEC. The E-stop bracket is shown on the tail; its exact place is the builders' choice
(checklist B6). The chassis is a stand-in drawn from measurements, not Traxxas CAD.
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cadquery as cq
import kit, extras, car1v2
from kit import box

OUT = os.path.join(HERE, 'out', 'car1v2', 'assembly')

GREY, DARK, BLUE, ORANGE, GREEN, SILVER, RED, BLACK = (
    (0.62, 0.62, 0.62), (0.16, 0.16, 0.18), (0.13, 0.30, 0.52), (0.90, 0.45, 0.10), (0.10, 0.45, 0.20),
    (0.75, 0.77, 0.80), (0.75, 0.12, 0.10), (0.05, 0.05, 0.05))


def build():
    kb = kit.build()
    S, comps, parts, extras_k, info = kb
    ex = extras.build(kb)
    canopy = ex[1]['stack_canopy']
    plinth, pinfo = car1v2.c1_plinth()
    cradle, cinfo = car1v2.oakd_cradle(kit.ARCH_TOP)
    w, d, h = car1v2.C['C1_BODY']
    c1 = box(pinfo['centre_x'] - d / 2, pinfo['centre_x'] + d / 2, -w / 2, w / 2, pinfo['base_z'], pinfo['top_z'])
    ow, oh, od = car1v2.C['OAKD']
    cam = box(cinfo['camera_back_x'], cinfo['camera_front_x'], -ow / 2, ow / 2, cinfo['camera_bottom_z'],
              cinfo['camera_bottom_z'] + oh)
    # the E-stop bracket, moved from where it is drawn to the middle of the rear deck's back edge
    eb = car1v2.estop_bracket()
    eb = eb[0] if isinstance(eb, tuple) else eb
    bb = eb.val().BoundingBox(); rb = parts['deck_rear'].val().BoundingBox()
    eb = eb.translate((rb.xmin + 14 - bb.xmin, -(bb.ymin + bb.ymax) / 2, rb.zmax - bb.zmin))

    items = []          # (name, solid, colour, group)
    for k, v in S.items():
        items.append((f'chassis_{k}', v, BLACK if 'tyre' in k else GREY, 'Slash 4x4 chassis (stand-in)'))
    for k in ('deck_rear', 'deck_mid', 'deck_front', 'splice_rear_left', 'splice_rear_right', 'splice_front_left',
              'splice_front_right'):
        items.append((k, parts[k], DARK, 'printed: deck'))
    for k in ('bumper', 'side_pod_left', 'side_pod_right', 'camera_arch', 'devkit_tray', 'canopy_leg', 'esc_cradle'):
        items.append((k, parts[k], BLUE, 'printed: kit'))
    items.append(('stack_canopy', canopy, BLUE, 'printed: kit'))
    items.append(('c1_plinth', plinth, ORANGE, 'printed: car 1 v2 mounts'))
    items.append(('oakd_cradle', cradle, ORANGE, 'printed: car 1 v2 mounts'))
    items.append(('estop_bracket_place_is_your_choice', eb, ORANGE, 'printed: car 1 v2 mounts'))
    items.append(('rplidar_c1', c1, RED, 'sensors (moved over from car 1)'))
    items.append(('oak_d_pro', cam, RED, 'sensors (moved over from car 1)'))
    for k in ('power_pcb', 'power_parts_low', 'power_parts_tall', 'fet_bar'):
        items.append((k, comps[k], GREEN, 'power board'))
    items.append(('fet_shield_acrylic', parts['laser_fet_shield'], SILVER, 'power board'))
    for k in ('power_standoffs_7mm', 'tray_standoffs_25mm', 'canopy_standoffs'):
        items.append((k, comps[k], SILVER, 'standoffs'))
    for k in ('devkit_pcb', 'jetson_module_and_sink', 'devkit_io', 'devkit_headers', 'devkit_bottom_parts'):
        items.append((k, comps[k], GREEN, 'Jetson dev kit'))
    items.append(('fsesc', comps['esc_case'], SILVER, 'motor controller'))
    items.append(('pod_fan_40mm', comps['fan_40mm'], BLACK, 'fan'))
    return items


def main():
    os.makedirs(OUT, exist_ok=True)
    items = build()
    asm = cq.Assembly(name='car1v2_stage1')
    listing = []
    for name, solid, col, group in items:
        shape = solid if isinstance(solid, cq.Workplane) else cq.Workplane(obj=solid)
        try:
            vol = sum(s.Volume() for s in shape.vals() if hasattr(s, 'Volume'))
        except Exception:
            vol = 0.0
        if vol <= 0:
            continue
        asm.add(shape, name=name, color=cq.Color(*col))
        bb = shape.val().BoundingBox() if len(shape.vals()) == 1 else shape.combine().val().BoundingBox()
        listing.append(dict(name=name, group=group, size_mm=[round(bb.xlen, 1), round(bb.ylen, 1), round(bb.zlen, 1)]))
    path = os.path.join(OUT, 'car1v2_assembly.step')
    asm.save(path)
    json.dump(dict(parts=listing, not_included=['4S LiPo pack', 'JK BMS and its holder', 'MIDI fuse', 'XT90-S', 'UBEC',
                                                 'cables'], frame='x forward, y left, z up, mm; z = 0 is the top of the deck'),
              open(os.path.join(OUT, 'parts.json'), 'w'), indent=1)
    print(len(listing), 'parts;', round(os.path.getsize(path) / 1e6, 2), 'MB')
    try:
        import render
        render.render([(s, c) for _, s, c, _ in items], os.path.join(OUT, 'car1v2_assembly.png'),
                      views=((22, -58), (24, 128)), size=6.5)
        print('picture written')
    except Exception as e:
        print('no picture:', e)


if __name__ == '__main__':
    main()
