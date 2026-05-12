import shutil
import sys
import os
os.chdir(os.path.dirname(os.path.realpath(__file__))) # set cwd to where the script is
import subprocess


import curses
from curses import wrapper
def concat(*args, sep=' '):
    return sep.join(str(arg) for arg in args)

try:
    with open("brightness.txt") as bt:
        brightness = int(bt.readline().strip())
except FileNotFoundError:
    brightness = 1023

print(brightness)

def save():
    with open("brightness.txt","w") as bt:
        bt.write(str(brightness))

def cursable(stdscr):
    curses.curs_set(0)
    n=0
    global brightness

    def display(*args, sep=' '):
        stdscr.addstr( 1,0, concat( *args, sep ) )

    sel = 0
    key = "primed"
    while True:
        n+=1
        run = False
        stdscr.clear()
        stdscr.addstr( 0,0, "Main > Sys > Brightness")
        if key == "primed": # interpret key inputs
            pass
        elif key == curses.KEY_RIGHT:
            brightness *= 1.1
        elif key == curses.KEY_LEFT:
            brightness /= 1.1
        elif key == ord('\n'):
            run = True
        brightness = int(brightness)

        if brightness < 10: # loop
            brightness = 10
        if brightness > 1023:
            brightness = 1023

        display(f"Brightness = {brightness}/1023")
        subprocess.run(f"gpio -g pwm 18 {brightness}",shell=True)

        if run:
            save()
            return

        stdscr.refresh()
        key = stdscr.getch() #refresh in loop, don't handle end feedback separately




if __name__ == '__main__':
    wrapper(cursable)
