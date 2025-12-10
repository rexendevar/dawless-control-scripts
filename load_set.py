import shutil
import sys
import os
os.chdir(os.path.dirname(os.path.realpath(__file__))) # set cwd to where the script is
import midiroute, fs_instruments, fs_mutes, fs_fonts, seer_of_wires, audioroute

def load(file: str) -> None:
    line = "primed"
    seer_of_wires.disconnect_all()
    if seer_of_wires.fs():
        fs_instruments.reset_insts()
        fs_mutes.multi_mute()
    with open(file) as save_file:
        while line != "":
            line = save_file.readline()
            if line.startswith("font") and seer_of_wires.fs():
                path = line.split(' ',2)[2].strip()
                fs_fonts.load_font(path, False)
            if line.startswith("inst") and seer_of_wires.fs():
                chan, fnt, bnk, prg = line.split(' ',1)[1].strip().split()
                fs_instruments.set_inst(int(chan), int(bnk), int(prg), int(fnt))
            elif line.startswith("mutes") and seer_of_wires.fs():
                muted_channels: list = line.strip().split(' ')[1:]
                for n, i in enumerate(muted_channels):
                    muted_channels[n] = int(i)
                fs_mutes.multi_mute(*muted_channels)
            elif line.startswith("route"):
                args = line.strip().split(' ~ ')[1:]
                midiroute.route(args[0],args[1],"connect")
            elif line.startswith("art"):
                args = line.strip().split(' ~ ')[1:]
                audioroute.link_prescribed(args[0],args[1])



if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] != 'current.sav':
            save = (sys.argv[1]+'.sav')
            try:
                shutil.copy( save, "current.sav" )
            except:
                pass
        else:
            save = sys.argv[1]
    else:
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
            print("Please use a number out of the list i cant be bothered doing error handling")
        else:
            try:
                shutil.copy( save, "current.sav" )
            except shutil.SameFileError:
                pass
    # try:
    load(save)
    # except:
    #     print("Load failed oh well")