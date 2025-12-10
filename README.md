# Purpose
I wanted to make a dawless setup, yada yada, ended up picking a Raspberry Pi 4 as the brains of it. Barring any unforeseen tech problems, the Pi will be run headless, broadcasting a wifi hotspot and controlled over SSH via RaspController. See also my other repo, LoChord (also a work in progress).

The scripts I have here in their current form allow me to:
- Run and configure Fluidsynth (soundfonts, instruments, channel mutes)
- Freely route audio and MIDI pipes via pipewire
- Save and load full Fluidsynth and Pipewire configs

# Setup
All these scripts should be placed into a single folder. Within that folder there must be a file called `current.sav`, a subfolder called `saves`, and another subfolder called `fonts` which contains `FluidR3_GM.sf2` (you can find this file in `/usr/share/sounds/sf2/`), along with any other soundfonts you wish to load.

I recommend creating aliases for all of these scripts like so:
```
alias fs="FULL_PATH_TO_FOLDER/toggle_fluidsynth.sh"
alias mut='/usr/bin/python3 "FULL_PATH_TO_FOLDER/fs_mutes.py"'
alias inst='/usr/bin/python3 "FULL_PATH_TO_FOLDER/fs_instruments.py"'
alias font='/usr/bin/python3 "FULL_PATH_TO_FOLDER/fs_fonts.py"'
alias cfs="FULL_PATH_TO_FOLDER/check_fluidsynth.sh"
alias fst="FULL_PATH_TO_FOLDER/fsterm.sh"

alias sst='/usr/bin/python3 "FULL_PATH_TO_FOLDER/save_set.py"'
alias lst='/usr/bin/python3 "FULL_PATH_TO_FOLDER/load_set.py"'
alias rl='/usr/bin/python3 "FULL_PATH_TO_FOLDER/reload_current.py"'

alias rt='/usr/bin/python3 "FULL_PATH_TO_FOLDER/midiroute.py"'
alias art='/usr/bin/python3 "FULL_PATH_TO_FOLDER/audioroute.py"'
alias pan='/usr/bin/python3 "FULL_PATH_TO_FOLDER/panic.py"'

alias 128="FULL_PATH_TO_FOLDER/128.sh"
alias 1024="FULL_PATH_TO_FOLDER/1024.sh"
```

# Caveats (will be fixed eventually but i might not update te repo)
- `rl` (reload_current) shouldn't really be used if you have fonts configured because it will re-import them. in that case you should use `fs; sleep 0.5; fs`
- currently no way to remove a soundfont from the config.
- poor error handling and code quality in general.
- some of these are made using AI, some aren't

# Usage
### Fluidsynth scripts
`toggle_fluidsynth.sh`:
- runs Fluidsynth if it's not already running, then loads `current.sav`
- stops Fluidsynth if it's already going
- FS creates a terminal at localhost port 9988

`fs_mutes.py`:
- mutes and unmutes MIDI channels in Fluidsynth using CCs

`fs_instruments.py`:
- sets specified Fluidsynth MIDI channels to selected instruments
- attempts to default to most recently edited channel & most recently selected soundfont
- press enter on the search input to show the full list

`fs_fonts.py`:
- loads soundfonts from the `fonts` folder
- FS exclusively loads fonts in order with no reflowing or anything. I can't choose which ID they load to so this one should be considered very fragile.

`check_fluidsynth.sh`:
- checks whether fluidsynth is running

`fsterm.sh`:
- gets you to the fluidsynth terminal. it's normal to not see any output, just type help and go from there

### Config scripts
`save_set.py`:
- copies the current config to a specified slot

`load_set.py`:
- loads a config from a specified slot. fragile soundfont caveat applies.

`reload_current.py`:
- the same as running `load_set` then choosing `current.sav`.

### Routing scripts
`midiroute.py`:
- lists currently active MIDI connections, then provides list of sources then list of sinks to link as desired
- if linking two ports that are already linked, will disconnect them

`audioroute.py`:
- lists currenlty active Pipewire connections, then provides list of sources then list of sinks
- nodes will be displayed with their channel count in parentheses, or with the name of their only port appended to the end
- port-by-port connections are made using connection masks as explained in a later section

`panic.py`:
- disconnects all Pipewire links, thereby silencing all audio output

### Buffer size scripts
128 sets the buffer size to 128 samples, 1024 does 1024. Both reload the current config.

### What is a connection mask?
It's a list of which of the source channels will connect to the sink channels. For instance, a connection mask of 210 will mean to connect the SECOND source port to the first sink port, the FIRST source port to the second sink port, and NOTHING to the third sink port.
