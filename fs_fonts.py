import subprocess
PORT = 9988
import os
os.chdir(os.path.dirname(os.path.realpath(__file__))) # set cwd to where the script is

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


def pick_font() -> None:
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
    print("Available fonts:")
    a_i = []
    for save in already_in:
        a_i.append(f'--> { fonts[ loaded.index(save) ][0] }\t{save}')
    a_i.sort()
    for save in a_i:
        print(save)
    for n, font in enumerate(usable_fonts):
        print(n+1,'\t',font)
    try:
        save = usable_fonts[ int(input("Load from save slot: "))-1 ]
        #save = ( '/home/spyndling/bigboy4tb/scripts/dawlesspreparation/'+save )
    except ValueError:
        print("Please use a number out of the list i cant be bothered doing error handling")
    load_font(save)


def load_font(path: str, save:bool=False) -> None:
    output = subprocess.check_output(f"echo 'load \'{path}\'' | nc -q 0 localhost {PORT}", shell=True).decode().split('\n')[0]
    print(output.replace('loaded SoundFont',path))
    if save:
        save_font(path, output)


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
        print("crashing")
        return




if __name__ == '__main__':
    pick_font()