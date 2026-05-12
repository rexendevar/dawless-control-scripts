import shutil
import sys
import os
os.chdir(os.path.dirname(os.path.realpath(__file__))) # set cwd to where the script is

import curses
from curses import wrapper
def concat(*args, sep=' '):
    return sep.join(str(arg) for arg in args)


def text_input(stdscr, position: tuple, opts: str) -> str:
    y, x = position[0], position[1]
    final_text = []
    cycle = ["Ent", *opts, "Esc","<X"]

    def choose_char(pos=0):
        i = pos # switch to specific selection and while loop
        key = "primed"
        while True:
            run = False
            #stdscr.clear()
            if key == "primed": # interpret key inputs
                pass
            elif key == curses.KEY_RIGHT:
                i += 1
            elif key == curses.KEY_LEFT:
                i -= 1
            elif key == ord('\n'):
                run = True

            if i < 0: # loop
                i = len(cycle)-1
            if i >= len(cycle):
                i = 0

            stdscr.addstr(y,x, '   ')
            stdscr.addstr(y,x, cycle[i], curses.A_REVERSE)
            if run: # wrap run action in conditional
                return cycle[i],i

            stdscr.refresh()
            key = stdscr.getch() #refresh in loop, don't handle end feedback separately

    next_char, next_pos = choose_char()
    while not next_char in ["Esc", "Ent"]:
        if next_char == "<X":
            try:
                final_text.pop(-1)
                x -= 1
            except:
                pass
        else:
            final_text.append(next_char)
            x += 1
        stdscr.addstr(*position, ''.join(final_text))
        next_char, next_pos = choose_char(next_pos)
    if next_char == "Ent":
        return ''.join(final_text)
    else:
        return ''


# if len(sys.argv) > 1:
#     shutil.copy( "current.sav", ('saves/'+sys.argv[1]+'.sav') )
# else:
#     shutil.copy( "current.sav", ('saves/'+input("Enter save name: ")+'.sav') )

def cursable(stdscr):
    curses.start_color()
    bw = curses.color_pair(0) # white on black if we need it
    curses.curs_set(0)
    def display(*args, sep=' '):
        stdscr.addstr( 1,0, concat( *args, sep ) )
    stdscr.addstr( 0,0, "Main > Sets > Save")
    display("Enter save name:")
    save_name = text_input(stdscr, (2, 0), "abcdefghijklmnopqrstuvwxyz1234567890_")
    if save_name:
        shutil.copy( "current.sav", ('saves/'+save_name+'.sav') )
        return f"saved as saves/{save_name}.sav"
    else:
        return


if __name__ == '__main__':
    output = wrapper(cursable)
    if output:
        print(output)