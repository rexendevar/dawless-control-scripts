import subprocess
import sys
PORT = 9988
import os
os.chdir(os.path.dirname(os.path.realpath(__file__))) # set cwd to where the script is

import curses
from curses import wrapper
def concat(*args, sep=' '):
    return sep.join(str(arg) for arg in args)

def save(mutes) -> None:
    other_data = []
    try:
        with open("current.sav") as save_file:
            save_data = save_file.readlines()
    except:
        pass
    else:
        for line in save_data:
            if not line.startswith("mutes"):
                other_data.append(line)
    save_data = other_data
    save_data.append('mutes ' + ' '.join(str(i) for i in mutes)+'\n')
    with open("current.sav", 'w') as save_file:
        save_file.writelines(save_data)


def multi_mute(*muted_channels: int) -> None:
    for chan in range(16):
        subprocess.check_output(f"echo 'cc {chan} 7 127' | nc -q 0 localhost {PORT}", shell=True)
    for chan in muted_channels:
        subprocess.check_output(f"echo 'cc {int(chan)-1} 7 0' | nc -q 0 localhost {PORT}", shell=True)
    print("Muted channels:",muted_channels)


def cursable(stdscr):
    curses.start_color()
    bw = curses.color_pair(0) # white on black if we need it
    curses.curs_set(0)
    def display(*args, sep=' '):
        stdscr.addstr( 1,0, concat( *args, sep ) )

    muted_channels = []
    try:
        with open("current.sav") as current:
            line = "primed"
            while not line.startswith("mutes") and line != "":
                line = current.readline()
        if line.startswith("mutes"):
            for chan in line.split()[1:]:
                muted_channels.append( int(chan) )
    except:
        pass

    i = 0 # switch to specific selection and while loop
    key = "primed"

    while True:
        run = False
        stdscr.clear()
        stdscr.addstr( 12, 32, "L", curses.A_REVERSE)
        stdscr.addstr( 0,0, "Main > MIDI > MuteCtrl")
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

        #for i in range(16): # remove for loop
        if i+1 in muted_channels:
            display("Channel ", i+1,"<- MUTED") # switch print for specific addstr
        elif 0 < i+1 <= 16: # limit range
            display("Channel ", i+1)
        else:
            display("Back") # provide alt option

        # if len(sys.argv) == 2: # remove integer input and argv
        #     channel = int(sys.argv[1])
        # else:
        #     channel = int(input("\nMIDI channel 1-16: "))

        if run: # wrap run action in conditional
            if i == 16: #exit
                break

            channel = i+1 # off by one error
            val = 127 * int(channel in muted_channels)
            stdscr.clear() # make way for short messages
            try: # wrap process call to handle errors
                subprocess.check_output(f"echo 'cc {channel-1} 7 {val}' | nc -q 0 localhost {PORT}", shell=True)
            except subprocess.CalledProcessError:
                stdscr.addstr( 1,0, "Process error")
            else:
                if channel in muted_channels:
                    muted_channels.remove(channel)
                    stdscr.addstr( 1,0, f"Unmuted {channel}")
                else:
                    muted_channels.append(channel)
                    stdscr.addstr( 1,0, f"Muted {channel}")
                muted_channels.sort()
                save(muted_channels)

        stdscr.refresh()
        key = stdscr.getch() #refresh in loop, don't handle end feedback separately




if __name__ == '__main__':
    wrapper(cursable)
    '''
    muted_channels = []
    try:
        with open("current.sav") as current:
            line = "primed"
            while not line.startswith("mutes") and line != "":
                line = current.readline()
        if line.startswith("mutes"):
            for chan in line.split()[1:]:
                muted_channels.append( int(chan) )
    except:
        pass

    for i in range(16):
        if i+1 in muted_channels:
            print(i+1,"<- MUTED")
        else:
            print(i+1)

    if len(sys.argv) == 2:
        channel = int(sys.argv[1])
    else:
        channel = int(input("\nMIDI channel 1-16: "))
    val = 127 * int(channel in muted_channels)
    subprocess.check_output(f"echo 'cc {channel-1} 7 {val}' | nc -q 0 localhost {PORT}", shell=True)
    if channel in muted_channels:
        muted_channels.remove(channel)
        print(f"unmuted {channel}")
    else:
        muted_channels.append(channel)
        print(f"muted {channel}")
    muted_channels.sort()
    save(muted_channels)
    '''