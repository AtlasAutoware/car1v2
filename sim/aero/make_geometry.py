"""Aero geometry for car 1 v2, built from the same CAD the parts are printed from.

    python3 sim/aero/make_geometry.py   ->  sim/aero/out/geom/*.stl (metres, ground at z = 0, nose toward +x)
                                            sim/aero/out/step/car1v2_aero_*.step (millimetres, for SOLIDWORKS)

What is in the model: the chassis keep-out shapes from mech/kit.py (tub, gearbox, motor, towers, shocks), four
plain tyres, the deck, bumper, side pods, canopy, camera arch, the BMS standing on the pack lid, the RPLidar C1
on its plinth and the OAK-D Pro on its cradle. The wing (two struts and the blade with its end plates) is a
separate surface so it can be left out or pitched.

What is not: suspension arms, driveshafts, wheel rims and spokes, cables, the gaps between printed parts. The
chassis numbers are the estimates listed in docs/MEASURE_FIRST.md. Treat the forces as good to tens of percent.
"""
import os, sys, json, math
import cadquery as cq
import trimesh

HERE = os.path.dirname(os.path.abspath(__file__))
MECH = os.path.join(HERE, '..', '..', 'mech')
sys.path.insert(0, MECH)
import kit, extras, car1v2
from kit import P, box, cyl, cylz

OUT = os.path.join(HERE, 'out')
for d in ('geom', 'step'):
    os.makedirs(os.path.join(OUT, d), exist_ok=True)

GROUND_SINK = 2.0        # mm the tyres sink into the ground plane, so the contact patch is not a knife edge
WING_ANGLES = [0.0, -12.0, -20.0]     # degrees; negative = leading edge down = downforce


def tyres():
    r = P['TYRE_D'] / 2
    yc = P['TRACK'] / 2 - P['TYRE_W'] / 2
    zc = kit.Z_RIM + P['TYRE_TOP_ABOVE_RIM'] - r
    out = []
    for ax in (kit.FRONT_AXLE, kit.REAR_AXLE):
        for sy in (1, -1):
            out.append(cyl((ax, sy * yc - P['TYRE_W'] / 2, zc), P['TYRE_D'], P['TYRE_W'], (0, 1, 0)))
    return out, zc - r


def wing(angle_deg):
    struts = kit.wing_struts()
    blade = kit.wing_blade()
    if abs(angle_deg) > 1e-6:
        c0, c1 = kit.WING['chord']
        pivot = ((c0 + c1) / 2, 0, kit.WING['z'] + 2.5)
        # +x is forward; a positive rotation about +y lowers the leading (front) edge
        blade = blade.rotate(pivot, (pivot[0], 1, pivot[2]), -angle_deg)
    return struts + [blade]


def to_mesh(solids, z_ground):
    meshes = []
    for s in solids:
        tmp = os.path.join(OUT, 'geom', '_tmp.stl')
        cq.exporters.export(s, tmp, tolerance=0.2, angularTolerance=0.3)
        m = trimesh.load(tmp)
        meshes.append(m)
    m = trimesh.util.concatenate(meshes)
    m.apply_translation((0, 0, -z_ground))
    m.apply_scale(0.001)
    os.remove(os.path.join(OUT, 'geom', '_tmp.stl'))
    return m


def main():
    kb = kit.build()
    S, comps, parts, extras_k, info = kb
    ex = extras.build(kb)
    canopy = ex[1]['stack_canopy']
    arch_top = kit.ARCH_TOP
    plinth, pinfo = car1v2.c1_plinth()
    cradle, cinfo = car1v2.oakd_cradle(arch_top)
    w, d, h = car1v2.C['C1_BODY']
    c1 = box(pinfo['centre_x'] - d / 2, pinfo['centre_x'] + d / 2, -w / 2, w / 2, pinfo['base_z'], pinfo['top_z'])
    ow, oh, od = car1v2.C['OAKD']
    cam = box(cinfo['camera_back_x'], cinfo['camera_front_x'], -ow / 2, ow / 2, cinfo['camera_bottom_z'], cinfo['camera_bottom_z'] + oh)

    ty, z_tyre_bottom = tyres()
    z_ground = z_tyre_bottom + GROUND_SINK
    body = [v for k, v in S.items() if 'tyre' not in k]
    body += ty
    for k in ('deck_rear', 'deck_mid', 'deck_front', 'bumper', 'camera_arch', 'side_pod_left', 'side_pod_right', 'pack_lid'):
        body.append(parts[k])
    body += [canopy, plinth, c1, cradle, cam]
    try:
        body.append(kit.bms_solid())
    except Exception as e:           # the BMS envelope is optional in the model
        print('no BMS solid:', e)

    geo = {}
    mb = to_mesh(body, z_ground)
    mb.export(os.path.join(OUT, 'geom', 'body.stl'))
    geo['body'] = dict(bounds_m=[[round(float(x), 4) for x in b] for b in mb.bounds], triangles=int(len(mb.faces)))
    for a in WING_ANGLES:
        mw = to_mesh(wing(a), z_ground)
        name = f'wing_{int(round(a))}'.replace('-', 'm')
        mw.export(os.path.join(OUT, 'geom', name + '.stl'))
        geo[name] = dict(bounds_m=[[round(float(x), 4) for x in b] for b in mw.bounds], triangles=int(len(mw.faces)))

    # frontal area: rasterise the silhouette seen along x (2 mm pixels)
    import numpy as np
    def frontal(meshes):
        px = 0.001
        ys = np.concatenate([m.vertices[:, 1] for m in meshes]); zs = np.concatenate([m.vertices[:, 2] for m in meshes])
        y0, y1, z0, z1 = ys.min(), ys.max(), max(zs.min(), 0.0), zs.max()
        ny, nz = int((y1 - y0) / px) + 2, int((z1 - z0) / px) + 2
        img = np.zeros((ny, nz), bool)
        from PIL import Image, ImageDraw
        im = Image.new('1', (ny, nz), 0); dr = ImageDraw.Draw(im)
        for m in meshes:
            tri = m.vertices[m.faces][:, :, 1:3]
            for t in tri:
                dr.polygon([((p[0] - y0) / px, (p[1] - z0) / px) for p in t], fill=1)
        return float(np.asarray(im).sum()) * px * px
    mw0 = trimesh.load(os.path.join(OUT, 'geom', 'wing_0.stl'))
    geo['frontal_area_m2'] = dict(no_wing=round(frontal([mb]), 5), wing_0=round(frontal([mb, mw0]), 5))
    c0, c1x = kit.WING['chord']
    geo['wing'] = dict(chord_m=(c1x - c0) / 1000.0, span_m=2 * kit.WING['span'] / 1000.0,
                       area_m2=round((c1x - c0) * 2 * kit.WING['span'] / 1e6, 5),
                       height_above_ground_m=round((kit.WING['z'] - z_ground) / 1000.0, 4))
    geo['z_ground_mm_in_kit_frame'] = round(z_ground, 2)
    geo['length_m'] = round(float(mb.bounds[1][0] - mb.bounds[0][0]), 4)
    json.dump(geo, open(os.path.join(OUT, 'geom', 'geometry.json'), 'w'), indent=1)
    print(json.dumps(geo, indent=1))

    # STEP for SOLIDWORKS Flow Simulation: one assembly without the wing, one with it at 0 degrees
    for name, extra in (('car1v2_aero_no_wing', []), ('car1v2_aero_wing_0', wing(0.0))):
        asm = cq.Assembly(name=name)
        for i, s in enumerate(body + extra):
            asm.add(s.translate((0, 0, -z_ground)), name=f'solid_{i:02d}')
        asm.save(os.path.join(OUT, 'step', name + '.step'))


if __name__ == '__main__':
    main()
