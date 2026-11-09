"""Pressure force on each wall patch of an OpenFOAM case, from the ASCII mesh and saved p fields.

    patch_forces(case, rho) -> {patch: {Fx, Fy, Fz, sd_Fx, sd_Fz, samples, area}}

F = rho * sum over the patch's faces of p_owner_cell * S_face, with S_face pointing out of the fluid (into the
body). p is the kinematic pressure simpleFoam solves for. The walls are zeroGradient in p, so the face value is
the owner cell's value. Skin friction is not included: on this bluff shape it adds a few percent to the drag.
"""
import os, re
import numpy as np


def _body(path):
    t = open(path).read()
    i = t.index('(', t.index('}'))            # first '(' after the FoamFile header
    return t, i


def _labels(path):
    t, i = _body(path)
    return np.array(t[i + 1:t.rindex(')')].split(), dtype=np.int64)


def _points(path):
    t, i = _body(path)
    nums = np.array(re.sub(r'[()]', ' ', t[i + 1:t.rindex(')')]).split(), dtype=float)
    return nums.reshape(-1, 3)


def _faces(path, start, n):
    t, i = _body(path)
    lines = t[i + 1:t.rindex(')')].strip().split('\n')
    out = []
    for ln in lines[start:start + n]:
        k = ln.index('(')
        out.append(np.array(ln[k + 1:ln.rindex(')')].split(), dtype=np.int64))
    return out


def _boundary(path):
    t = open(path).read()
    res = {}
    for m in re.finditer(r'(\w+)\s*\{([^}]*)\}', t[t.index('('):]):
        d = m.group(2)
        nf = re.search(r'nFaces\s+(\d+)', d); sf = re.search(r'startFace\s+(\d+)', d)
        if nf and sf:
            res[m.group(1)] = (int(sf.group(1)), int(nf.group(1)))
    return res


def _internal_p(path):
    t = open(path).read()
    m = re.search(r'internalField\s+nonuniform\s+List<scalar>\s*(\d+)\s*\(', t)
    n = int(m.group(1))
    j = m.end()
    return np.array(t[j:t.index(')', j)].split(), dtype=float)[:n]


def patch_forces(case, rho, patches=('body', 'wing')):
    pm = os.path.join(case, 'constant', 'polyMesh')
    bnd = _boundary(os.path.join(pm, 'boundary'))
    pts = _points(os.path.join(pm, 'points'))
    owner = _labels(os.path.join(pm, 'owner'))
    times = sorted([d for d in os.listdir(case) if re.fullmatch(r'\d+', d) and d != '0'], key=int)
    out = {}
    for patch in patches:
        if patch not in bnd:
            continue
        start, n = bnd[patch]
        S = np.zeros((n, 3))
        for a, f in enumerate(_faces(os.path.join(pm, 'faces'), start, n)):
            v = pts[f]
            c = v.mean(axis=0)
            r = v - c
            S[a] = 0.5 * np.cross(r, np.roll(r, -1, axis=0)).sum(axis=0)
        own = owner[start:start + n]
        F = []
        for tname in times:
            p = _internal_p(os.path.join(case, tname, 'p'))
            F.append(rho * (p[own][:, None] * S).sum(axis=0))
        F = np.array(F)
        out[patch] = dict(Fx=float(F[:, 0].mean()), Fy=float(F[:, 1].mean()), Fz=float(F[:, 2].mean()),
                          sd_Fx=float(F[:, 0].std()), sd_Fz=float(F[:, 2].std()), samples=len(times),
                          area=float(np.linalg.norm(S, axis=1).sum()))
    return out


def region_cp(case, U, regions, patch='body'):
    """Area-weighted mean pressure coefficient of the patch faces inside each region.

    regions: {name: dict(box=((x0, y0, z0), (x1, y1, z1)), axis=0|1|2, sign=+1|-1|0)}. A face counts when its
    centre is in the box and its outward normal (out of the body, into the air) points mostly along `axis` with
    the given sign (0 = either). Cp = p / (U^2 / 2) with p the kinematic gauge pressure, so Cp = 1 at a stagnation
    point and negative means suction. Returns {name: {cp, sd_cp, area_m2, faces}}.
    """
    pm = os.path.join(case, 'constant', 'polyMesh')
    bnd = _boundary(os.path.join(pm, 'boundary'))
    pts = _points(os.path.join(pm, 'points'))
    owner = _labels(os.path.join(pm, 'owner'))
    start, n = bnd[patch]
    S = np.zeros((n, 3)); C = np.zeros((n, 3))
    for a, f in enumerate(_faces(os.path.join(pm, 'faces'), start, n)):
        v = pts[f]
        c = v.mean(axis=0)
        r = v - c
        S[a] = 0.5 * np.cross(r, np.roll(r, -1, axis=0)).sum(axis=0)
        C[a] = c
    own = owner[start:start + n]
    A = np.linalg.norm(S, axis=1)
    nrm = -S / A[:, None]                      # S points into the body; the outward normal is the other way
    times = sorted([d for d in os.listdir(case) if re.fullmatch(r'\d+', d) and d != '0'], key=int)
    P = np.array([_internal_p(os.path.join(case, t, 'p'))[own] for t in times])
    out = {}
    for name, r in regions.items():
        (x0, y0, z0), (x1, y1, z1) = r['box']
        m = ((C[:, 0] >= x0) & (C[:, 0] <= x1) & (C[:, 1] >= y0) & (C[:, 1] <= y1) & (C[:, 2] >= z0) & (C[:, 2] <= z1))
        comp = nrm[:, r['axis']]
        m &= (np.abs(comp) > 0.8) if r.get('sign', 0) == 0 else (comp * r['sign'] > 0.8)
        if not m.any():
            out[name] = dict(cp=None, sd_cp=None, area_m2=0.0, faces=0)
            continue
        cp = (P[:, m] * A[m]).sum(axis=1) / A[m].sum() / (0.5 * U * U)
        out[name] = dict(cp=round(float(cp.mean()), 3), sd_cp=round(float(cp.std()), 3),
                         area_m2=round(float(A[m].sum()), 5), faces=int(m.sum()))
    return out
