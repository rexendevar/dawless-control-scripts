#!/usr/bin/env python3
"""
Flexible MIDI Message Translator with Templates
"""
import os
os.chdir(os.path.dirname(os.path.realpath(__file__))) # set cwd to where the script is
import rtmidi
import time
PORT = 9988
import subprocess

channel = [0,1]
keep_running = True
levels = []

import curses
from curses import wrapper
def concat(*args, sep=' '):
    return sep.join(str(arg) for arg in args)

# [240, 67, 16, 127, 28, 12, 1, 16, 24, 1, 247]
# [240, 67, 16, 127, 28, 12, 1, 16, 46, 14, 247]


def cursable(stdscr):
    curses.curs_set(0)
    load_levels()
    posns = []
    stage = ''
    i = 0 # switch to specific selection and while loop
    key = "primed"
    while True:
        run = False
        #stdscr.clear()
        stdscr.addstr( 12, 32, "L", curses.A_REVERSE)
        stdscr.addstr( 0,0, f"Main > MIDI > Mixer{stage}")
        if key == "primed": # interpret key inputs
            pass
        elif key == curses.KEY_RIGHT:
            i += 1
        elif key == curses.KEY_LEFT:
            i -= 1
        elif key == ord('\n'):
            run = True

        if i < 0: # loop
            i = 16
        if i > 16:
            i = 0

        y,x = 1,0
        for L, level in enumerate(levels):
            if i == L:
                stdscr.addstr(y,x, format(level,"3d"), curses.A_REVERSE)
            else:
                stdscr.addstr(y,x, format(level,"3d"))
            if L == 7:
                y,x = 2,0
            else:
                x += 3
            posns.append((y,x))
        if i == 16:
            stdscr.addstr(3,0, "Back", curses.A_REVERSE)
        else:
            stdscr.addstr(3,0, "Back")

        # stdscr.addstr(y,x, '   ')
        # stdscr.addstr(y,x, cycle[i], curses.A_REVERSE)
        if run: # wrap run action in conditional
            if i == 16:
                save()
                return
            else:
                fuck_with(stdscr, posns[i-1], i)
            stdscr.addstr( 0,0, f"Main > MIDI > Mixer     ")

        stdscr.refresh()
        key = stdscr.getch() #refresh in loop, don't handle end feedback separately



def fuck_with(stdscr, pos:tuple, chan:int):
    stage = f" > {chan+1}"
    global levels
    i = levels[chan] # switch to specific selection and while loop
    key = "primed"
    while True:
        run = False
        #stdscr.clear()
        stdscr.addstr( 12, 32, "L", curses.A_REVERSE)
        stdscr.addstr( 0,0, f"Main > MIDI > Mixer{stage}")
        if key == "primed": # interpret key inputs
            pass
        elif key == curses.KEY_RIGHT:
            i += 2
        elif key == curses.KEY_LEFT:
            i -= 2
        elif key == ord('\n'):
            run = True

        if i <= 0: # loop
            i = 0
        if i >= 127:
            i = 127

        # for L, level in enumerate(levels):
        #     if i == L:
        #         stdscr.addstr(*pos, str(level), curses.A_REVERSE)
        #     else:
        #         stdscr.addstr(*pos, str(level))
        #     if L == 7:
        #         y,x = 2,0
        #     else:
        #         x += 3

        stdscr.addstr(*pos, format(i,"3d"), curses.A_REVERSE)
        levels[chan] = i
        subprocess.check_output(f"echo 'cc {chan} 7 {i}' | nc -q 0 localhost {PORT}", shell=True)
        # stdscr.addstr(y,x, '   ')
        # stdscr.addstr(y,x, cycle[i], curses.A_REVERSE)
        if run: # wrap run action in conditional
            return

        stdscr.refresh()
        key = stdscr.getch()




def test_callback(message, data):
    print(message)
    match message[0]:
        case [240, 67, 16, 127, 28, 12, 1, 16, 31, 1, 247]:
            pass # undo

        case [240, 67, 16, 127, 28, 12, 1, 16, 39, 1, 247]:
            channel[0] = 0
        case [240, 67, 16, 127, 28, 12, 1, 16, 39, 2, 247]:
            channel[0] = 4
        case [240, 67, 16, 127, 28, 12, 1, 16, 39, 5, 247]:
            channel[0] = 8
        case [240, 67, 16, 127, 28, 12, 1, 16, 39, 6, 247]:
            channel[0] = 12

        case [240, 67, 16, 127, 28, 12, 1, 16, 39, 7, 247]:
            channel[1] = 1
        case [240, 67, 16, 127, 28, 12, 1, 16, 39, 8, 247]:
            channel[1] = 2
        case [240, 67, 16, 127, 28, 12, 1, 16, 39, 8, 247]:
            channel[1] = 3
        case [240, 67, 16, 127, 28, 12, 1, 16, 39, 10, 247]:
            channel[1] = 4

        case [240, 67, 16, 127, 28, 12, 1, 16, 39, 0, 247]:
            save()
            global keep_running
            keep_running = False

    if message[0][:-1] == [176,105] and message[0][-1] != 0:
        chan = sum(channel)
        global levels
        levels[chan-1] = message[0][-1]
        subprocess.check_output(f"echo 'cc {chan-1} 7 {message[0][-1]}' | nc -q 0 localhost {PORT}", shell=True)
        print(f"\rSetting channel {format(chan, '2')} to volume {format(message[0][-1], '3')}", end='')


def load_levels(apply=False):
    global levels
    try:
        with open("current.sav") as current:
            line = "primed"
            while not line.startswith("levels") and line != "":
                line = current.readline()
        if line.startswith("levels"):
            for chan in line.strip().split()[1:]:
                levels.append( int(chan) )
    except:
        pass
    if not levels:
        for i in range(16):
            levels.append(63)
    if apply:
        for chn, val in enumerate(levels):
            print(f"echo 'cc {chn} 7 {val}'")
            subprocess.check_output(f"echo 'cc {chn} 7 {val}' | nc -q 0 localhost {PORT}", shell=True)

def save():
    other_data = []
    try:
        with open("current.sav") as save_file:
            save_data = save_file.readlines()
    except:
        pass
    else:
        for line in save_data:
            if not line.startswith("levels"):
                other_data.append(line)
    save_data = other_data
    save_data.append('levels ' + ' '.join(str(i) for i in levels)+'\n')
    with open("current.sav", 'w') as save_file:
        save_file.writelines(save_data)



if __name__=='__main__':
    wrapper(cursable)
    # seqtrak_in = rtmidi.MidiIn()
    # port_name = "SEQTRAK MIDI"
    # ports = seqtrak_in.get_ports()
    # port_index = next((i for i, name in enumerate(ports) if port_name in name), None)
    # if port_index is not None:
    #     seqtrak_in.open_port(port_index)
    #     load_levels()
    #     seqtrak_in.ignore_types(sysex=False)
    #     seqtrak_in.set_callback(test_callback)


    # print('Fluidsynth mixer is running')

    # try:
    #     while keep_running:
    #         # input()
    #         # channel = -1
    #         # try:
    #         #     ch = int( input('Will mix on channel: ') )
    #         # except:
    #         #     pass
    #         # if not os.path.isfile('.keep_running_daemons'):
    #         #     raise KeyboardInterrupt('doens\'t matter what i type here')
    #         time.sleep(0.5)
    # except KeyboardInterrupt:
    #     print("\nShutting down...")
