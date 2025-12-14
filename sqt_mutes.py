import subprocess
import sys
PORT = 9988
import os
os.chdir(os.path.dirname(os.path.realpath(__file__))) # set cwd to where the script is
import time

pipe = '.sqtmute_instructions'
out = '.sqtmute_output'

def save(mutes) -> None:
    other_data = []
    try:
        with open("current.sav") as save_file:
            save_data = save_file.readlines()
    except:
        pass
    else:
        for line in save_data:
            if not line.startswith("sqtmutes"):
                other_data.append(line)
    save_data = other_data
    save_data.append('sqtmutes ' + ' '.join(str(i) for i in mutes)+'\n')
    with open("current.sav", 'w') as save_file:
        save_file.writelines(save_data)

def ensure():
    if not is_running():
        subprocess.check_output("python3 ./muter.py &", shell=True)
        time.sleep(0.5)
        print("Running muter now")

def instruct(inst: str, expect: bool=False) -> str:
    if expect:
        with open(out, 'w'):
            pass
    with open(pipe, 'w') as instructions:
        instructions.write(f'{inst}\n')
    time.sleep(0.3)
    response = ''
    if expect:
        with open(out) as output:
            response = ''.join(output.readlines()).strip()
    return response


def is_running() -> bool:
    output = instruct('s',True).strip()
    return bool(output)

def multi_mute(*muted_channels: int) -> None:
    ensure()
    instruct('a')
    muteline = 't ' + ' '.join(str(chan) for chan in muted_channels)
    print('SQT:',instruct(muteline, True))



if __name__ == '__main__':
    # if not is_running():
    #     print("muter not running")
    #     sys.exit(1)
    ensure()
    muted_channels = []

    try:
        muted_channels = list(int(i) for i in instruct('s',True).split(' ')[1:])
    except:
        muted_channels = []

    for i in range(16):
        if i+1 in muted_channels:
            print(i+1,"<- MUTED")
        else:
            print(i+1)


    print(instruct('t '+input("\nMIDI channels 1-16: "), True))

    try:
        muted_channels = list(int(i) for i in instruct('s',True).split(' ')[1:])
    except:
        muted_channels = []

    muted_channels.sort()
    save(muted_channels)