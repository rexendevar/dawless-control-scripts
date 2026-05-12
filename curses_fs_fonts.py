import subprocess
PORT = 9988
import os
os.chdir(os.path.dirname(os.path.realpath(__file__))) # set cwd to where the script is

import curses
from curses import wrapper
def concat(*args, sep=' '):
    return sep.join(str(arg) for arg in args)

def list_loaded(show: bool):
    output = subprocess.check_output(f"echo 'fonts' | nc -q 0 localhost {PORT}", shell=True).decode().split('\n')
    fonts = []
    for line in output:
        if line == "ID  Name" or line == '':
            continue
        fonts.append( ((line.strip().split(' ')[0]), line.split('/')[-1], line.strip().split('  ',1)[1]) )
    fonts.reverse()
    loaded: list[str] = []
    for font in fonts:
        if show:
            print(font[0], '\t', font[2])
        loaded.append(font[2])
    return fonts


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
        stdscr.addstr(0,0, f"Main > MIDI > Fnt{stage}")
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
    fonts = list_loaded(False)
    loaded = [font[2] for font in fonts]
    usable_fonts = []
    already_in = []
    tally = 0
    for i in os.walk("./fonts"):
        for file in i[2]:
            name = i[0].strip('./')+'/'+file
            if '.sf' in file.lower():
                if not name in loaded:
                    usable_fonts.append(i[0].strip('./')+'/'+file)
                    tally += 1
                else:
                    already_in.append(i[0].strip('./')+'/'+file)
    #print("Available fonts:")
    a_i = []
    for save in already_in:
        a_i.append(f'{ fonts[ loaded.index(save) ][0] } {save}')
    a_i.sort()

    def arbitrary_loop():
        opts = ["Back","View active",*usable_fonts]
        stdscr.addstr(0,0, "Main > MIDI > Fnt")
        sel = select_loop(stdscr, opts, ' > Load', True)
        if sel == 0:
            return
        elif sel == 1:
            looking_at = ["Back",*a_i]
            stdscr.addstr(0,0, "Main > MIDI > Fnt")
            select_loop(stdscr, looking_at, " > View", True)
            return arbitrary_loop()
        else:
            return sel-1

    save = arbitrary_loop()
    if save is None:
        return
    save = usable_fonts[ save-1 ]


    # # for n, font in enumerate(usable_fonts):
    # #     print(n+1,'\t',font)
    # try:
    #     save = usable_fonts[ int(input("Load from save slot: "))-1 ]
    #     #save = ( '/home/spyndling/bigboy4tb/scripts/dawlesspreparation/'+save )
    # except ValueError:
    #     print("\tPlease use a number out of the list i cant be bothered doing error handling")
    return load_font(save)


def load_font(path: str, save:bool=False) -> None:
    output = subprocess.check_output(f"echo 'load \'{path}\'' | nc -q 0 localhost {PORT}", shell=True).decode().split('\n')[0]
    if save:
        save_font(path, output)
    return output.replace('loaded SoundFont',path)


def save_font(path: str, log: str) -> None:
    try:
        id = int( log[-1:] )
        print(id)
        with open('current.sav') as current:
            saved = current.readlines()
        fonts = []
        others = []
        for line in saved:
            if line.startswith('font'):
                fonts.append(line)
            else:
                others.append(line)
        fonts.append(f'font {id} {path}\n')
        fonts.sort()
        with open('current.sav','w') as current:
            current.writelines(fonts)
            current.writelines(others)
    except:
        print("\tcrashing")
        return




if __name__ == '__main__':
    bub = wrapper(cursable)
    print(bub)