# Purpose
I wanted to make a dawless setup, yada yada, ended up picking a Raspberry Pi 4 as the brains of it. Barring any unforeseen tech problems, the Pi will be run headless, broadcasting a wifi hotspot and controlled over SSH via RaspController. See also my other repo, LoChord (also a work in progress).

The scripts I have here in their current form allow me to:
- Run and configure Fluidsynth (soundfonts, instruments, channel mutes)
- Freely route audio and MIDI pipes via pipewire
- Save and load full Fluidsynth and Pipewire configs

# Major update (May '26)
It's been months since I touched this repo but I might as well upload everything I have. The main changes are as follows:
- The Pi is here
- I'm using Reaper for audio multitracking (see ReaPad and Turing-Complete on ReaPack for how I control Reaper itself)
- Switched from using the wifi hotspot for script control to controlling everything on-device using a screen and a clicky encoder
- Code quality and organization remains bad
- LoChord won't run anymore (I have a guitar + use the controller for Reaper so it's no longer needed)

Run `curses_launcher.py` and navigate using L/R arrows plus Enter to get everything done. `gpio-encoder.py` just binds the encoder plus a couple bonus buttons to the main things.

Beyond this point almost all documentation is 5 months outdated.

# Setup
All these scripts should be placed into a single folder. Within that folder there must be a file called `current.sav`, a subfolder called `saves`, and another subfolder called `fonts` which contains `FluidR3_GM.sf2` (you can find this file in `/usr/share/sounds/sf2/`), along with any other soundfonts you wish to load. Most changes you make will be saved back to `current.sav`.

I recommend creating aliases for all of these scripts like so:
```
alias curses='/path/to/python3 "/path2/to/curses_launcher.py"'
alias lc='/path/to/python3 "/home/flynn/dawless/lochord/lochord.py"'

alias dm='/path2/to/daemons.sh'
alias log='/path2/to/dlog.sh'
alias slog='cat /home/flynn/logs/startup.log'
alias rlog='tail -f /home/flynn/logs/reaper.log'

alias fs="/path2/to/toggle_fluidsynth.sh"
alias mut='/path/to/python3 "/path2/to/fs_mutes.py"'
alias inst='/path/to/python3 "/path2/to/fs_instruments.py"'
alias font='/path/to/python3 "/path2/to/fs_fonts.py"'
alias cfs="/path2/to/check_fluidsynth.sh"
alias fst="/path2/to/fsterm.sh"

alias muter="/path2/to/toggle_sqtmuter.sh"
alias smut='/path/to/python3 "/path2/to/sqt_mutes.py"'
alias syxt='/path/to/python3 "/path2/to/syx_translator.py"'

alias sst='/path/to/python3 "/path2/to/save_set.py"'
alias lst='/path/to/python3 "/path2/to/load_set.py"'
alias rl='/path/to/python3 "/path2/to/reload_current.py"'
alias clean='/path/to/python3 "/path2/to/clean.py"'

alias rt='/path/to/python3 "/path2/to/midiroute.py"'
alias art='/path/to/python3 "/path2/to/audioroute.py"'
alias pan='/path/to/python3 "/path2/to/panic.py"'

alias 128="/path2/to/128.sh"
alias 1024="/path2/to/1024.sh"

alias st='dm & muter & fs'

alias reaper='pw-jack /home/flynn/opt/REAPER/reaper'
alias tr='/path2/to/toggle_reaper.sh'
alias reagui='rm /home/flynn/opt/REAPER/libSwell.so && cp /home/flynn/opt/REAPER/libSwell-gui.so /home/flynn/opt/REAPER/libSwell.so'
alias reatui='rm /home/flynn/opt/REAPER/libSwell.so && cp /home/flynn/opt/REAPER/libSwell-tui.so /home/flynn/opt/REAPER/libSwell.so'

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

### Seqtrak muter scripts
The Seqtrak muter creates a MIDI input and output that will pass through all MIDI messages except for select muted channels. Used for piping MIDI to my Yamaha Seqtrak which does not have incoming MIDI mute per channel on its own; this way one MIDI source can be used to control multiple sinks without issues. The muter script itself is essentially a daemon.

`toggle_sqtmuter.sh`:
- runs or stops the muter script

`sqt_mutes.py`:
- interfacing with the muter script
- uses an evil evil vile form of IPC done by writing and reading actual files (not pipes) in the same directory

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
