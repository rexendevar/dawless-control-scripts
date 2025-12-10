cd "$(dirname "$0")"
pw-metadata -n settings 0 clock.force-quantum 128
pw-metadata -n settings 0 clock.force-rate 48000
python3 ./load_set.py current.sav