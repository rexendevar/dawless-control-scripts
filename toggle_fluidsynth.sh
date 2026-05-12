#!/bin/bash
PORT=9988
cd "$(dirname "$0")"

if [ -n "$(pgrep fluidsynth)" ]; then
    pkill -9 fluidsynth
    echo "fluidsynth killed"
else
    # Start with a Unix socket for control
    fluidsynth -is -a pipewire \
    fonts/FluidR3_GM.sf2 \
    -m alsa_seq -g 3 \
    -o shell.port=9988 -r 44100 \
    > /tmp/fluidsynth.log 2>&1 &
    disown
    echo "fluidsynth started"
    sleep 0.2
    python3 ./load_set.py 'current.sav'
fi
