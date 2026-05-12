#!/bin/bash
cd "$(dirname "$0")"
if [ -n "$(pgrep -x reaper)" ]; then
    pkill -9 -x reaper
    echo "reaper killed"
else
    script -f -c "pw-jack /home/flynn/opt/REAPER/reaper" ~/logs/reaper.log > /dev/null &
    disown
    echo "reaper running"
fi

