import curses
import subprocess
import time
import os
os.chdir(os.path.dirname(os.path.realpath(__file__))) # set cwd to where the script is

def main(stdscr):
    # List of scripts to run

    menu_fs = [
        # HANDLE FS NOT RUNNING
        {"name": "Fluidsynth status", "cmd": "./check_fluidsynth.sh", "sl": True}, # GOOD
        {"name": "Toggle Fluidsynth", "cmd": "./toggle_fluidsynth.sh", "sl": True}, # GOOD
        {"name": "FS Instruments", "cmd": "python3 curses_fs_instruments.py", "sl": True}, # GOOD
        {"name": "FS Soundfonts", "cmd": "python3 curses_fs_fonts.py", "sl": True}, # GOOD
        {"name": "FS Mixer", "cmd": "python3 curses_fs_mixer.py", "sl": False}, # GOOD
        {"name": "FS mute control", "cmd": "python3 curses_fs_mutes.py", "sl": False}, # FIX ZEROS
        {"name": "SQT muter control", "cmd": "python3 curses_sqt_mutes.py", "sl": False}, # GOOD
        {"name": "Back", "cmd": "main"}
    ]

    menu_routing = [
        {"name": "MIDI routing", "cmd": "python3 curses_midiroute.py", "sl": True}, # NEEDS TESTING
        {"name": "Audio routing", "cmd": "python3 curses_audioroute.py", "sl": False}, # NEEDS TON OF WORK
        {"name": "Back", "cmd": "main"}
    ]

    menu_ap = [ # REMOVED: bug in NIC means starting the access point again is impossible
        {"name": "Back to wifi", "cmd": "sudo accesspopup", "sl": True}, # NEEDS TESTING
        {"name": "Start AP", "cmd": "\
            sudo systemctl stop NetworkManager && \
            sudo modprobe -r brcmfmac_wcc && \
            sudo modprobe -r brcmfmac && \
            sudo modprobe brcmfmac && \
            sudo modprobe brcmfmac_wcc && \
            sudo systemctl start NetworkManager && \
            sudo accesspopup -a", "sl": True}, # NEEDS TESTING
        {"name": "Back", "cmd": "sys", "path": "Sys"},
    ]

    menu_dm = [
        {"name": "Toggle LoChord & SyxT", "cmd": "./daemons.sh", "sl": True}, # GOOD
        {"name": "LoChord/SyxT log", "cmd": "python3 curses_dlog.py", "sl": False}, # GOOD
        {"name": "Toggle SQT muter", "cmd": "./toggle_sqtmuter.sh", "sl": True}, # GOOD
        {"name": "Toggle Reaper", "cmd": "./toggle_reaper.sh", "sl": True}, # GOOD
        {"name": "Reaper log", "cmd": "python3 curses_rlog.py", "sl": False}, # GOOD
        {"name": "Back", "cmd": "main"}
    ]

    menu_sets = [
        {"name": "Load set", "cmd": "python3 curses_load_set.py", "sl": True}, # ADD LEVELS
        {"name": "Save set", "cmd": "python3 curses_save_set.py", "sl": True}, # GOOD
        {"name": "Set log", "cmd": "python3 curses_slog.py", "sl": False},
        {"name": "Back", "cmd": "main"}
    ]

    menu_sys = [
        {"name": "Brightness", "cmd": "python3 curses_brightness.py", "sl": False}, # GOOD
        {"name": "Back to wifi", "cmd": "sudo accesspopup", "sl": True},
        {"name": "Reboot", "cmd": "python3 curses_reboot.py", "sl": False}, # GOOD
        {"name": "Back", "cmd": "main"}
    ]

    scripts = [
        {"name": "Routing...", "cmd": menu_routing, "path": "Rt"},
        {"name": "MIDI...", "cmd": menu_fs, "path": "MIDI"},
        {"name": "Daemons...", "cmd": menu_dm, "path": "Dmn"}, # GOOD
        {"name": "Sets...", "cmd": menu_sets, "path": "Sets"},
        {"name": "System...", "cmd": menu_sys, "path": "Sys"},
        {"name": "PANIC", "cmd": "python3 curses_panic.py", "sl": False},

        #{"name": "Exit", "cmd": None}
    ]



    menu = scripts

    current_index = 0

    # Curses setup
    curses.curs_set(0)  # Hide cursor
    path = "Main"

    while True:
        stdscr.clear()

        # Draw title
        # stdscr.addstr(0, 0, "=== Script Launcher ===", curses.A_BOLD)
        # stdscr.addstr(1, 0, "")

        # Draw menu
        stdscr.addstr(12,32,"L",curses.A_REVERSE)
        stdscr.addstr(0, 0, path)
        for i, script in enumerate(menu):
            if i == current_index:
                stdscr.addstr(i+1, 0, f"> {script['name']}", curses.A_REVERSE)
            else:
                stdscr.addstr(i+1, 0, f"  {script['name']}")

        # # Instructions
        # stdscr.addstr(len(menu) + 3, 0, "")
        # stdscr.addstr(len(menu) + 4, 0, "L/R: Navigate | ENTER: Run | q: Quit")

        stdscr.refresh()

        # Get input
        key = stdscr.getch()

        if key == curses.KEY_LEFT:
            current_index = (current_index - 1) % len(menu)
        elif key == curses.KEY_RIGHT:
            current_index = (current_index + 1) % len(menu)
        elif key == ord('\n'):  # Enter key
            selected = menu[current_index]

            key = "reset"
            current_index = 0

            if selected['cmd'] == "sys":
                selected['cmd'] = menu_sys

            if selected['cmd'] is None:  # Exit option
                break
            elif type(selected['cmd']) == list:
                menu = selected['cmd']
                current_index = 0
                path = "Main > " + selected["path"]
                continue
            elif selected['cmd'] == "main":
                menu = scripts
                current_index = 0
                path = "Main"
                continue

            # Exit curses temporarily
            curses.endwin()
            os.system("clear")

            # Run the script
            #print(f"\nRunning: {selected['name']}\n")
            subprocess.run(selected['cmd'], shell=True)

            #input("\nPress ENTER to return to menu...")
            # Restart curses
            if selected["sl"]:
                time.sleep(1)
            stdscr = curses.initscr()
            curses.noecho()
            curses.cbreak()
            stdscr.keypad(True)
            curses.curs_set(0)

        elif key == ord('q'):
            break

if __name__ == "__main__":
    curses.wrapper(main)
