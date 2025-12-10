import subprocess
PORT = 9988
import os
os.chdir(os.path.dirname(os.path.realpath(__file__))) # set cwd to where the script is
import fs_fonts


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


def try_search(options: list):
    insts = get_inst_list(False, font_id)
    search = input("Enter instrument: ")
    try:
        search_num = int(search)
        # fail on purpose if int is larger than list
        grinch = 1 / max(len(options)-search_num, 0)
    except:
        options = []
        if not search:
            for n, inst in enumerate(insts):
                options.append(inst)
                print(n,inst)
        else:
            #alias a bunch of em
            count = 0
            opts_list = []
            for inst in insts:
                if search.lower() in inst.lower():
                    options.append(inst)
                    opts_list.append((count,inst))
                    print(count, inst)
                    count += 1
        if len(options) == 1:
            select(options[0])
        else:
            try_search(options)
    else:
        select(options[search_num])


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



def select(instrument: str):
    insts: dict[str,list[str]] = get_inst_list(False, font_id) # type: ignore
    print(f"Switching to {instrument}")
    sel = insts[instrument]
    output = subprocess.check_output(f"echo 'select {channel-1} {font_id} {sel[0]} {sel[1]}' | nc -q 0 localhost {PORT}", shell=True)
    if output != b'':
        print( output )
    save_inst(sel)
    save_chan(channel)
    save_font(font_id)


def save_inst(sel: list[str]) -> None:
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


if __name__ == '__main__':
    try:
        channel = int(input("MIDI channel 1-16: "))
    except:
        channel = get_recent_channel()
        print("Using channel", channel)
    fonts = fs_fonts.list_loaded(True)
    try:
        font_id = int(input("Soundfont from list: "))
    except:
        font_id = get_recent_font()
        print("Using font", font_id)
    insts = get_inst_list(False, font_id)
    search = input("Enter instrument: ")
    options = []
    if not search:
        for n, inst in enumerate(insts):
            options.append(inst)
            print(n,inst)
    else:
        #alias a bunch of em
        count = 0
        opts_list = []
        for inst in insts:
            if search.lower() in inst.lower():
                options.append(inst)
                opts_list.append((count,inst))
                print(count, inst)
                count += 1
    if len(options) == 1:
        select(options[0])
    else:
        try_search(options)