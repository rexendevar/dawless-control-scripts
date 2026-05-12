import shutil
import sys
import os
os.chdir(os.path.dirname(os.path.realpath(__file__))) # set cwd to where the script is
import midiroute, fs_instruments, fs_mutes, fs_fonts, seer_of_wires, audioroute, sqt_mutes

class Tee:
    def __init__(self, *files):
        self.files = files

    def write(self, obj):
        for f in self.files:
            f.write(obj)
            f.flush()

    def flush(self):
        for f in self.files:
            f.flush()

original_stdout = sys.stdout


import curses
from curses import wrapper
def concat(*args, sep=' '):
    return sep.join(str(arg) for arg in args)

def load(file: str, flags: str='') -> None:
    line = "primed"
    '''
    flags:
    m - mutes
    s - seqtrak mutes
    a - audio routing
    r - midi routing
    i - instruments
    f - fonts
    - disables'''

    if flags:
        mut = 'm' in flags
        smut = 's' in flags
        art = 'a' in flags
        mrt = 'r' in flags
        insts = 'i' in flags
        fnts = 'f' in flags
        if '-' in flags:
            mut = not mut
            smut = not smut
            art = not art
            mrt = not mrt
            insts = not insts
            fnts = not fnts
    else:
        mut, smut, art, mrt, insts, fnts = True, True, True, True, True, False

    if art:
        seer_of_wires.disconnect_all()
    if mrt:
        for wire in seer_of_wires.see(True):
            midiroute.route(*wire, 'drop') # type: ignore
    if seer_of_wires.fs():
        if insts:
            fs_instruments.reset_insts()
        if mut:
            fs_mutes.multi_mute()
    with open(file) as save_file:
        log_file = open("/home/flynn/logs/startup.log", "w")
        sys.stdout = Tee(sys.stdout, log_file)
        while line != "":
            line = save_file.readline()
            if line.startswith("font") and seer_of_wires.fs() and fnts:
                path = line.split(' ',2)[2].strip()
                #print(f"\tNot loading {path} due to the caveats")
                fs_fonts.load_font(path, False)

            if line.startswith("inst") and seer_of_wires.fs() and insts:
                chan, fnt, bnk, prg = line.split(' ',1)[1].strip().split()
                fs_instruments.set_inst(int(chan), int(bnk), int(prg), int(fnt))

            elif line.startswith("mutes") and seer_of_wires.fs() and mut:
                muted_channels: list = line.strip().split(' ')[1:]
                for n, i in enumerate(muted_channels):
                    muted_channels[n] = int(i)
                fs_mutes.multi_mute(*muted_channels)

            elif line.startswith("sqtmutes") and smut:
                sqt_mutes.ensure()
                sqt_mutes.multi_mute( * list(int(i) for i in line.strip().split(' ')[1:]) )

            elif line.startswith("route") and mrt:
                if 'SQTMuter' in line:
                    sqt_mutes.ensure()
                args = line.strip().split(' ~ ')[1:]
                midiroute.route(args[0],args[1],"connect")

            elif line.startswith("art") and art:
                args = line.strip().split(' ~ ')[1:]
                audioroute.link_prescribed(args[0],args[1])
        log_file.close()
        sys.stdout = original_stdout

def cursable(stdscr):
    curses.start_color()
    bw = curses.color_pair(0) # white on black if we need it
    curses.init_pair(1, 0, 3)
    yeloblack = curses.color_pair(1)
    curses.curs_set(0)

    def display(*args, sep=' '):
        stdscr.addstr( 1,0, concat( *args, sep ) )

    saves = []
    for i in os.walk("."):
        for file in i[2]:
            if file.endswith('.sav'):
                saves.append(i[0]+'/'+file)

    sel = 0
    key = "primed"
    while True:
        run = False
        stdscr.clear()
        stdscr.addstr( 0,0, "Main > Sets > Load")
        if key == "primed": # interpret key inputs
            pass
        elif key == curses.KEY_RIGHT:
            sel += 1
        elif key == curses.KEY_LEFT:
            sel -= 1
        elif key == ord('\n'):
            run = True

        if sel < 0: # loop
            sel = len(saves)
        if sel > len(saves):
            sel = 0

        if sel < len(saves):
            display(saves[sel])
        else:
            display("Back")

        if run and sel < len(saves):
            save = saves[sel]
            break
        elif run:
            return False

        stdscr.refresh()
        key = stdscr.getch() #refresh in loop, don't handle end feedback separately

    flags = ['-','m','s','a','r','i','f']
    opts = ["Back ",*flags," Load"]
    selected = ['a','r']
    sel = 0
    key = "primed"
    while True:
        run = False
        stdscr.clear()
        stdscr.addstr( 12, 32, "L", curses.A_REVERSE)
        stdscr.addstr( 0,0, "Main > Sets > Load > Flags")
        if key == "primed": # interpret key inputs
            pass
        elif key == curses.KEY_RIGHT:
            sel += 1
        elif key == curses.KEY_LEFT:
            sel -= 1
        elif key == ord('\n'):
            run = True

        if sel < 0: # loop
            sel = 8
        if sel > 8:
            sel = 0

        stdscr.addstr(1,0, "")
        for n, opt in enumerate(opts):
            if opt in selected:
                attr = yeloblack
            elif opt in flags:
                attr = curses.A_DIM
            else:
                attr = curses.A_NORMAL

            col = curses.A_REVERSE * int(sel==n)

            stdscr.addstr(opt, attr|col)

        if run:
            if sel == 0:
                return False
            elif sel == 8:
                return save, ''.join(selected)
            else:
                if opts[sel] in selected:
                    selected.remove( opts[sel] )
                else:
                    selected.append( opts[sel] )
        # if run and sel < len(saves):
        #     save = saves[sel]
        #     break
        # elif run:
        #     return False

        stdscr.refresh()
        key = stdscr.getch() #refresh in loop, don't handle end feedback separately


if __name__ == '__main__':
    save = wrapper(cursable)
    if save:
        try:
            shutil.copy( save[0], "current.sav" )
        except shutil.SameFileError:
            pass
        load(*save)
