import sys
import os
os.chdir(os.path.dirname(os.path.realpath(__file__))) # set cwd to where the script is

import time
import textwrap
import threading

import curses
from curses import wrapper
def concat(*args, sep=' '):
    return sep.join(str(arg) for arg in args)

FILE = "/home/flynn/logs/reaper.log"
WIDTH = 32
HEIGHT = 11
log_contents = []

# text = '''This is first paragraph
# This is second paragraph which is also longest
# This is last paragraph'''
# paras = text.splitlines()
# lines = [j for i in paras for j in textwrap.wrap(i,width=25)]
# print(lines)



def detect_file_changes(stdscr, file_path=FILE, interval=0.2):
    last_modified = os.path.getmtime(file_path)
    while threading.main_thread().is_alive():
        current_modified = os.path.getmtime(file_path)
        if current_modified != last_modified:
            read(stdscr)
            last_modified = current_modified
        time.sleep(interval)


def read(stdscr, file = FILE) -> list:
    global log_contents
    with open(file) as log:
        temp_text = log.readlines()
    lines = [j for i in temp_text for j in textwrap.wrap(i,width=WIDTH-1, subsequent_indent=' ')]
    lines_final = [" " + line for line in lines]
    log_contents = lines_final
    update_visual(stdscr, 0)


def update_visual(stdscr, n:int=0):
    stdscr.clear()
    stdscr.addstr(0,0,"Main > Dmn > RLog")
    if n >0 :
        for i, line in enumerate(log_contents[-HEIGHT-n:-n]):
            stdscr.addstr(i+1,0, line)
    else:
        for i, line in enumerate(log_contents[-HEIGHT:]):
            stdscr.addstr(i+1,0, line)
    stdscr.refresh()


def cursable(stdscr):
    curses.curs_set(0)
    read(stdscr)
    background_check = threading.Thread(target=detect_file_changes, args=(stdscr,FILE))
    background_check.start()
    key = "primed"
    sel = 0
    while True:
        run = False
        if key == "primed": # interpret key inputs
            pass
        elif key == curses.KEY_RIGHT:
            sel -= 1
        elif key == curses.KEY_LEFT:
            sel += 1
        elif key == ord('\n'):
            run = True

        if sel < 0:
            sel = 0
        if sel > len(log_contents) - HEIGHT:
            sel = len(log_contents) - HEIGHT

        if run:
            if sel>0:
                sel = 0
                update_visual(stdscr)
            else:
                return
        else:
            update_visual(stdscr, sel)
        key = stdscr.getch()


if __name__ == '__main__':
    #read(stdscr)
    wrapper(cursable)
