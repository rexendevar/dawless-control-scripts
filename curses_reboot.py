import shutil
import sys
import os
os.chdir(os.path.dirname(os.path.realpath(__file__))) # set cwd to where the script is
import subprocess


import curses
from curses import wrapper
def concat(*args, sep=' '):
    return sep.join(str(arg) for arg in args)
    

def cursable(stdscr):
    curses.start_color()
    bw = curses.color_pair(0) # white on black if we need it
    curses.init_pair(1, 0, 1)
    yeloblack = curses.color_pair(1)
    curses.curs_set(0)
    n=0

    def display(*args, sep=' '):
        stdscr.addstr( 1,0, concat( *args, sep ) )

    sel = 0
    key = "primed"
    while True:
        run = False
        stdscr.clear()
        stdscr.addstr( 0,0, "Main > Sys > Reboot")
        if key == "primed": # interpret key inputs
            pass
        elif key == curses.KEY_RIGHT:
            sel += 1
        elif key == curses.KEY_LEFT:
            sel -= 1
        elif key == ord('\n'):
            run = True

        if sel < 0: # loop
            sel = 1
        if sel > 1:
            sel = 0

        if sel == 0:
            stdscr.addstr( 1,0, "Back" )
        elif sel == 1:
            stdscr.addstr( 1,0, "Confirm reboot", yeloblack )

        if run:
            if sel == 1:
                subprocess.run("sudo systemctl reboot",shell=True)
            return

        stdscr.refresh()
        key = stdscr.getch() #refresh in loop, don't handle end feedback separately

 


if __name__ == '__main__':
    wrapper(cursable)
