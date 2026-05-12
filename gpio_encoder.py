from gpiozero import Button, RotaryEncoder
from signal import pause
import subprocess
from evdev import uinput, ecodes as e
import os
os.chdir(os.path.dirname(os.path.realpath(__file__))) # set cwd to where the script is
import time

with uinput.UInput() as ui:
    last_lr = 0
    last_enter = time.time()
    last_enc = time.time()
    def left_right():
        
        global last_lr, last_enc
        now_enc = time.time()
        if now_enc-last_enc < 0.05:
            return
        if l_r.steps < last_lr:
            ui.write(e.EV_KEY, e.KEY_LEFT, 1)
            ui.write(e.EV_KEY, e.KEY_LEFT, 0)
            ui.syn()
        else:
            ui.write(e.EV_KEY, e.KEY_RIGHT, 1)
            ui.write(e.EV_KEY, e.KEY_RIGHT, 0)
            ui.syn()
        last_lr = l_r.steps
        last_enc = now_enc

    def enter():
        global last_lr, last_enter
        now_enter = time.time()
        #print(now_enter - last_enter)
        if now_enter - last_enter < 0.5:
            return
        last_enter = now_enter
        ui.write(e.EV_KEY, e.KEY_ENTER, 1)
        ui.write(e.EV_KEY, e.KEY_ENTER, 0)
        ui.syn()
        l_r.steps = 0
        last_lr = 0
        
    def rl_curses():
        ui.write(e.EV_KEY, e.KEY_LEFTCTRL, 1)
        ui.write(e.EV_KEY, e.KEY_C, 1)
        ui.write(e.EV_KEY, e.KEY_LEFTCTRL, 0)
        ui.write(e.EV_KEY, e.KEY_C, 0)
        ui.syn()
        time.sleep(0.5)
        ui.write(e.EV_KEY, e.KEY_C, 1)
        ui.write(e.EV_KEY, e.KEY_C, 0)
        ui.write(e.EV_KEY, e.KEY_U, 1)
        ui.write(e.EV_KEY, e.KEY_U, 0)
        ui.write(e.EV_KEY, e.KEY_R, 1)
        ui.write(e.EV_KEY, e.KEY_R, 0)
        ui.write(e.EV_KEY, e.KEY_S, 1)
        ui.write(e.EV_KEY, e.KEY_S, 0)
        ui.write(e.EV_KEY, e.KEY_E, 1)
        ui.write(e.EV_KEY, e.KEY_E, 0)
        ui.write(e.EV_KEY, e.KEY_S, 1)
        ui.write(e.EV_KEY, e.KEY_S, 0)
        ui.write(e.EV_KEY, e.KEY_ENTER, 1)
        ui.write(e.EV_KEY, e.KEY_ENTER, 0)
        ui.syn()
    
    def reload():
        subprocess.run("./reload_screen.sh",shell=True)
        

    clicker = Button(24)
    screenload = Button(27)
    curseload = Button(23)
    l_r = RotaryEncoder(20, 19, wrap=True, max_steps=180)
    l_r.steps = 0


    clicker.when_pressed = enter
    l_r.when_rotated = left_right
    screenload.when_pressed = reload
    curseload.when_pressed = rl_curses
    pause()
