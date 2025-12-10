PORT=9988
cd "$(dirname "$0")"

if [ -n "$(pgrep fluidsynth)" ]; then
    pkill -9 fluidsynth
    echo "fluidsynth killed"
else
    # Start with a Unix socket for control
    fluidsynth -is -a alsa \
    fonts/FluidR3_GM.sf2 \
    -m alsa_seq -g 1 \
    -o shell.port=9988 \
    > /tmp/fluidsynth.log 2>&1 &
    disown
    echo "fluidsynth started"
    sleep 1
    python3 ./load_set.py 'current.sav'
fi