#!/usr/bin/env bash
VIDEO_PATH="/home/embebidos/splash/intro.mp4"

export TERM="${TERM:-linux}"
export SDL_VIDEODRIVER="${SDL_VIDEODRIVER:-kmsdrm}"

setterm -cursor off 2>/dev/null || true
clear

if [ -f "$VIDEO_PATH" ]; then
    if command -v mpv >/dev/null 2>&1; then
        mpv --fullscreen --really-quiet --no-terminal "$VIDEO_PATH" >/dev/null 2>&1 || true
    elif command -v ffplay >/dev/null 2>&1; then
        ffplay -fs -nodisp -autoexit -loglevel quiet "$VIDEO_PATH" >/dev/null 2>&1 || true
    fi
fi

while true; do
    setterm -cursor off 2>/dev/null || true
    python3 /home/embebidos/scripts/menu_ui.py >> /tmp/menu_ui.log 2>&1
    sleep 0.5
done
