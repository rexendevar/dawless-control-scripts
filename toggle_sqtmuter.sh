PORT=9988
cd "$(dirname "$0")"

if test -e ".sqtmute_instructions"; then
    echo q > .sqtmute_instructions
    echo "muter stopped"
else
    python3 ./muter.py &
    echo "muter started"
fi