'''route midi from source to sink'''
import subprocess
import sys
import os
os.chdir(os.path.dirname(os.path.realpath(__file__))) # set cwd to where the script is
import seer_of_wires


import curses
from curses import wrapper
def concat(*args, sep=' '):
    return sep.join(str(arg) for arg in args)



def list_nodes(direction: str):
    inputs = ""
    for node in subprocess.check_output(['pw-link',direction]).decode():
        inputs = inputs + node
    inputs = inputs.split('\n')
    return inputs

def get_nodes(direction: str):
    inputs = list_nodes(direction)
    midis = []
    for i in inputs:
        if "Midi" in i:
            midis.append(i)

    binkum = []
    for i in midis:
        #binkum.append( (i, i.split(" (",1)[0].split(":")[-1] ) )
        name = i.split( ':',1 )[1].split( ' (' )[0].split('Client')[-1]
        if "Virtual RawMIDI" in name:
            name = "Reaper Clock"
        binkum.append( (i, name ) )

    # for n, node in enumerate(binkum):
    #     print(str(n) + ": " + node[1])
    return binkum

def match_node(direction: str, name: str):
    if "fluid" in name.lower():
        name = "synth input port"
    elif "reaper clock" in name.lower():
        name = "virtual rawmidi"
    nodes = list_nodes(direction)
    nodes.sort()
    for node in nodes:
        if "Midi" in node and name.lower() in node.lower():
            return node
    return "nada"

def save(source: str, sink: str, connected: bool) -> None:
    source = source.split(   " (capture"   ,1)[0].split(':')[-1] #source.split( ') ',1 )[1]
    if "synth input port" in sink.lower():
        sink = "fluid"
    elif "virtual rawmidi" in sink.lower():
        sink = "reaper clock"
    else:
        sink = sink.split(   " (playback"   ,1)[0].split(':')[-1] #sink.split( ') ',1 )[1]
    status_line = f'route ~ {source} ~ {sink}\n'
    with open('current.sav') as current:
        config = current.readlines()
    if status_line in config and not connected:
        config.remove(status_line)
        with open('current.sav','w') as current:
            current.writelines(config)
    elif connected and not status_line in config:
        with open('current.sav','w') as current:
            current.writelines(config)
            current.write('\n'+status_line)
    else:
        return

def route(source_in:str, sink_in:str, auto:str='') -> None:
    source = match_node("-o", source_in)
    sink = match_node("-i", sink_in)
    bad_source = source == 'nada'
    bad_sink = sink == 'nada'
    # todo write proper error feedback
    
    if bad_source and bad_sink:
        print(f"\tSource {source_in} and sink {sink_in} are both bad")
    elif bad_source:
        print(f"\tCannot find source {source_in}")
    elif bad_sink:
        print(f"\tCannot find sink {sink_in}")
    else:
        log = ""
        if auto == 'connect':
            log = subprocess.check_output(['pw-link', source, sink], stderr=subprocess.STDOUT).decode()
            print(f"Connected {source.split( ') ' ,1)[1]} -> {sink.split( ') ' ,1)[1]}")

        elif auto == 'drop':
            subprocess.check_output(['pw-link', '-d', source, sink])
            print(f"Disconnected {source.split( ') ' ,1)[1]} -> {sink.split( ') ' ,1)[1]}")

        else:
            try:
                log = subprocess.check_output(['pw-link', source, sink], stderr=subprocess.STDOUT).decode()
                print(f"Connected {source.split( ') ' ,1)[1]} -> {sink.split( ') ' ,1)[1]}")
                save(source, sink, True)
            except subprocess.CalledProcessError:
                subprocess.check_output(['pw-link', '-d', source, sink])
                print(f"Disconnected {source.split( ') ' ,1)[1]} -> {sink.split( ') ' ,1)[1]}")
                save(source, sink, False)

def select_loop(stdscr, entries: list, stage: str='', return_index: bool=False):
    curses.start_color()
    bw = curses.color_pair(0) # white on black if we need it
    curses.curs_set(0)
    def display(*args, sep=' '):
        stdscr.addstr( 1,0, concat( *args, sep ) )

    i = 1 # switch to specific selection and while loop
    key = "primed"

    while True:
        run = False
        stdscr.clear()
        stdscr.addstr( 12, 32, "L", curses.A_REVERSE)
        stdscr.addstr( 0,0, f"Main > Rt > MIDI{stage}")
        if key == "primed": # interpret key inputs
            pass
        elif key == curses.KEY_RIGHT:
            i += 1
        elif key == curses.KEY_LEFT:
            i -= 1
        elif key == ord('\n'):
            run = True

        if i < 0: # loop
            i = len(entries)-1
        if i >= len(entries):
            i = 0

        display(entries[i])
        if run: # wrap run action in conditional
            if return_index:
                return i
            else:
                return entries[i]

        stdscr.refresh()
        key = stdscr.getch() #refresh in loop, don't handle end feedback separately



def cursable(stdscr):
    wires = seer_of_wires.see(True)
    cables = []
    if wires:
        #print("Active connections:")
        for wire in wires:
            cables.append('   ' + ' -> '.join(wire))
    opts = ["Back","Active connections:", *cables, "Next" ]
    sel = select_loop(stdscr, opts)
    while sel not in ["Back", "Next"]:
        sel = select_loop(stdscr, opts)
    if sel == "Back":
        return

    sources = get_nodes('-o')
    s_f_s = []
    for s in sources:
        s_f_s.append(s[1])
    opts = ["Back","MIDI Sources:",*s_f_s]
    sel = select_loop(stdscr, opts, " > 1 Src", True)
    while sel == 1:
        sel = select_loop(stdscr, opts, " > 1 Src", True)
    if sel == 0:
        cursable(stdscr)
        return
    source_num = sel-2

    sinks = get_nodes('-i')
    s_f_s = []
    for s in sinks:
        s_f_s.append(s[1])
    opts = ["Back","MIDI Sinks:",*s_f_s]
    sel = select_loop(stdscr, opts, " > 2 Snk", True)
    while sel == 1:
        sel = select_loop(stdscr, opts, " > 2 Snk", True)
    if sel == 0:
        cursable(stdscr)
        return
    sink_num = sel-2

    try:
        output = subprocess.check_output(['pw-link', sources[source_num][0], sinks[sink_num][0]])
        if output != b'':
            print(output.decode())
        save(sources[source_num][0], sinks[sink_num][0], True)
        return "Nodes connected"
    except subprocess.CalledProcessError:
        output = subprocess.check_output(['pw-link', '-d', sources[source_num][0], sinks[sink_num][0]])
        if output != b'':
            print(output)
        return "Nodes disconnected"
        save(sources[source_num][0], sinks[sink_num][0], False)


if __name__ == '__main__':
    print(wrapper(cursable))
