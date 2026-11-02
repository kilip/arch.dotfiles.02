#!/bin/bash

WALLPAPER_DIRECTORY=~/wallpaper

WALLPAPER=$(find "$WALLPAPER_DIRECTORY" -mindepth 1 -type d | shuf -n 1)

hyprctl hyprpaper wallpaper "DP-1,$WALLPAPER/mon1.jpg"
hyprctl hyprpaper wallpaper "HDMI-A-1,$WALLPAPER/mon2.jpg"
hyprctl hyprpaper wallpaper "DVI-D-1,$WALLPAPER/mon3.jpg"
