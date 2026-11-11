# Pictures for posting

All of these come out of the design files; none are photos.

| file | what it shows |
| --- | --- |
| `car_front_left.png`, `car_rear_right.png`, `car_side.png`, `car_top.png` | The whole car: the printed kit with the stack canopy, both boards, the pack, every cable and plug, on a stand-in Slash 4x4. Rendered with Blender Cycles by `render_car.py` from the scene `car_scene.py` builds out of `mech/kit.py`, `mech/extras.py` and the two boards' KiCad 3D models. |
| `car_exploded.png` | The same, with the drive board lifted 55 mm, the brain board 115 mm and the canopy 185 mm to show the stack. The cables are hidden in this one, and the antennas are folded back. |
| `drive_iso.png`, `drive_top.png`, `drive_bottom.png` | The drive board as routed, rendered by KiCad. The four bulk capacitors, the 2 x 20 stack socket and the power stage (FETs on the underside) are the big parts. |
| `brain_iso.png`, `brain_top.png` | The brain board (Jetson carrier) as routed, rendered by KiCad. The Jetson module and the NVMe card plug in and are not shown. Many of the parts from Antmicro's design, the module socket among them, have no 3D model here and show as bare pads. |
| `drive_thermal_70A.png` | Simulated temperature of the drive board at 70 A peak phase current with the fan, 35 C air: about 58 C on the hottest FET (`sim/drive_thermal.py`). |
| `dclink_waveforms.png` | Simulated ripple current in the ESC's bus capacitors (`sim/dclink.py`). |
| `precharge.png` | Simulated switch-on of the motor bus through the precharge resistors (`sim/precharge.py`). |
| `poe_boost.png` | Simulated 52 V boost that powers the camera over Ethernet (`sim/poe_boost.py`). |

Stand-ins: in the car pictures the chassis is drawn from `kit.py`'s keep-out numbers (all estimates), with
suspension, wheels and tread drawn to look plausible, not measured. The lidar, the camera and lens, the Jetson
module with the dev kit's heatsink and fan, the NVMe and Wi-Fi cards, the RJ45 jacks and plugs, the stacking
header, the 40 mm fan and the antennas are simple shapes sized from their datasheets or from kit.py's envelopes, not models of
the real parts. In the drive board pictures a few parts have no 3D model in KiCad and show as bare pads.

To make them again:

1. `boards/tools/run_kicad.sh glb-drive glb-brain render-drive render-brain` writes the board models and renders
   to `boards/*/out/render/`; copy the board PNGs you want here.
2. `python3 share/car_scene.py` writes the scene (`share/scene/`, not in git).
3. Render with `python3 share/render_car.py -- car_front_left car_rear_right car_side car_top car_exploded`, using
   Blender 4.2's `bpy` module (Python 3.11). About 12 minutes a view at 2700 x 1800 and 80 samples on two CPU
   cores; `--quick` gives a 900 x 600 preview in under a minute.
4. `sim/run_all.sh` writes the plots to `sim/out/`.

`make_renders.py` is the older VTK version, with no chassis, canopy or cables. It writes the same car file names.

## Car 1 v2 (11 November 2026)

| file | what it shows |
| --- | --- |
| `car1v2_car_front_left.png`, `car1v2_car_rear_right.png`, `car1v2_car_side.png`, `car1v2_car_top.png` | Car 1 v2, stage 1, on the stand-in Slash 4x4: the printed kit, the power board under the dev-kit tray, the Jetson dev kit, the canopy, the FSESC, the RPLidar C1 and the OAK-D Pro on their new mounts. 1800 x 1200, 96 samples. |
| `car1v2_car_exploded.png` | The same with the power board lifted 45 mm, the Jetson on its tray 120 mm and the canopy 195 mm. |
| `../boards/power/out/render/power_iso.png`, `power_top.png` | The power board with its parts, rendered by KiCad 10 on a transparent background. |

Not drawn, because nobody has measured where they go: the LiPo pack, the JK BMS, the fuse, the XT90-S, the UBEC and
every cable. The lidar, the camera, the Jetson dev kit, the FSESC and the fan are simple shapes sized from their
envelopes in `mech/`, not models of the real parts. In the whole-car pictures the power board is bare apart from
the FET heatsink bar: the GLB that kicad-cli exported on the team laptop has the board, copper and silkscreen but
no component models.

To make them again:

1. On the KiCad machine: `bash boards/tools/run_kicad.sh "" glb-power`, then in `boards/power`
   `kicad-cli pcb render --quality high --background transparent --perspective --rotate '-50,0,-35' --zoom 0.85 -w 2700 -h 1800 -o out/render/power_iso.png atlas_power.kicad_pcb`
   (and `--side top` for `power_top.png`).
2. `python3 share/car1v2_scene.py` writes the scene (`share/scene_car1v2/`, not in git). It needs CadQuery.
3. `python3 share/render_car.py -- --scene scene_car1v2 --prefix car1v2_ --size 1800x1200 --samples 96 car_front_left`
   and the same for `car_rear_right car_side car_top car_exploded`. About 5 minutes a view on two CPU cores.
