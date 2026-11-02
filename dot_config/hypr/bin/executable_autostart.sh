#!/bin/bash

# 1. Buka remoat open (trigger antigravity server & window)
# remoat open &

# 2. Jalanin btop & Chrome duluan biar gak nunggu lama
# kitty --class btop_term -e btop &
# google-chrome-stable &

# 3. Kasih delay buat nunggu antigravity siap
# sleep 20

# 4. Fallback: Paksa pindahin window "Working" ke workspace 2
# hyprctl dispatch movetoworkspacesilent 2,title:Working

# 5. Terakhir jalanin remoat start:
# kitty --class remoat_term -e remoat start &

# /usr/bin/code &
