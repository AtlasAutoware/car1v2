"""Car 1 v2 add-on parts for the rev B kit (Traxxas Slash 4x4).

    python3 mech/car1v2.py     ->  mech/out/car1v2/{stl,step,3mf,dxf}/ and car1v2_report.json

Car 1 v2 drives on car 1's RPLidar C1 and OAK-D Pro, so three parts change against `kit.py`:

  c1_plinth      replaces lidar_plinth. Same outline and the same four deck bolts, so the TiM561 plinth can go
                 back on later. The C1 is held from below by four M2.5 screws.
  oakd_cradle    replaces camera_cradle on the camera arch's tongue (same two M3 inserts). The OAK-D Pro hangs
                 on an upright by the two M4 holes in its back (VESA, 75 mm apart).
  estop_bracket  a bracket for a panel-mount emergency-stop button at the tail of the deck.
  bms_fence_jk   kit.bms_fence() rebuilt for the JK-B1A8S10P BMS (151 x 105 x 15.5 mm, Amazon listing) instead of
                 the JBD (160 x 105 x 10 mm). No interference check has been run on it.

Every other printed and laser-cut part comes from `kit.py` / `extras.py` unchanged.

Numbers and where they come from:
  RPLidar C1 body 55.6 x 55.6 x 41.3 mm, four M2.5 holes in the base, screws at most 4 mm deep
      (Slamtec datasheet C1M1-R2 v1.0). The hole PATTERN is only in the datasheet's figure 4-1, which could not
      be read, so the plinth has four diagonal slots that take any square pattern from C1_SLOT[0] to C1_SLOT[1]
      mm between hole centres. Measure the lidar; if its pattern is not square, set C1_HOLES and rerun.
  OAK-D Pro 97 x 29.5 x 22.9 mm (W x H x D, Luxonis datasheet, Dec 2021). Luxonis states a 75 mm M4 VESA pair
      on the back and a 1/4-20 thread underneath for the OAK-D and the PoE Pro; for the USB Pro that could not be
      read, so CONFIRM both on the camera in hand. The upright's slots take the M4 pair at any height on the back.
      The tripod thread is not used: its screw would have to pass through the arch tongue under the camera.
  E-stop panel hole: ESTOP_D, 22.3 mm for a 22 mm button or 16.2 for a 16 mm one. Set it to the button bought.
Environment variables of the same name override any number in C (as in kit.py).
"""
import os, sys, json, math
import cadquery as cq

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import kit                      # parameters and helpers only; kit.build() is not run
from kit import P, box, cylz, union, M3_CLEAR, M3_INSERT, M3_HEAD, PLINTH_BOLTS

OUT = os.path.join(HERE, 'out', 'car1v2')
for d in ('stl', 'step', '3mf', 'dxf'):
    os.makedirs(os.path.join(OUT, d), exist_ok=True)

C = dict(
    C1_BODY=(55.6, 55.6, 41.3),      # Slamtec datasheet
    C1_SCREW_MAX=4.0,                # mm of M2.5 thread allowed inside the lidar (datasheet)
    C1_SLOT=(36.0, 50.0),            # square hole patterns the slots accept, centre to centre
    C1_HOLES=None,                   # [(x, y), ...] from the body centre, once measured; replaces the slots
    C1_FLOOR=3.0,                    # plinth thickness under the lidar where the M2.5 screws pass
    M25_CLEAR=2.9, M25_HEAD=5.0,
    OAKD=(97.0, 29.5, 22.9),         # W (across the car), H, D (along the car): Luxonis datasheet
    OAKD_VESA=75.0,                  # M4 hole spacing on the back. CONFIRM on the camera.
    M4_CLEAR=4.5, OAKD_LIFT=8.0,     # camera underside above the base, so the two M3 heads fit under it
    ESTOP_D=22.3, ESTOP_PLATE=(46.0, 46.0), ESTOP_T=4.0, ESTOP_FOOT=24.0,
    JK_BMS=(151.0, 105.0, 15.5),     # 5.94 x 4.14 x 0.61 in on the Amazon listing; measure the unit
    OAKD_MASS_KG=0.10, CRASH_G=20.0, PETGCF_WEAK_MPA=20.0,   # hand check of the camera upright (mass and strength are round numbers)
)
for k in list(C):
    if k in os.environ:
        C[k] = json.loads(os.environ[k])


def c1_plinth():
    """Same outline, pocket position and deck bolts as kit.lidar_plinth; the lidar sits centred where the
    TiM561 did, in a 0.6 mm locating recess, on a floor thin enough for 4 mm of M2.5 thread engagement."""
    xf = P['LIDAR_FRONT_X']; xr = xf - 70.0; t = P['PLINTH_T']
    w, d, _ = C['C1_BODY']
    cx = xf - 39.0                               # lidar centre: here the four deck inserts miss all four slots
    p = box(xr, xf, -32, 32, 0, t).edges('|Z').fillet(4)
    p = p.cut(box(cx - d / 2 - 0.3, cx + d / 2 + 0.3, -w / 2 - 0.3, w / 2 + 0.3, t - 0.6, t + 1))
    floor = C['C1_FLOOR']
    # relief from below so a 6 mm M2.5 screw engages no more than C1_SCREW_MAX: floor + 0.6 recess left above
    relief_top = t - 0.6 - floor
    if C['C1_HOLES']:
        for (hx, hy) in C['C1_HOLES']:
            p = p.cut(cylz(cx + hx, hy, -1, t + 1, C['M25_CLEAR'])).cut(cylz(cx + hx, hy, -1, relief_top, C['M25_HEAD'] + 1.0))
    else:
        s0, s1 = C['C1_SLOT']
        r0, r1 = s0 / 2 * math.sqrt(2), s1 / 2 * math.sqrt(2)
        for ang in (45, 135, 225, 315):
            a = math.radians(ang)
            slot = (cq.Workplane('XY').center((r0 + r1) / 2, 0).slot2D(r1 - r0 + C['M25_CLEAR'], C['M25_CLEAR'])
                    .extrude(t + 2).translate((0, 0, -1)).rotate((0, 0, 0), (0, 0, 1), ang).translate((cx, 0, 0)))
            head = (cq.Workplane('XY').center((r0 + r1) / 2, 0).slot2D(r1 - r0 + C['M25_HEAD'] + 1.0, C['M25_HEAD'] + 1.0)
                    .extrude(relief_top + 1).translate((0, 0, -1)).rotate((0, 0, 0), (0, 0, 1), ang).translate((cx, 0, 0)))
            p = p.cut(slot).cut(head)
    for (x, y) in PLINTH_BOLTS:
        p = p.cut(cylz(x, y, -1, t - 1.0, M3_INSERT))
    # cable notch at the rear for the lidar's 5-pin lead
    p = p.cut(box(xr - 1, xr + 6, -6, 6, t - 2.5, t + 1))
    return p, dict(centre_x=round(cx, 2), base_z=round(t - 0.6, 2), top_z=round(t - 0.6 + C['C1_BODY'][2], 2),
                   screw='M2.5 x 6 from below' if abs((floor + C['C1_SCREW_MAX']) - 7.0) < 3.01 else 'check',
                   thread_engaged_mm=round(6.0 - floor, 2))


def oakd_cradle(arch_top):
    """Base on the arch tongue (two M3 screws into its inserts, heads counterbored) with an upright behind the
    camera. Two M4 screws through vertical slots in the upright go into the camera's back. Bolt the base
    down first, then hang the camera: its underside is OAKD_LIFT above the base, over the M3 heads."""
    w, h, d = C['OAKD']
    zb = arch_top
    ins = [P['LIDAR_FRONT_X'] - 58, P['LIDAR_FRONT_X'] - 42]          # the tongue's inserts (kit.camera_arch)
    xu1 = ins[0] - 7.0                                                # upright front face = camera back
    xu0 = xu1 - 5.0
    x_front = xu1 + d
    base = box(xu0 - 14.0, ins[1] + 6.0, -17, 17, zb, zb + 5.0)
    up_h = 5.0 + C['OAKD_LIFT'] + h + 2.0
    upright = box(xu0, xu1, -(C['OAKD_VESA'] / 2 + 8), C['OAKD_VESA'] / 2 + 8, zb, zb + up_h)
    c = union(base, upright)
    zc = zb + 5.0 + C['OAKD_LIFT'] + h / 2
    for sy in (-1, 1):
        y = sy * C['OAKD_VESA'] / 2
        c = c.cut(box(xu0 - 1, xu1 + 1, y - C['M4_CLEAR'] / 2, y + C['M4_CLEAR'] / 2, zc - 8.0, zc + 8.0))
        g = (cq.Workplane('XZ').polyline([(xu0, zb + 5.0), (xu0 - 14.0, zb + 5.0), (xu0, zb + 5.0 + 26.0)]).close()
             .extrude(4).translate((0, sy * 13.0 + 2.0, 0)))
        c = c.union(g)
    for x in ins:
        c = c.cut(cylz(x, 0, zb - 1, zb + 6, M3_CLEAR)).cut(cylz(x, 0, zb + 2.0, zb + 6, M3_HEAD))
    # cable relief for the camera's USB-C plug, which leaves the back of the body: open window in the upright centre
    c = c.cut(box(xu0 - 1, xu1 + 1, -14, 14, zb + 5.0 + C['OAKD_LIFT'] + 2.0, zb + up_h + 1))
    info = dict(camera_back_x=round(xu1, 2), camera_front_x=round(x_front, 2), camera_bottom_z=round(zb + 5.0 + C['OAKD_LIFT'], 2),
                lens_axis_z=round(zc, 2), arch_insert_x=ins, m4_slot_z=[round(zc - 8.0, 2), round(zc + 8.0, 2)],
                m3_head_clear_of_upright_mm=round(ins[0] - xu1 - M3_HEAD / 2, 2))
    return c, info


def estop_bracket():
    """An L: a foot with two M3 slots, and an upright plate with the panel hole. Printed lying on its side."""
    pw, ph = C['ESTOP_PLATE']; t = C['ESTOP_T']; foot = C['ESTOP_FOOT']
    plate = box(0, t, -pw / 2, pw / 2, 0, ph + t)
    base = box(0, foot, -pw / 2, pw / 2, 0, t)
    b = union(plate, base)
    b = b.cut(cq.Workplane('YZ').center(0, t + ph / 2).circle(C['ESTOP_D'] / 2).extrude(t + 2).translate((-1, 0, 0)))
    # anti-rotation flat marker: none; most buttons carry a 3.2 mm key notch at 12 o'clock
    b = b.cut(box(-1, t + 1, -1.7, 1.7, t + ph / 2 + C['ESTOP_D'] / 2 - 0.2, t + ph / 2 + C['ESTOP_D'] / 2 + 1.6))
    for sy in (-1, 1):
        b = b.cut(box(t + 6, foot - 5, sy * 15 - M3_CLEAR / 2, sy * 15 + M3_CLEAR / 2, -1, t + 1))
    for sy in (-1, 1):                                # gussets
        g = (cq.Workplane('XZ').polyline([(t, t), (t + 14, t), (t, t + 22)]).close().extrude(3)
             .translate((0, sy * (pw / 2 - 1.5) + 1.5, 0)))
        b = b.union(g)
    return b


def flat_dxf(solid, z, path):
    """Outline of a part at height z as a DXF (for laser-cutting a flat version)."""
    sec = cq.Workplane('XY').workplane(offset=z).add(solid.val()).section()
    cq.exporters.export(sec, path)


def main():
    L, scan_z, lidar_top = kit.tim561()
    kit.camera_arch(lidar_top)                 # sets kit.ARCH_TOP exactly as the kit's arch is printed
    arch_top = kit.ARCH_TOP
    plinth, pinfo = c1_plinth()
    cradle, cinfo = oakd_cradle(arch_top)
    estop = estop_bracket()
    old_bms = P['BMS']
    P['BMS'] = tuple(C['JK_BMS'])
    bms = kit.bms_fence()
    P['BMS'] = old_bms
    parts = dict(c1_plinth=plinth, oakd_cradle=cradle, estop_bracket=estop, bms_fence_jk=bms)
    orient = dict(c1_plinth=None, oakd_cradle=None, estop_bracket=((0, 1, 0), 90), bms_fence_jk=None)   # bracket lies on its upright
    rep = {}
    for name, p in parts.items():
        cq.exporters.export(p, os.path.join(OUT, 'step', f'{name}.step'))
        q = p
        if orient[name]:
            q = q.rotate((0, 0, 0), orient[name][0], orient[name][1])
        bb = q.val().BoundingBox()
        q = q.translate((-(bb.xmin + bb.xmax) / 2, -(bb.ymin + bb.ymax) / 2, -bb.zmin))
        cq.exporters.export(q, os.path.join(OUT, 'stl', f'{name}.stl'), tolerance=0.05, angularTolerance=0.15)
        cq.exporters.export(q, os.path.join(OUT, '3mf', f'{name}.3mf'), tolerance=0.05, angularTolerance=0.15)
        bb = q.val().BoundingBox()
        v = p.val().Volume() / 1000.0
        rep[name] = dict(bed_xyz=[round(bb.xlen, 1), round(bb.ylen, 1), round(bb.zlen, 1)], volume_cm3=round(v, 1),
                         mass_g_solid_petgcf=round(v * 1.30, 0), solids=len(p.val().Solids()))
    # flat versions for the laser: the plinth's plan (cut from 6 mm sheet, the lidar then sits on the surface) and the
    # E-stop plate alone (3 mm sheet, bolted to a printed or bent foot)
    flat_dxf(plinth, 1.0, os.path.join(OUT, 'dxf', 'c1_plinth_plan.dxf'))
    pw, ph = C['ESTOP_PLATE']
    pl = (cq.Workplane('XY').rect(pw, ph).extrude(1).cut(cq.Workplane('XY').circle(C['ESTOP_D'] / 2).extrude(1))
          .cut(cq.Workplane('XY').center(0, C['ESTOP_D'] / 2 + 0.7).rect(3.4, 1.8).extrude(1)))
    cq.exporters.export(pl.section(), os.path.join(OUT, 'dxf', 'estop_plate.dxf'))

    # checks
    lidar_top_c1 = pinfo['top_z']
    s0, s1 = C['C1_SLOT']
    r0 = s0 / 2 * math.sqrt(2) - (C['M25_HEAD'] + 1.0) / 2
    r1 = s1 / 2 * math.sqrt(2) + (C['M25_HEAD'] + 1.0) / 2
    worst = 1e9
    for (x, y) in PLINTH_BOLTS:                      # distance from each deck insert to the nearest slot relief
        dx, dy = x - pinfo['centre_x'], y
        for ang in (45, 135, 225, 315):
            a = math.radians(ang)
            t = max(r0, min(r1, dx * math.cos(a) + dy * math.sin(a)))      # closest point on the slot's centre line
            gap = math.hypot(dx - t * math.cos(a), dy - t * math.sin(a)) - (C['M25_HEAD'] + 1.0) / 2 - M3_INSERT / 2
            worst = min(worst, gap)
    body = C['C1_BODY']
    checks = dict(
        deck_insert_to_slot_relief_mm=round(worst, 2), deck_inserts_clear_of_slots=bool(worst >= 1.0),
        c1_body_inside_plinth=bool(pinfo['centre_x'] - body[1] / 2 >= P['LIDAR_FRONT_X'] - 70.0 and pinfo['centre_x'] + body[1] / 2 <= P['LIDAR_FRONT_X']),
        c1_top_below_camera_base_mm=round(arch_top - lidar_top_c1, 2),
        camera_lens_axis_above_c1_top_mm=round(cinfo['lens_axis_z'] - lidar_top_c1, 2),
        m3_heads_clear_of_upright=bool(cinfo['m3_head_clear_of_upright_mm'] >= 1.0),
    )
    assert all(v for k, v in checks.items() if isinstance(v, bool)), checks
    # hand check: the camera upright as a cantilever under a frontal stop of CRASH_G
    w_cam, h_cam, d_cam = C['OAKD']
    force = C['OAKD_MASS_KG'] * C['CRASH_G'] * 9.81
    arm = C['OAKD_LIFT'] + h_cam / 2                      # base top to the M4 slots, mm
    width = (C['OAKD_VESA'] + 16.0) - 28.0                # upright width less the cable window, mm
    z_sec = width * 5.0 ** 2 / 6.0                        # section modulus of the 5 mm upright, mm^3
    stress = force * arm / z_sec
    checks['camera_upright_hand_check'] = dict(force_N=round(force, 1), arm_mm=round(arm, 2), stress_MPa=round(stress, 2),
                                               factor_vs_weak_axis=round(C['PETGCF_WEAK_MPA'] / stress, 1), gussets_counted=False)
    out = dict(params=C, arch_top_z=round(arch_top, 2), tim561_top_z=round(lidar_top, 2), c1=pinfo, oakd=cinfo,
               checks=checks, parts=rep,
               unverified=['C1 hole pattern (slots cover square patterns 36 to 50 mm)', 'OAK-D Pro M4 pair on its back: spacing 75 mm and height (the slots take any height)', 'M4 thread depth in the camera: choose the screw so it does not bottom out',
                           'E-stop button diameter', 'where the E-stop bracket bolts to the deck (two M3 inserts to add at the tail)', 'JK BMS size and where its leads leave; bms_fence_jk has had no interference check'])
    json.dump(out, open(os.path.join(OUT, 'car1v2_report.json'), 'w'), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == '__main__':
    main()
