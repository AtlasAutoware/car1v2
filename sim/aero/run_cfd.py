"""Steady RANS (OpenFOAM simpleFoam, k-omega SST) of car 1 v2 on a moving ground.

    python3 sim/aero/run_cfd.py CASE [SPEED]     CASE: nowing | wing_0 | wing_m12 | wing_m20     SPEED m/s, default 8

Needs OpenFOAM v1912 (Ubuntu: apt install openfoam; this script sources /usr/share/openfoam/etc/bashrc) and the
STLs from make_geometry.py. Writes sim/aero/out/cases/CASE/ and appends the result to sim/aero/out/results.json.

Set-up, so the numbers can be judged: domain 2.5 x 1.2 x 0.7 m, 40 mm base cells, 10 mm in a box round the car,
5 mm on the car and 2.5 to 1.25 mm on the wing; no prism layers, wall functions; ground moving at the car's
speed, wheels not rotating; pressure forces (no skin friction) averaged over the fields saved at five
iteration counts in the last third of the run. Coarse on purpose: it runs in
about 20 minutes on two cores and is meant for comparing variants, not for absolute numbers.
"""
import os, sys, json, glob, subprocess, shutil, textwrap
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'out')
RHO, NU = 1.2, 1.5e-5
ITER = 500
SAVE_EVERY, KEEP = 40, 5          # pressure fields kept at 340, 380, ... 500 for the force average
HEAD = 'FoamFile\n{\n    version 2.0;\n    format ascii;\n    class %s;\n    object %s;\n}\n'


def w(case, rel, cls, obj, body):
    p = os.path.join(case, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, 'w').write(HEAD % (cls, obj) + textwrap.dedent(body))


def make_case(name, V):
    case = os.path.join(OUT, 'cases', name)
    shutil.rmtree(case, ignore_errors=True)
    os.makedirs(os.path.join(case, 'constant', 'triSurface'))
    shutil.copy(os.path.join(OUT, 'geom', 'body.stl'), os.path.join(case, 'constant', 'triSurface', 'body.stl'))
    has_wing = name != 'nowing'
    if has_wing:
        shutil.copy(os.path.join(OUT, 'geom', name + '.stl'), os.path.join(case, 'constant', 'triSurface', 'wing.stl'))
    w(case, 'system/blockMeshDict', 'dictionary', 'blockMeshDict', '''
        scale 1;
        vertices ((-1.6 -0.6 0) (0.9 -0.6 0) (0.9 0.6 0) (-1.6 0.6 0) (-1.6 -0.6 0.7) (0.9 -0.6 0.7) (0.9 0.6 0.7) (-1.6 0.6 0.7));
        blocks (hex (0 1 2 3 4 5 6 7) (62 30 18) simpleGrading (1 1 1));
        edges ();
        boundary
        (
            inlet  { type patch; faces ((1 2 6 5)); }
            outlet { type patch; faces ((0 4 7 3)); }
            ground { type wall;  faces ((0 3 2 1)); }
            top    { type patch; faces ((4 5 6 7)); }
            sides  { type patch; faces ((0 1 5 4) (3 7 6 2)); }
        );
        ''')
    wing_geo = 'wing.stl { type triSurfaceMesh; name wing; }' if has_wing else ''
    wing_ref = 'wing { level (4 5); }' if has_wing else ''
    w(case, 'system/snappyHexMeshDict', 'dictionary', 'snappyHexMeshDict', f'''
        castellatedMesh true; snap true; addLayers false;
        geometry
        {{
            body.stl {{ type triSurfaceMesh; name body; }}
            {wing_geo}
            nearBox {{ type searchableBox; min (-0.60 -0.24 0); max (0.36 0.24 0.36); }}
        }}
        castellatedMeshControls
        {{
            maxLocalCells 1500000; maxGlobalCells 2500000; minRefinementCells 10; maxLoadUnbalance 0.1;
            nCellsBetweenLevels 2; features (); resolveFeatureAngle 30;
            refinementSurfaces {{ body {{ level (3 3); }} {wing_ref} }}
            refinementRegions {{ nearBox {{ mode inside; levels ((1e15 2)); }} }}
            locationInMesh (0.701 0.411 0.513); allowFreeStandingZoneFaces true;
        }}
        snapControls {{ nSmoothPatch 3; tolerance 2.0; nSolveIter 30; nRelaxIter 5; nFeatureSnapIter 10;
                        implicitFeatureSnap true; explicitFeatureSnap false; multiRegionFeatureSnap false; }}
        addLayersControls {{ relativeSizes true; layers {{}} expansionRatio 1.0; finalLayerThickness 0.3; minThickness 0.1;
                        nGrow 0; featureAngle 60; nRelaxIter 3; nSmoothSurfaceNormals 1; nSmoothNormals 3; nSmoothThickness 10;
                        maxFaceThicknessRatio 0.5; maxThicknessToMedialRatio 0.3; minMedianAxisAngle 90;
                        nBufferCellsNoExtrude 0; nLayerIter 50; }}
        meshQualityControls {{ maxNonOrtho 65; maxBoundarySkewness 20; maxInternalSkewness 4; maxConcave 80; minVol 1e-13;
                        minTetQuality -1e30; minArea -1; minTwist 0.02; minDeterminant 0.001; minFaceWeight 0.05;
                        minVolRatio 0.01; minTriangleTwist -1; nSmoothScale 4; errorReduction 0.75;
                        relaxed {{ maxNonOrtho 75; }} }}
        mergeTolerance 1e-6;
        ''')
    # No function objects: the Ubuntu 24.04 build of OpenFOAM v1912 stops with "error in IOstream sha1" as soon
    # as controlDict has one. Forces are integrated from the saved pressure fields instead (foam_forces.py).
    w(case, 'system/controlDict', 'dictionary', 'controlDict', f'''
        application simpleFoam; startFrom latestTime; startTime 0; stopAt endTime; endTime {ITER}; deltaT 1;
        writeControl timeStep; writeInterval {SAVE_EVERY}; purgeWrite {KEEP}; writeFormat ascii; writePrecision 7;
        timeFormat general; timePrecision 6; runTimeModifiable false;
        ''')
    w(case, 'system/fvSchemes', 'dictionary', 'fvSchemes', '''
        ddtSchemes { default steadyState; }
        gradSchemes { default Gauss linear; grad(U) cellLimited Gauss linear 1; }
        divSchemes
        {
            default none;
            div(phi,U) bounded Gauss linearUpwind grad(U);
            div(phi,k) bounded Gauss upwind;
            div(phi,omega) bounded Gauss upwind;
            div((nuEff*dev2(T(grad(U))))) Gauss linear;
        }
        laplacianSchemes { default Gauss linear limited 0.5; }
        interpolationSchemes { default linear; }
        snGradSchemes { default limited 0.5; }
        wallDist { method meshWave; }
        ''')
    w(case, 'system/fvSolution', 'dictionary', 'fvSolution', '''
        solvers
        {
            p { solver GAMG; smoother GaussSeidel; tolerance 1e-7; relTol 0.05; }
            "(U|k|omega)" { solver smoothSolver; smoother symGaussSeidel; tolerance 1e-8; relTol 0.1; }
        }
        SIMPLE { nNonOrthogonalCorrectors 1; consistent yes; }
        relaxationFactors { equations { U 0.8; k 0.7; omega 0.7; } }
        ''')
    w(case, 'constant/transportProperties', 'dictionary', 'transportProperties', f'transportModel Newtonian;\nnu {NU};\n')
    w(case, 'constant/turbulenceProperties', 'dictionary', 'turbulenceProperties',
      'simulationType RAS;\nRAS { RASModel kOmegaSST; turbulence on; printCoeffs off; }\n')
    k = 1.5 * (0.01 * V) ** 2
    om = k ** 0.5 / (0.09 ** 0.25 * 0.02)
    walls = ['body', 'wing'] if has_wing else ['body']

    def bf(inlet, outlet, ground, wall, slip='slip'):
        s = f'    inlet {{ {inlet} }}\n    outlet {{ {outlet} }}\n    ground {{ {ground} }}\n    top {{ type {slip}; }}\n    sides {{ type {slip}; }}\n'
        for p in walls:
            s += f'    {p} {{ {wall} }}\n'
        return s
    def field(name, cls, dim, internal, b):
        p = os.path.join(case, '0', name)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, 'w').write(HEAD % (cls, name) + f'dimensions {dim};\ninternalField uniform {internal};\nboundaryField\n{{\n{b}}}\n')
    field('U', 'volVectorField', '[0 1 -1 0 0 0 0]', f'({-V} 0 0)',
          bf(f'type fixedValue; value uniform ({-V} 0 0);', f'type inletOutlet; inletValue uniform (0 0 0); value uniform ({-V} 0 0);',
             f'type fixedValue; value uniform ({-V} 0 0);', 'type noSlip;'))
    field('p', 'volScalarField', '[0 2 -2 0 0 0 0]', '0',
          bf('type zeroGradient;', 'type fixedValue; value uniform 0;', 'type zeroGradient;', 'type zeroGradient;'))
    field('k', 'volScalarField', '[0 2 -2 0 0 0 0]', f'{k}',
          bf(f'type fixedValue; value uniform {k};', f'type inletOutlet; inletValue uniform {k}; value uniform {k};',
             f'type kqRWallFunction; value uniform {k};', f'type kqRWallFunction; value uniform {k};'))
    field('omega', 'volScalarField', '[0 0 -1 0 0 0 0]', f'{om}',
          bf(f'type fixedValue; value uniform {om};', f'type inletOutlet; inletValue uniform {om}; value uniform {om};',
             f'type omegaWallFunction; value uniform {om};', f'type omegaWallFunction; value uniform {om};'))
    field('nut', 'volScalarField', '[0 2 -1 0 0 0 0]', '0',
          bf('type calculated; value uniform 0;', 'type calculated; value uniform 0;',
             'type nutkWallFunction; value uniform 0;', 'type nutkWallFunction; value uniform 0;'))
    return case


def sh(case, cmd, log):
    full = f'set +u; source /usr/share/openfoam/etc/bashrc >/dev/null 2>&1; cd {case} && {cmd} > {log} 2>&1'
    return subprocess.run(['bash', '-c', full]).returncode


def main():
    name = sys.argv[1]
    V = float(sys.argv[2]) if len(sys.argv) > 2 else 8.0
    case = make_case(name, V)
    for cmd, log in (('blockMesh', 'log.blockMesh'), ('snappyHexMesh -overwrite', 'log.snappy'),
                     ('checkMesh -latestTime', 'log.checkMesh'), ('simpleFoam', 'log.simpleFoam')):
        rc = sh(case, cmd, log)
        if rc != 0 and cmd != 'checkMesh -latestTime':
            print(name, cmd, 'failed, see', os.path.join(case, log)); sys.exit(1)
    cells = None
    for line in open(os.path.join(case, 'log.checkMesh')):
        if line.strip().startswith('cells:'):
            cells = int(line.split()[1])
    res = dict(case=name, speed_mps=V, cells=cells, iterations=ITER, rho=RHO)
    q = 0.5 * RHO * V * V
    geo = json.load(open(os.path.join(OUT, 'geom', 'geometry.json')))
    A = geo['frontal_area_m2']['no_wing' if name == 'nowing' else 'wing_0']
    import foam_forces
    forces = foam_forces.patch_forces(case, RHO)
    tot_x = tot_z = 0.0
    for patch in ('body', 'wing'):
        fr = forces.get(patch)
        if fr:
            res[patch] = dict(drag_N=round(-fr['Fx'], 4), lift_N=round(fr['Fz'], 4), side_N=round(fr['Fy'], 4),
                              sd_drag_N=round(fr['sd_Fx'], 4), sd_lift_N=round(fr['sd_Fz'], 4), samples=fr['samples'],
                              area_m2=round(fr['area'], 4))
            tot_x += -fr['Fx']; tot_z += fr['Fz']
    res['total'] = dict(drag_N=round(tot_x, 4), lift_N=round(tot_z, 4), frontal_area_m2=A,
                        Cd=round(tot_x / (q * A), 3), Cl=round(tot_z / (q * A), 3), CdA_m2=round(tot_x / q, 5))
    path = os.path.join(OUT, 'results.json')
    allr = json.load(open(path)) if os.path.exists(path) else {}
    allr[f'{name}@{V:g}'] = res
    json.dump(allr, open(path, 'w'), indent=1)
    print(json.dumps(res, indent=1))


if __name__ == '__main__':
    main()
