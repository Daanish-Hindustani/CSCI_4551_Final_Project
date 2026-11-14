#!/usr/bin/env bash
set -eo pipefail
trap 'exit 0' INT TERM

source /workspace/install/setup.bash

Xvfb "$DISPLAY" -screen 0 1440x900x24 -nolisten tcp &
display_pid=$!
for attempt in {1..50}; do
    if xdpyinfo >/dev/null 2>&1; then
        break
    fi
    kill -0 "$display_pid"
    sleep 0.1
done
if ! xdpyinfo >/dev/null 2>&1; then
    echo "Xvfb failed to start" >&2
    exit 1
fi

openbox &
x11vnc -display "$DISPLAY" -localhost -rfbport 5900 -nopw -forever -shared &
websockify --web /usr/share/novnc 6080 127.0.0.1:5900 &
ros2 launch so101_description "${1:-sim.launch.py}" &
wait -n
