import shutil
import sys
import os
os.chdir(os.path.dirname(os.path.realpath(__file__))) # set cwd to where the script is
import midiroute, fs_instruments, fs_mutes, fs_fonts, fs_mixer, seer_of_wires, audioroute, sqt_mutes

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
        lvls = 'l' in flags
        if '-' in flags:
            mut = not mut
            smut = not smut
            art = not art
            mrt = not mrt
            insts = not insts
            fnts = not fnts
            lvls = not lvls
    else:
        mut, smut, art, mrt, insts, fnts, lvls = False, True, True, True, True, False, True

    if art:
        seer_of_wires.disconnect_all()
    if mrt:
        # ~ for wire in seer_of_wires.see(True):
            # ~ print('trying to drop', wire)
            # ~ midiroute.route(*wire, 'drop') # type: ignore
        midiroute.disconnect_all()
    if seer_of_wires.fs():
        if insts:
            fs_instruments.reset_insts()
        if mut:
            fs_mutes.multi_mute()
    if lvls:
        fs_mixer.load_levels(True)
    with open(file) as save_file:
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



if __name__ == '__main__':
    flags = []
    save = ''
    if len(sys.argv) > 1:
        if sys.argv[1] == 'c':
            pass
        elif sys.argv[1] != 'current.sav':
            save = (sys.argv[1]+'.sav')
            try:
                shutil.copy( save, "current.sav" )
            except:
                pass
        else:
            save = sys.argv[1]
        if len(sys.argv) > 2:
            flags = [sys.argv[2]]

    if not save:
        saves = []
        for i in os.walk("."):
            for file in i[2]:
                if file.endswith('.sav'):
                    saves.append(i[0]+'/'+file)
        print("Current saves:")
        for n, save_file in enumerate(saves):
            print(n,'\t',save_file)
        try:
            save = saves[ int(input("Load from save slot: "))]
        except ValueError:
            print("\tPlease use a number out of the list i cant be bothered doing error handling")
        else:
            try:
                shutil.copy( save, "current.sav" )
            except shutil.SameFileError:
                pass
    # try:
    load(save, *flags)
    # except:
    #     print("Load failed oh well")
