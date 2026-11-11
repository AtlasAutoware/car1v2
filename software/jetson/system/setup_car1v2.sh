#!/usr/bin/env bash
# Set up a Jetson Orin Nano dev kit for car 1 v2: the rev B power board (ATLAS-PWR-1) with car 1's sensors,
# an RPLidar C1 and an OAK-D Pro, both on USB.
#
#   sudo software/jetson/system/setup_car1v2.sh            # stage 1: C1 + OAK-D Pro, 4S LiPo
#   sudo software/jetson/system/setup_car1v2.sh --tim561   # later: also bring up the SICK TiM561 feed and network
#   sudo software/jetson/system/setup_car1v2.sh --check    # change nothing, only report what is plugged in
#
# It runs install.sh (the rev B tools, udev names, services, 25 W power mode), then adds what car 1 v2 changes:
# device names for the lidar and camera, the lidar feed setting, and the low-battery level for a LiPo.
# Safe to run again. Nothing here has run on hardware yet: read the summary it prints and fix what it flags.
set -euo pipefail
[ "$(id -u)" = 0 ] || { echo "run with sudo"; exit 1; }
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TIM561=0; CHECK=0
for a in "$@"; do
    case "$a" in
        --tim561) TIM561=1 ;;
        --check) CHECK=1 ;;
        *) echo "unknown option $a"; exit 2 ;;
    esac
done
CONF=/etc/atlas/atlas.conf
RULES=/etc/udev/rules.d/98-atlas-car1v2.rules
NOTE=()

setconf() {     # setconf KEY VALUE: replace or append KEY=VALUE in atlas.conf
    if grep -q "^$1=" "$CONF"; then sed -i "s|^$1=.*|$1=$2|" "$CONF"; else echo "$1=$2" >> "$CONF"; fi
}

if [ "$CHECK" = 0 ]; then
    echo ">> rev B base install"
    "$HERE/install.sh"

    echo ">> device names: /dev/rplidar (C1's USB adapter), OAK-D Pro usable without root"
    cat > "$RULES" <<'EOF'
# Car 1 v2 sensors. Installed by software/jetson/system/setup_car1v2.sh.
# RPLidar C1 through its USB adapter (Silicon Labs CP210x, 10c4:ea60): /dev/rplidar, as in Slamtec's rplidar.rules.
KERNEL=="ttyUSB*", ATTRS{idVendor}=="10c4", ATTRS{idProduct}=="ea60", MODE="0660", GROUP="dialout", SYMLINK+="rplidar"
# Luxonis OAK-D Pro (Movidius 03e7, booted and unbooted product IDs), as in Luxonis's 80-movidius.rules.
SUBSYSTEM=="usb", ATTRS{idVendor}=="03e7", MODE="0666"
EOF
    udevadm control --reload-rules
    udevadm trigger --subsystem-match=tty --subsystem-match=usb || true

    echo ">> settings in $CONF"
    # The board's switched lidar feed (J409) is for the TiM561. The C1 takes 5 V from its USB adapter.
    setconf ATLAS_LIDAR_AT_BOOT "$TIM561"
    # LiPo: shut down cleanly at 3.50 V per cell under load (the rev B value, 3.30 V, was for the 18650 pack).
    setconf ATLAS_SHUTDOWN_CELL_V 3.50
    if [ "$TIM561" = 0 ]; then
        # No Ethernet lidar: keep NetworkManager from waiting on its profile.
        nmcli connection modify atlas-lidar connection.autoconnect no 2>/dev/null || true
    else
        nmcli connection modify atlas-lidar connection.autoconnect yes 2>/dev/null || true
    fi
    systemctl daemon-reload
    systemctl restart atlas-battery.service 2>/dev/null || NOTE+=("atlas-battery.service did not restart: journalctl -u atlas-battery")
fi

echo
echo "== car 1 v2 hardware check =="
have() { if eval "$2" >/dev/null 2>&1; then echo "  ok       $1"; else echo "  MISSING  $1"; NOTE+=("$3"); fi; }
have "power board supervisor (Pico) at /dev/atlas_supervisor" "test -e /dev/atlas_supervisor" \
     "no supervisor: is the Pico's micro-USB lead in a dev-kit USB-A port, and is main.py on the Pico?"
have "FSESC UART at /dev/atlas_vesc" "test -e /dev/atlas_vesc" \
     "no /dev/atlas_vesc: check the 40-wire ribbon on J12 and the getty note install.sh printed"
have "RPLidar C1 adapter at /dev/rplidar" "test -e /dev/rplidar" \
     "no /dev/rplidar: plug the C1's USB adapter into a dev-kit USB-A port (lsusb should list 10c4:ea60)"
have "OAK-D Pro on USB (03e7)" "lsusb -d 03e7:" \
     "no OAK-D Pro: use a USB 3 port and the cable from car 1; with the IR projector on it may need Luxonis's Y-adapter"
if lsusb -t 2>/dev/null | grep -B3 -i 'Driver=usbfs\|Class=Vendor' | grep -q '480M'; then
    NOTE+=("a USB device is linked at 480M: if that is the OAK-D Pro, move it to a blue USB 3 port")
fi
if command -v atlas >/dev/null; then
    echo
    atlas status 2>/dev/null | head -20 || NOTE+=("'atlas status' failed: sudo journalctl -u atlas-battery -n 30")
fi
echo
echo "Still to do by hand:"
echo "  - install the car's driving stack on this Jetson (the carv1 repository) and its Python and ROS packages;"
echo "  - steering goes through the FSESC's servo output, as on car 1, so the stack's steering path is unchanged;"
echo "    the servo and chassis are new, so run the steering calibration again;"
echo "  - run the VESC motor detection for the Puller Pro (docs/FLASHING.md, B4), then the drive calibration;"
echo "  - set this Jetson's clock after every power-off until it has an RTC battery."
for n in "${NOTE[@]+"${NOTE[@]}"}"; do echo "NOTE: $n"; done
