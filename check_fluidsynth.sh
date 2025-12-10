if [ -n "$(pgrep fluidsynth)" ]; then
    echo "fluidsynth is running"
else
    echo "fluidsynth is stopped"
fi