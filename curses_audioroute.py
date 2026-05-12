'''route audio from source to sink'''
import subprocess
import os
os.chdir(os.path.dirname(os.path.realpath(__file__))) # set cwd to where the script is
import seer_of_wires as sor

import curses
from curses import wrapper
def concat(*args, sep=' '):
    return sep.join(str(arg) for arg in args)


def show_wires():
    nodes = sor.read_dump()
    for id in nodes:
        node = nodes[id]
        for portid in node['ports']:
            port = node['ports'][portid]
            if port['direction'] == 'out' and port['connections']:
                for node_out in port['connections']:
                    for port_out in port['connections'][node_out]:
                        print(
                            node['name']+'.'+port['name'],
                            '-->',
                            nodes[node_out]['name']+'.'+nodes[node_out]['ports'][port_out]['name']
                        )
    return nodes


def save(line: str, add: bool) -> None:
    if add:
        with open('current.sav','a') as sav:
            sav.write(line)
    else:
        with open('current.sav') as sav:
            lines = sav.readlines()
        lines.remove(line)
        while '\n' in lines:
            lines.remove('\n')
        with open('current.sav','w') as sav:
            sav.writelines(lines)



def save2(nodes: dict, connect: bool, src_id: int, snk_id: int, srcport: int = 0, snkport: int = 0):
    srcname = nodes[src_id]['name']
    snkname = nodes[snk_id]['name']
    if srcport and snkport:
        srcport = nodes[src_id]['ports'][srcport]['name']
        snkport = nodes[snk_id]['ports'][snkport]['name']
        line = f"art ~ \"{srcname}:{srcport}\" ~ \"{snkname}:{snkport}\"\n"

    if connect:
        with open('current.sav','a') as sav:
            sav.write(line)
    else:
        with open('current.sav') as sav:
            lines = sav.readlines()
        save_lines = []
        if srcport and snkport:
            save_lines = lines
            save_lines.remove(line)
        else:
            for read_line in lines:
                if not (read_line.startswith('art') and srcname in read_line.split(' ~ ')[1] and snkname in read_line.split(' ~ ')[2]):
                    save_lines.append(read_line)
        while '\n' in save_lines:
            save_lines.remove('\n')
        with open('current.sav','w') as sav:
            sav.writelines(save_lines)


def show_wires2():
    nodes = sor.read_dump()
    wires = []
    y = 0
    for id in nodes:
        node = nodes[id]
        if node['source_sink'] in ['SRC','S&S']:
            for nodeid in node['connections']:
                wires.append( concat(
                    node['name'],
                    '-->',
                    nodes[nodeid]['name']
                ))
                y += 1
    return nodes, wires


def connect(src: int, snk: int) -> bool:
    try:
        output = subprocess.check_output(f'pw-link {src} {snk}', shell=True)
        if output != b'':
            print(output.decode())
        return True
    except:
        output = subprocess.check_output(f'pw-link -d {src} {snk}', shell=True)
        if output != b'':
            print(output.decode())
        return False


def disconnect_all():
    output = subprocess.check_output(f'pw-link -d --all', shell=True)
    if output != b'':
        print(output.decode())


def link_prescribed(src: str, snk: str):
    try:
        output = subprocess.check_output(f'pw-link {src} {snk}', shell=True)
        if output != b'':
            print(output.decode())
    except subprocess.CalledProcessError:
        print(f"\tCannot link {src} to {snk}")
    else:
        print(f"Linked {src} to {snk}")


def thex(number: str) -> int:
    match number:
        case 'A':
            return 10
        case 'B':
            return 11
        case 'C':
            return 12
        case 'D':
            return 13
        case 'E':
            return 14
        case 'F':
            return 15
        case _:
            return int(number)


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
        stdscr.addstr( 0,0, f"Main > Rt > Aud{stage}")
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


def text_input(stdscr, position: tuple, opts: list, stage: str='') -> str:
    y, x = position[0], position[1]
    final_text = []
    cycle = ["Ent", *opts, "Esc","<X"]

    def choose_char():
        i = 0 # switch to specific selection and while loop
        key = "primed"
        while True:
            run = False
            #stdscr.clear()
            stdscr.addstr( 12, 32, "L", curses.A_REVERSE)
            stdscr.addstr( 0,0, f"Main > Rt > Aud{stage}")
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

    next_char = choose_char()
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
        next_char = choose_char()
    if next_char == "Ent":
        return ''.join(final_text)
    else:
        return ''

def binary_mask(stdscr, position: tuple, number: int) -> str:
    flags = ["0" * number]
    opts = ["Back ",*flags," Ent"]
    selected = []
    sel = 0
    key = "primed"
    while True:
        run = False
        #stdscr.clear()
        if key == "primed": # interpret key inputs
            pass
        elif key == curses.KEY_RIGHT:
            sel += 1
        elif key == curses.KEY_LEFT:
            sel -= 1
        elif key == ord('\n'):
            run = True

        if sel < 0: # loop
            sel = len(opts)-1
        if sel >= len(opts):
            sel = 0

        stdscr.addstr(position[0], position[1], "")
        for n, opt in enumerate(opts):
            if opt in selected:
                attr = curses.A_BOLD
            elif opt in flags:
                attr = curses.A_DIM
            else:
                attr = curses.A_NORMAL

            col = curses.A_REVERSE * int(sel==n)

            stdscr.addstr(opt, attr|col)

        if run:
            if sel == 0:
                return False # todo handle cancel
            elif sel == len(opts)-1:
                return save, ''.join(selected)
            else:
                opts[sel] = str(int(opts[sel]=="0"))




def cursable(stdscr):
    nodes, wires = show_wires2()

    opts = ["Back","Active wires:",*wires,"Next"]
    sel = select_loop(stdscr, opts)
    while sel not in ["Back","Next"]:
        sel = select_loop(stdscr, opts)
    if sel == "Back":
        return

    sources = []
    tally = 1
    src_ids = []
    src_chans = []
    for id in nodes:
        node = nodes[id]
        if node['source_sink'] in ['SRC','S&S']:
            chans = 0
            for port_id in node['ports']:
                chans += int(node['ports'][port_id]['direction'] == 'out')
            src_ids.append(id)
            src_chans.append(chans)
            if chans>1:
                sources.append(f'{tally}  ({chans}) {node["name"]}')
            else:
                for port in node['ports']:
                    if node['ports'][port]['direction'] == 'out':
                        sources.append(f'{tally}      {node["name"]}.{node["ports"][port]["name"] }')
            tally += 1

    opts = ["Back","Audio sources:",*sources]
    sel = select_loop(stdscr, opts, " > 1 Src", True)
    while sel == 1:
        sel = select_loop(stdscr, opts, " > 1 Src", True)
    if sel == 0:
        cursable(stdscr)
        return
    src_id = src_ids[sel-2]


    sinks = []
    tally = 1
    snk_ids = []
    snk_chans = []
    for id in nodes:
        node = nodes[id]
        if node['source_sink'] in ['SNK','S&S']:
            chans = 0
            for port_id in node['ports']:
                chans += int(node['ports'][port_id]['direction'] == 'in')
            snk_ids.append(id)
            snk_chans.append(chans)
            if chans>1:
                sinks.append(f'{tally}  ({chans}) {node["name"]}')
            else:
                for port in node['ports']:
                    if node['ports'][port]['direction'] == 'in':
                        sinks.append(f'{tally}      {node["name"]}.{node["ports"][port]["name"] }')
            tally += 1

    opts = ["Back","Audio sinks:",*sinks]
    sel = select_loop(stdscr, opts, " > 2 Snk", True)
    while sel == 1:
        sel = select_loop(stdscr, opts, " > 2 Snk", True)
    if sel == 0:
        cursable(stdscr)
        return
    snk_id = snk_ids[sel-2]

    y = 1







    # equal number of channels DONE
    if len(nodes[src_id]['ports']) == len(nodes[snk_id]['ports']):
        src = []
        for port in nodes[src_id]['ports']:
            src.append(port)
        snk = []
        for port in nodes[snk_id]['ports']:
            snk.append(port)
        tally = 1
        src = [0]
        #print("Source channels:")
        stdscr.addstr( y,0, "Source channels:" )
        y += 1
        for port in nodes[src_id]['ports']:
            if nodes[src_id]['ports'][port]['direction'] == 'out':
                stdscr.addstr(y, 0, f"{hex(tally)[2:]} {nodes[src_id]['ports'][port]['name']}")
                y += 1
                src.append(port)
                tally += 1

        y+=1
        snk = []
        for port in nodes[snk_id]['ports']:
            if nodes[snk_id]['ports'][port]['direction'] == 'in':
                stdscr.addstr(y,0,(nodes[snk_id]['ports'][port]['name']))
                snk.append(port)
        mask = ''
        while len(mask) != len(snk):
            stdscr.addstr(y,0,"Connection mask (123...):")
            stdscr.refresh()
            mask = text_input(stdscr, (y+1, 0), (str(n) for n in range(len(snk)+1)) )
            if not mask:
                msk = []
                for n, i in enumerate(snk):
                    msk.append(hex(n+1)[2:])
                mask = ''.join(msk)
            elif mask == '0':
                mask = '0'*len(snk)

        sor.disconnect_all(src_id, snk_id)
        save2(nodes, False, src_id, snk_id)
        con = False
        for n, char in enumerate(mask):
            try:
                digit = int('0x'+char,0)
                if digit == 0:
                    continue
                con = connect( src[digit], snk[n])
                save2(nodes, con, src_id, snk_id, src[digit], snk[n])
            except ValueError:
                pass

        if con:
            print(f"Connected {nodes[src_id]['name']} to {nodes[snk_id]['name']}")
        else:
            print(f"Disconnected {nodes[src_id]['name']} from {nodes[snk_id]['name']}")






    # 1 source port UNTESTABLE i think
    elif len(nodes[src_id]['ports']) == 1:
        for port in nodes[src_id]['ports']:
            src = port
        snk = []
        for port in nodes[snk_id]['ports']:
            if nodes[snk_id]['ports'][port]['direction'] == 'in':
                stdscr.addstr(y, 0, f"{hex(tally)[2:]} {nodes[snk_id]['ports'][port]['name']}")
                y += 1
                snk.append(port)
                tally += 1
        mask = ''
        while len(mask) != len(nodes[snk_id]['ports']):
            #mask = input("Enter binary connection mask (to sink): ")
            mask = binary_mask(stdscr, (y+1,0), len(nodes[snk_id]['ports']))
        snk_final = []
        for n, digit in enumerate(mask):
            if digit == '1':
                snk_final.append(snk[n])
        sor.disconnect_all(src_id, snk_id)
        save2(nodes, False, src_id, snk_id)

        con = False
        for i in snk_final:
            con = connect(src, i)
            save2(nodes, con, src_id, snk_id, src, snk_final[i])
        if con:
            print(f"Connected {nodes[src_id]['name']} to {nodes[snk_id]['name']}")
        else:
            print(f"Disconnected {nodes[src_id]['name']} from {nodes[snk_id]['name']}")







    # 1 sink port
    elif len(nodes[snk_id]['ports']) == 1:
        for port in nodes[snk_id]['ports']:
            snk = port
        src = []
        for port in nodes[src_id]['ports']:
            if nodes[src_id]['ports'][port]['direction'] == 'out':
                print(nodes[src_id]['ports'][port]['name'])
                src.append(port)
        mask = ''
        while len(mask) != len(nodes[src_id]['ports']):
            mask = input("Enter binary connection mask (from source): ")
        src_final = []
        for n, digit in enumerate(mask):
            if digit == '1':
                src_final.append(src[n])
        sor.disconnect_all(src_id, snk_id)
        save2(nodes, False, src_id, snk_id)
        con = False
        for i in src_final:
            con = connect(snk, i)
            save2(nodes, con, src_id, snk_id, src_final[i], snk)
        if con:
            print(f"Connected {nodes[src_id]['name']} to {nodes[snk_id]['name']}")
        else:
            print(f"Disconnected {nodes[src_id]['name']} from {nodes[snk_id]['name']}")








    # arbitrary numbers of both
    else:
        tally = 1
        src = [0]
        stdscr.addstr( y,0, "Source channels:" )
        y += 1
        for port in nodes[src_id]['ports']:
            if nodes[src_id]['ports'][port]['direction'] == 'out':
                stdscr.addstr(y,0, f"{hex(tally)[2:]} {nodes[src_id]['ports'][port]['name']}")
                y += 1
                src.append(port)
                tally += 1
        print()
        

        snk = []
        for port in nodes[snk_id]['ports']:
            if nodes[snk_id]['ports'][port]['direction'] == 'in':
                print(nodes[snk_id]['ports'][port]['name'])
                snk.append(port)
        mask = ''
        while len(mask) != len(snk):
            mask = input("Enter connection mask: ")

        sor.disconnect_all(src_id, snk_id)
        save2(nodes, False, src_id, snk_id)
        con = False
        for n, char in enumerate(mask):
            try:
                digit = int('0x'+char,0)
                if digit == 0:
                    continue
                con = connect( src[digit], snk[n])
                save2(nodes, con, src_id, snk_id, src[digit], snk[n])
            except ValueError:
                pass

        if con:
            print(f"Connected {nodes[src_id]['name']} to {nodes[snk_id]['name']}")
        else:
            print(f"Disconnected {nodes[src_id]['name']} from {nodes[snk_id]['name']}")



if __name__ == '__main__':
    wrapper(cursable)
