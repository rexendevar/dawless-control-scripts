import subprocess
PORT = 9988
import os
os.chdir(os.path.dirname(os.path.realpath(__file__))) # set cwd to where the script is
import curses_fs_fonts
import time

import curses
from curses import wrapper
def concat(*args, sep=' '):
    return sep.join(str(arg) for arg in args)

channel = 0


def get_inst_list(basic: bool = False, fnt: int=1) -> list[str]|dict[str,list[str]]:
    instruments = subprocess.check_output(f"echo 'inst {fnt}' | nc -q 0 localhost {PORT}", shell=True).decode().split('\n')
    if basic:
        return instruments
    insts: dict[str,list[str]] = {}
    for inst in instruments:
        if not inst:
            continue
        inst = inst.split(' ',1)
        insts[inst[1]] = inst[0].split('-',1)
    return insts


def try_search(stdscr, options: list, font_id):
    stdscr.clear()
    insts = get_inst_list(False, font_id)
    search = text_input(stdscr, (1,6))
    if search == "cancel":
        cursable(stdscr)
        return

    #search = input("Enter instrument: ")
    options = []
    if not search:
        for n, inst in enumerate(insts):
            options.append(inst)
            #print(n,inst)
        opts = ["Back", "Search", *options]
        sel = select_loop(stdscr, opts, " > 3 Inst", False)
        if sel == "Search":
            try_search(stdscr, options, font_id)
        elif sel == "Back":
            cursable(stdscr)
            return
        else:
            return select(sel, font_id)
    else:
        #alias a bunch of em
        count = 0
        opts_list = []
        for inst in insts:
            if search.lower() in inst.lower():
                options.append(inst)
                opts_list.append((count,inst))
                count += 1
        if len(options) == 1:
            return select(options[0], font_id)
        else:
            opts = ["Back", "Search", *options]
            sel = select_loop(stdscr, opts, " > 3 Inst", False)
            if sel == "Search":
                try_search(stdscr, options, font_id)
            elif sel == "Back":
                cursable(stdscr)
                return
            else:
                return select(sel, font_id)
    # insts = get_inst_list(False, font_id)
    # search = text_input(stdscr, (1,6))
    # if search == "cancel":
    #     cursable(stdscr)
    #     return
    # try:
    #     search_num = int(search)
    #     # fail on purpose if int is larger than list
    #     grinch = 1 / max(len(options)-search_num, 0)
    # except:
    #     options = []
    #     if not search:
    #         for n, inst in enumerate(insts):
    #             options.append(inst)
    #             print(n,inst)
    #     else:
    #         #alias a bunch of em
    #         count = 0
    #         opts_list = []
    #         for inst in insts:
    #             if search.lower() in inst.lower():
    #                 options.append(inst)
    #                 opts_list.append((count,inst))
    #                 print(count, inst)
    #                 count += 1
    #         if len(options) == 1:
    #             select(options[0], font_id)
    #         else:
    #             try_search(stdscr, options, font_id)
    # else:
    #     select(options[search_num], font_id)


def get_recent_channel() -> int:
    try:
        with open("current.sav") as save_file:
            save_data = save_file.readlines()
    except:
        pass
    else:
        for line in save_data:
            if line.startswith("chansel"):
                return int(line.split()[1])
    return 1


def get_recent_font() -> int:
    try:
        with open("current.sav") as save_file:
            save_data = save_file.readlines()
    except:
        pass
    else:
        for line in save_data:
            if line.startswith("fntsel"):
                return int(line.split()[1])
    return 1



def select(instrument: str, font_id):
    insts: dict[str,list[str]] = get_inst_list(False, font_id) # type: ignore
    print(f"Switching to {instrument}")
    sel = insts[instrument]
    try:
        subprocess.check_output(f"echo 'select {channel-1} {font_id} {sel[0]} {sel[1]}' | nc -q 0 localhost {PORT}", shell=True)
    except subprocess.CalledProcessError:
        return "Process error"
    else:
        save_inst(sel, font_id)
        save_chan(channel)
        save_font(font_id)
        return f"Switching channel {channel} to {instrument}"


def save_inst(sel: list[str], font_id) -> None:
    known_instruments = []
    other_data = []
    track = None
    try:
        with open("current.sav") as save_file:
            save_data = save_file.readlines()
    except:
        pass
    else:
        for line in save_data:
            if line.startswith("inst"):
                known_instruments.append(line.split())
            else:
                other_data.append(line)
        for i, inst in enumerate(known_instruments):
            if int(inst[1]) == channel:
                track = i
                break
        if track is not None:
            known_instruments.pop(track)
    known_instruments.append( ["inst", str(channel), str(font_id), str(sel[0]), str(sel[1])] )
    save_data = other_data
    for inst in known_instruments:
        save_data.append(" ".join(inst)+'\n')
    with open("current.sav", 'w') as save_file:
        save_file.writelines(save_data)


def save_chan(sel: int) -> None:
    final_data = []
    try:
        with open("current.sav") as save_file:
            save_data = save_file.readlines()
    except:
        pass
    else:
        for line in save_data:
            if not line.startswith("chansel"):
                final_data.append(line)
    final_data.append( f"chansel {sel}\n" )
    with open("current.sav", 'w') as save_file:
        save_file.writelines(final_data)


def save_font(sel: int) -> None:
    final_data = []
    try:
        with open("current.sav") as save_file:
            save_data = save_file.readlines()
    except:
        pass
    else:
        for line in save_data:
            if not line.startswith("fntsel"):
                final_data.append(line)
    final_data.append( f"fntsel {sel}\n" )
    with open("current.sav", 'w') as save_file:
        save_file.writelines(final_data)


def reset_insts() -> None:
    for channel in range(16):
        subprocess.check_output(f"echo 'select {channel} 1 000 000' | nc -q 0 localhost {PORT}", shell=True)


def find_name(bnk: int, prg: int, fnt: int) -> str:
    instruments = get_inst_list(True, fnt)
    bnkname = format(bnk,"03d")
    prgname = format(prg,"03d")
    for inst in instruments:
        if inst.startswith(f"{bnkname}-{prgname}"):
            return inst.split(' ',1)[1]
    return "This should never happen"




def set_inst(channel: int, bnk: int, prg: int, fnt: int) -> None:
    output = subprocess.check_output(f"echo 'select {channel-1} {fnt} {bnk} {prg}' | nc -q 0 localhost {PORT}", shell=True)
    if output != b'':
        print( output )
    print(f"Set channel {channel} to {find_name(bnk, prg, fnt)}")


def num_input(stdscr, position: tuple, opts: list) -> str:
    y, x = position[0], position[1]
    final_text = []
    cycle = ["Ent", *opts, "Esc"]

    i = 0 # switch to specific selection and while loop
    key = "primed"
    while True:
        run = False
        #stdscr.clear()
        # stdscr.addstr( 12, 32, "L", curses.A_REVERSE)
        # stdscr.addstr( 0,0, f"Main > Sets > Rt > Aud{stage}")
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
            return cycle[i]

        stdscr.refresh()
        key = stdscr.getch() #refresh in loop, don't handle end feedback separately


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
        stdscr.addstr(0,0, f"Main > MIDI > Ins{stage}")
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


def text_input(stdscr, position: tuple) -> str|int:
    y, x = position[0], position[1]
    final_text = []
    cycle = ["Ent", *"abcdefghijklmnopqrstuvwxyz 1234567890 ", "Esc","<X"]
    stdscr.clear()
    def choose_char(pos=0):
        i = pos # switch to specific selection and while loop
        key = "primed"
        while True:
            run = False
            #stdscr.clear()
            stdscr.addstr(0,0, "Main > MIDI > Ins > 3 Inst")
            stdscr.addstr(1,0, "Inst:")
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
    elif next_char == "Esc":
        return 'cancel'


def cursable(stdscr):
    def display(*args, sep=' '):
        stdscr.addstr( 1,0, concat( *args, sep ) )
    stdscr.addstr( 12, 32, "L", curses.A_REVERSE)
    stdscr.addstr(0,0, "Main > MIDI > Ins > 1 Ch  ")
    stdscr.addstr(1,0, "Channel ")
    #8
    global channel
    channel = num_input(stdscr, (1,8), list(str(i+1) for i in range(16)))
    if channel == "Ent":
        channel = get_recent_channel()
        stdscr.addstr(1,0, f"Using channel {channel}")
        stdscr.refresh()
        time.sleep(1)
    elif channel == "Esc":
        return
    else:
        channel = int(channel)

    fonts = curses_fs_fonts.list_loaded(False)
    fonts_show = []
    for i in fonts:
        fonts_show.append(i[2])

    opts = ["Back","Soundfonts:",*fonts_show]
    stdscr.addstr(0,0, "Main > MIDI > Ins > 2 Sft ")
    sel = select_loop(stdscr, opts, " > 2 Sft", True)
    while sel == 1:
        sel = select_loop(stdscr, opts, " > 2 Sft", True)
    if sel == 0:
        cursable(stdscr)
        return
    font_id = sel-1

    stdscr.clear()

    insts = get_inst_list(False, font_id)
    search = text_input(stdscr, (1,6))
    if search == "cancel":
        cursable(stdscr)
        return

    #search = input("Enter instrument: ")
    options = []
    if not search:
        for n, inst in enumerate(insts):
            options.append(inst)
            #print(n,inst)
        opts = ["Back", "Search", *options]
        sel = select_loop(stdscr, opts, " > 3 Inst", False)
        if sel == "Search":
            try_search(stdscr, options, font_id)
        elif sel == "Back":
            cursable(stdscr)
            return
        else:
            return select(sel, font_id)
    else:
        #alias a bunch of em
        count = 0
        opts_list = []
        for inst in insts:
            if search.lower() in inst.lower():
                options.append(inst)
                opts_list.append((count,inst))
                count += 1
        if len(options) == 1:
            return select(options[0], font_id)
        else:
            opts = ["Back", "Search", *options]
            sel = select_loop(stdscr, opts, " > 3 Inst", False)
            if sel == "Search":
                try_search(stdscr, options, font_id)
            elif sel == "Back":
                cursable(stdscr)
                return
            else:
                return select(sel, font_id)


if __name__ == '__main__':
    print(wrapper(cursable))