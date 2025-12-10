'''route audio from source to sink'''
import subprocess
import os
os.chdir(os.path.dirname(os.path.realpath(__file__))) # set cwd to where the script is
import seer_of_wires as sor

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
    for id in nodes:
        node = nodes[id]
        if node['source_sink'] in ['SRC','S&S']:
            for nodeid in node['connections']:
                print(
                    node['name'],
                    '-->',
                    nodes[nodeid]['name']
                )
    return nodes


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
    output = subprocess.check_output(f'pw-link {src} {snk}', shell=True)
    if output != b'':
        print(output.decode())
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

def link_nodes():
    nodes = show_wires2()
    print()
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
                print(f'{tally}  ({chans}) {node["name"]}')
            else:
                for port in node['ports']:
                    print(f'{tally}      {node["name"]}.{node["ports"][port]["name"] }')
            tally += 1

    src_sel = -1
    while not (1<= src_sel <= tally):
        try:
            src_sel = int(input("Select source from list: "))
        except ValueError:
            src_sel = -1
    src_id = src_ids[src_sel-1]
    print()

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
                print(f'{tally}  ({chans}) {node["name"]}')
            else:
                for port in node['ports']:
                    print(f'{tally}      {node["name"]}.{node["ports"][port]["name"] }')
            tally += 1

    snk_sel = -1
    while not (1<= snk_sel <= tally):
        try:
            snk_sel = int(input("Select sink from list: "))
        except ValueError:
            snk_sel = -1
    snk_id = snk_ids[snk_sel-1]
    print()


    # equal number of channels
    if len(nodes[src_id]['ports']) == len(nodes[snk_id]['ports']):
        src = []
        for port in nodes[src_id]['ports']:
            src.append(port)
        snk = []
        for port in nodes[snk_id]['ports']:
            snk.append(port)
        tally = 1
        src = [0]
        print("Source channels:")
        for port in nodes[src_id]['ports']:
            if nodes[src_id]['ports'][port]['direction'] == 'out':
                print(f"{hex(tally)[2:]} {nodes[src_id]['ports'][port]['name']}")
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
            mask = input("Enter connection mask (defaults to 123...): ")
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

    # 1 source port
    elif len(nodes[src_id]['ports']) == 1:
        for port in nodes[src_id]['ports']:
            src = port
        snk = []
        for port in nodes[snk_id]['ports']:
            if nodes[snk_id]['ports'][port]['direction'] == 'in':
                print(nodes[snk_id]['ports'][port]['name'])
                snk.append(port)
        mask = ''
        while len(mask) != len(nodes[snk_id]['ports']):
            mask = input("Enter binary connection mask (to sink): ")
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
        print("Source channels:")
        for port in nodes[src_id]['ports']:
            if nodes[src_id]['ports'][port]['direction'] == 'out':
                print(f"{hex(tally)[2:]} {nodes[src_id]['ports'][port]['name']}")
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
    link_nodes()