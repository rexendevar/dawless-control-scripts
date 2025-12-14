import subprocess
import sys
PORT = 9988
import os
os.chdir(os.path.dirname(os.path.realpath(__file__))) # set cwd to where the script is

def save(mutes) -> None:
    other_data = []
    try:
        with open("current.sav") as save_file:
            save_data = save_file.readlines()
    except:
        pass
    else:
        for line in save_data:
            if not line.startswith("mutes"):
                other_data.append(line)
    save_data = other_data
    save_data.append('mutes ' + ' '.join(str(i) for i in mutes)+'\n')
    with open("current.sav", 'w') as save_file:
        save_file.writelines(save_data)


def multi_mute(*muted_channels: int) -> None:
    for chan in range(16):
        subprocess.check_output(f"echo 'cc {chan} 7 127' | nc -q 0 localhost {PORT}", shell=True)
    for chan in muted_channels:
        subprocess.check_output(f"echo 'cc {int(chan)-1} 7 0' | nc -q 0 localhost {PORT}", shell=True)
    print("Muted channels:",muted_channels)


if __name__ == '__main__':
    muted_channels = []
    try:
        with open("current.sav") as current:
            line = "primed"
            while not line.startswith("mutes") and line != "":
                line = current.readline()
        if line.startswith("mutes"):
            for chan in line.split()[1:]:
                muted_channels.append( int(chan) )
    except:
        pass

    for i in range(16):
        if i+1 in muted_channels:
            print(i+1,"<- MUTED")
        else:
            print(i+1)

    if len(sys.argv) == 2:
        channel = int(sys.argv[1])
    else:
        channel = int(input("\nMIDI channel 1-16: "))
    val = 127 * int(channel in muted_channels)
    subprocess.check_output(f"echo 'cc {channel-1} 7 {val}' | nc -q 0 localhost {PORT}", shell=True)
    if channel in muted_channels:
        muted_channels.remove(channel)
        print(f"unmuted {channel}")
    else:
        muted_channels.append(channel)
        print(f"muted {channel}")
    muted_channels.sort()
    save(muted_channels)