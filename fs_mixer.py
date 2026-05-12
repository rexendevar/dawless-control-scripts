import os
os.chdir(os.path.dirname(os.path.realpath(__file__))) # set cwd to where the script is
import rtmidi
import time
PORT = 9988
import subprocess

channel = [0,1]
keep_running = True
levels = []
wpctl_id = 0
last_fader = "none"

# [240, 67, 16, 127, 28, 12, 1, 16, 24, 1, 247]
# [240, 67, 16, 127, 28, 12, 1, 16, 46, 14, 247]
# [240, 67, 16, 127, 28, 12, 1, 16, 24, 1, 247] < ignore
# [240, 67, 16, 127, 28, 12, 1, 16, 24, 4, 247]


def test_callback(message, data):
    global levels, last_fader
    match message[0]:
        case [240, 67, 16, 127, 28, 12, 1, 16, 31, 1, 247]:
            pass # undo

        # snare clap perc1 perc2 - select group of 4
        case [240, 67, 16, 127, 28, 12, 1, 16, 39, 1, 247]:
            channel[0] = 0
        case [240, 67, 16, 127, 28, 12, 1, 16, 39, 2, 247]:
            channel[0] = 4
        case [240, 67, 16, 127, 28, 12, 1, 16, 39, 5, 247]:
            channel[0] = 8
        case [240, 67, 16, 127, 28, 12, 1, 16, 39, 6, 247]:
            channel[0] = 12

        # synth1 synth2 dx sampler - select individual channel
        case [240, 67, 16, 127, 28, 12, 1, 16, 39, 7, 247]:
            channel[1] = 1
        case [240, 67, 16, 127, 28, 12, 1, 16, 39, 8, 247]:
            channel[1] = 2
        case [240, 67, 16, 127, 28, 12, 1, 16, 39, 9, 247]:
            channel[1] = 3
        case [240, 67, 16, 127, 28, 12, 1, 16, 39, 10, 247]:
            channel[1] = 4

        # hat - toggle mute on current channel
        case [240, 67, 16, 127, 28, 12, 1, 16, 39, 4, 247]:
            chan = sum(channel)
            if levels[chan-1] < 10:
                volume = 63
                mute = "OFF"
            else:
                volume = 0
                mute = "ON"
            levels[chan-1] = volume
            try:
                subprocess.check_output(f"echo 'cc {chan-1} 7 {volume}' | nc -q 0 localhost {PORT}", shell=True)
                print(f"LVL: Setting channel mute on {format(chan, '2')} to {mute}", flush=True)
            except subprocess.CalledProcessError:
                print("LVL: Error")

        # kick - save and exit
        case [240, 67, 16, 127, 28, 12, 1, 16, 39, 0, 247]:
            save()
            print()
            global keep_running
            keep_running = False

    # highpass fader actual fader (not sysex)
    if message[0][:-1] == [176,105] and message[0][-1] != 0:
        chan = sum(channel)
        levels[chan-1] = message[0][-1]
        if not last_fader=="fs":
            last_fader = "fs"
            print()
        try:
            subprocess.check_output(f"echo 'cc {chan-1} 7 {message[0][-1]}' | nc -q 0 localhost {PORT}", shell=True)
            print(f"LVL: Setting channel {format(chan, '2')} to volume {format(message[0][-1], '3')}", end='\r', flush=True)
        except subprocess.CalledProcessError:
            print("LVL: Error")
        
    # repeater fader controls seqtrak 
    elif message[0][:-1] == [176,106] and message[0][-1] != 0:
        final_volume = round(message[0][-1] / 127 * 1.5,3)
        if not last_fader=="sqt":
            last_fader = "sqt"
            print()
        subprocess.Popen(f"wpctl set-volume {wpctl_id} {final_volume}", shell=True)
        print(f"LVL: Setting SQT volume to {final_volume} (out of 1.5)", end='\r', flush=True)


def load_levels(apply=False):
    global levels
    try:
        with open("current.sav") as current:
            line = "primed"
            while not line.startswith("levels") and line != "":
                line = current.readline()
        if line.startswith("levels"):
            for chan in line.split()[1:]:
                levels.append( int(chan) )
            #print(levels)
    except FileNotFoundError:
        pass
    if not levels:
        for i in range(16):
            levels.append(63)
    if apply:
        for chn, val in enumerate(levels):
            try:
                subprocess.check_output(f"echo 'cc {chn} 7 {val}' | nc -q 0 localhost {PORT}", shell=True)
            except subprocess.CalledProcessError:
                print("LVL: Error")


def save():
    other_data = []
    try:
        with open("current.sav") as save_file:
            save_data = save_file.readlines()
    except:
        pass
    else:
        for line in save_data:
            if not line.startswith("levels"):
                other_data.append(line)
    save_data = other_data
    save_data.append('levels ' + ' '.join(str(i) for i in levels)+'\n')
    with open("current.sav", 'w') as save_file:
        save_file.writelines(save_data)



if __name__=='__main__':
    seqtrak_in = rtmidi.MidiIn()
    port_name = "SEQTRAK MIDI"
    ports = seqtrak_in.get_ports()
    port_index = next((i for i, name in enumerate(ports) if port_name in name), None)
    if port_index is not None:
        seqtrak_in.open_port(port_index)
        load_levels()
        seqtrak_in.ignore_types(sysex=False)
        seqtrak_in.set_callback(test_callback)

    try:
        wpctl_id = int(subprocess.check_output("wpctl status | awk '/SEQTRAK Analog Stereo/{gsub(/\./,\"\",$2); print $2}'", shell=True).decode().strip())
        print(wpctl_id)
    except:
        print("Cannot set audio level properly")
    print('Fluidsynth mixer is running')

    try:
        while keep_running:
            # input()
            # channel = -1
            # try:
            #     ch = int( input('Will mix on channel: ') )
            # except:
            #     pass
            # if not os.path.isfile('.keep_running_daemons'):
            #     raise KeyboardInterrupt('doens\'t matter what i type here')
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nShutting down...")
