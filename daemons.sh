PORT=9988
cd "$(dirname "$0")"

if test -e ".keep_running_daemons"; then
    rm ./.keep_running_daemons
    echo "Daemons stopped"
else
    echo jhljh > .keep_running_daemons
    rm daemons.log
    python3 ./syx_translator.py &
    disown
    #python3 ../lochord/lochord.py &
    #disown
    echo "LoChord and SyxTranslator started"
fi