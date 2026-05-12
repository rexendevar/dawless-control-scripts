import shutil
import sys
import os
os.chdir(os.path.dirname(os.path.realpath(__file__))) # set cwd to where the script is
import midiroute, fs_instruments, fs_mutes, fs_fonts, seer_of_wires, audioroute, sqt_mutes

def load(file: str) -> None:
    line = "primed"
    final = []

    with open(file) as save_file:
        while line != "":
            line = save_file.readline()

            if line.startswith("route"):
                if 'SQTMuter' in line:
                    sqt_mutes.ensure()
                args = line.strip().split(' ~ ')[1:]
                if midiroute.route(args[0],args[1],"clean"):
                    final.append(line)
            elif line == '\n':
                pass
            else:
                final.append(line)

            # ~ elif line.startswith("art") and art:
                # ~ args = line.strip().split(' ~ ')[1:]
                # ~ audioroute.link_prescribed(args[0],args[1])
    with open(file, 'w') as save_file:
        save_file.writelines(final)

if __name__=='__main__':
    load('current.sav')
