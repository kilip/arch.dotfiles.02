#!/usr/bin/bash

# Kill running waybar and proxy
killall -q waybar
pkill -f "hypr-ipc-proxy.py"

# Start proxy in background
python3 "$HOME/.config/waybar/bin/hypr-ipc-proxy.py" --daemon
sleep 0.2

# Launch waybar detached
nohup setsid env HYPRLAND_INSTANCE_SIGNATURE=waybar_proxy waybar >/dev/null 2>&1 &
