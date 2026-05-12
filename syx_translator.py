#!/usr/bin/env python3
"""
Flexible MIDI Message Translator with Templates
"""
import os
os.chdir(os.path.dirname(os.path.realpath(__file__))) # set cwd to where the script is
import rtmidi
import time
import mido
import subprocess

LOG_FILE = 'daemons.log'

if LOG_FILE:
    global print
    def print(*section):
        final = ' '.join( str(sec) for sec in section ) + '\n'
        with open(LOG_FILE, 'a') as log:
            log.write('SYX: ' + final)


STRUCTURES = {
    'TrackPatternSwitch': {
        'syx': [240, 67, 16, 127, 28, 12, 48, 'd1', 15, 'd2', 247],
        'vars_syx': [7,9],
        'ranges_syx': {
            'd1': '80 <= x <= 90'
        },
        'transform_syx': { # transform SYX values to CC - for sysex path
            'd1': 'x + 23' # minus 80, plus 103
        },
        'cc': [191, 'd1', 'd2'],
        'vars_cc': [1,2],
        'ranges_cc': { # check whether CC levels are usable/relevant - for cc path
            'd1': '103 <= x <= 113',
            'd2': '0 <= x <= 5'
        },
        'transform_cc': {
            'd1': 'x - 23'
        },
    },
    'TrackMuteUnmute': {
        'syx': [240, 67, 16, 127, 28, 12, 48, 'd1', 41, 'd2', 247],
        'vars_syx': [7, 9],
        'ranges_syx': {
            'd1': '80 <= x <= 90',
            'd2': 'x==0 or x==125'
        },
        'transform_syx': {
            'd1': 'x - 60'
        },
        'cc': [191, 'd1', 'd2'],
        'vars_cc': [1, 2],
        'ranges_cc': {
            'd1': '20 <= x <= 30',
            'd2': 'x==0 or x==125'
        },
        'transform_cc': {
            'd1': 'x + 60'
        }
    }
}


COMBOS = {
    'SetRecordQuantize': {
        'steps_to_activate': [
            [240, 67, 16, 127, 28, 12, 1, 16, 39, 0, 247], # kick select
            [240, 67, 16, 127, 28, 12, 1, 16, 39, 0, 247], # kick select
            [240, 67, 16, 127, 28, 12, 1, 16, 39, 6, 247], # perc2 select
            [240, 67, 16, 127, 28, 12, 1, 16, 39, 10, 247], # sampler select
            [240, 67, 16, 127, 28, 12, 1, 16, 44, 'x', 247] # sampler pad
        ],
        'var': 9, # we care about this element of the last list
        'transform': ['x_vars.append(min( 5, x ))'], # will run before sending output
        'execute': [240, 67, 16, 127, 28, 12, 00, 00, 0x1f, 'x', 247], # output sysex
        'x_vars': [(0,9)], 
        'known_values': ['off', '1/32', '1/16t', '1/16', '1/8t', '1/8'],
        'ignore': [
            ([240, 67, 16, 127, 28, 12, 1, 16, 40, 'n', 247], 9) # ignore anything in this format where 9 could be anything
        ]
    },
    'TapTempo': {
        'steps_to_activate': [
            [240, 67, 16, 127, 28, 12, 1, 16, 39, 1, 247], # snare select
            [240, 67, 16, 127, 28, 12, 1, 16, 39, 1, 247], # snare select
            [240, 67, 16, 127, 28, 12, 1, 16, 39, 6, 247], # perc2 select
            [240, 67, 16, 127, 28, 12, 1, 16, 39, 10, 247], # sampler select
            [240, 67, 16, 127, 28, 12, 1, 16, 44, 'x', 247], # sampler pad
            [240, 67, 16, 127, 28, 12, 1, 16, 44, 'x', 247], # sampler pad
            [240, 67, 16, 127, 28, 12, 1, 16, 44, 'x', 247], # sampler pad
            [240, 67, 16, 127, 28, 12, 1, 16, 44, 'x', 247], # sampler pad
            [240, 67, 16, 127, 28, 12, 1, 16, 44, 'x', 247], # sampler pad
            [240, 67, 16, 127, 28, 12, 1, 16, 44, 'x', 247], # sampler pad
            [240, 67, 16, 127, 28, 12, 1, 16, 44, 'x', 247], # sampler pad
            [240, 67, 16, 127, 28, 12, 1, 16, 44, 'x', 247], # sampler pad
        ],
        'var': 9,
        'transform': [
            'x_vars.append(time.monotonic() - tempo_tap_start_time)',
            'x_vars[1] = 7 / x_vars[1] * 60',
            'if x_vars[0] == 0: x_vars[1] /= 2', # step 1 to tap eighths
            'if x_vars[0] in [1,2]: x_vars[1] *= .75', # steps 2 & 3 to tap dotted eighths
            'if x_vars[0] in [3,4]: pass', # steps 4 & 5 to tap quarters
            'if x_vars[0] in [5,6]: x_vars[1] *= 1.5', # steps 6 & 7 to tap dotted quarters
            'x_vars[1] = round(x_vars[1])',
            'x_vars.insert(0, min(300, max(5, x_vars[0])))',
            'x_vars[-1] -= 5',
            'x_vars.insert(0, x_vars[-1]//128 )',
            'x_vars.insert(1, x_vars[-1]%128 )'
            ],
        'execute': [240, 67, 16, 127, 28, 12, 0x30, 0x40, 0x76, 'x', 'x', 247],
        'x_vars': [(0,9),(1,10)],
        'ignore': [
            ([240, 67, 16, 127, 28, 12, 1, 16, 40, 'n', 247], 9)
        ]
    },
    'FluidsynthMixer': {
        'steps_to_activate': [
            [240, 67, 16, 127, 28, 12, 1, 16, 24, 1, 247], # project button
            [240, 67, 16, 127, 28, 12, 1, 16, 46, 14, 247], # all knob press
        ],
        'var': 0,
        'transform': [
            'print("transforming")',
            'print(subprocess.check_output("python3 ./fs_mixer.py &", shell=True).decode())',
        ],
        'execute': [],
        'x_vars': [],
        'ignore': [
            (['n', 67, 16, 127, 28, 12, 1, 16, 24, 4, 247],0),
        ]
    },
    'FetchAllPatternStates': {
        'steps_to_activate': [
            [240, 67, 16, 127, 28, 12, 1, 16, 46, 2, 247], # fx knob click - dot
            [240, 67, 16, 127, 28, 12, 1, 16, 46, 3, 247] # fx knob click - fader?
        ],
        'var': 9,
        'transform': [],
        'execute': [
            [240, 0x43, 0x30, 127, 28, 12, 0x30, 0x50, 0x0f, 247], # pattern states
            [240, 0x43, 0x30, 127, 28, 12, 0x30, 0x51, 0x0f, 247],
            [240, 0x43, 0x30, 127, 28, 12, 0x30, 0x52, 0x0f, 247],
            [240, 0x43, 0x30, 127, 28, 12, 0x30, 0x53, 0x0f, 247],
            [240, 0x43, 0x30, 127, 28, 12, 0x30, 0x54, 0x0f, 247],
            [240, 0x43, 0x30, 127, 28, 12, 0x30, 0x55, 0x0f, 247],
            [240, 0x43, 0x30, 127, 28, 12, 0x30, 0x56, 0x0f, 247],
            [240, 0x43, 0x30, 127, 28, 12, 0x30, 0x57, 0x0f, 247],
            [240, 0x43, 0x30, 127, 28, 12, 0x30, 0x58, 0x0f, 247],
            [240, 0x43, 0x30, 127, 28, 12, 0x30, 0x59, 0x0f, 247],
            [240, 0x43, 0x30, 127, 28, 12, 0x30, 0x5a, 0x0f, 247],
            [240, 0x43, 0x30, 127, 28, 12, 0x30, 0x50, 0x29, 247], # mute states
            [240, 0x43, 0x30, 127, 28, 12, 0x30, 0x51, 0x29, 247],
            [240, 0x43, 0x30, 127, 28, 12, 0x30, 0x52, 0x29, 247],
            [240, 0x43, 0x30, 127, 28, 12, 0x30, 0x53, 0x29, 247],
            [240, 0x43, 0x30, 127, 28, 12, 0x30, 0x54, 0x29, 247],
            [240, 0x43, 0x30, 127, 28, 12, 0x30, 0x55, 0x29, 247],
            [240, 0x43, 0x30, 127, 28, 12, 0x30, 0x56, 0x29, 247],
            [240, 0x43, 0x30, 127, 28, 12, 0x30, 0x57, 0x29, 247],
            [240, 0x43, 0x30, 127, 28, 12, 0x30, 0x58, 0x29, 247],
            [240, 0x43, 0x30, 127, 28, 12, 0x30, 0x59, 0x29, 247],
            [240, 0x43, 0x30, 127, 28, 12, 0x30, 0x5a, 0x29, 247]
        ],
        'x_vars': [999],
        'ignore': [
            ([240, 67, 16, 127, 28, 12, 1, 16, 40, 'n', 247], 9)
        ]
    },
    'FetchAllPatternStates2': { # yucky way to do it but this way it doesn't matter which state comes first
        'steps_to_activate': [
            [240, 67, 16, 127, 28, 12, 1, 16, 46, 3, 247], # fx knob click - fader
            [240, 67, 16, 127, 28, 12, 1, 16, 46, 2, 247] # fx knob click - dot
        ],
        'var': 9,
        'transform': [],
        'execute': [
            [240, 0x43, 0x30, 127, 28, 12, 0x30, 0x50, 0x0f, 247], # pattern states
            [240, 0x43, 0x30, 127, 28, 12, 0x30, 0x51, 0x0f, 247],
            [240, 0x43, 0x30, 127, 28, 12, 0x30, 0x52, 0x0f, 247],
            [240, 0x43, 0x30, 127, 28, 12, 0x30, 0x53, 0x0f, 247],
            [240, 0x43, 0x30, 127, 28, 12, 0x30, 0x54, 0x0f, 247],
            [240, 0x43, 0x30, 127, 28, 12, 0x30, 0x55, 0x0f, 247],
            [240, 0x43, 0x30, 127, 28, 12, 0x30, 0x56, 0x0f, 247],
            [240, 0x43, 0x30, 127, 28, 12, 0x30, 0x57, 0x0f, 247],
            [240, 0x43, 0x30, 127, 28, 12, 0x30, 0x58, 0x0f, 247],
            [240, 0x43, 0x30, 127, 28, 12, 0x30, 0x59, 0x0f, 247],
            [240, 0x43, 0x30, 127, 28, 12, 0x30, 0x5a, 0x0f, 247],
            [240, 0x43, 0x30, 127, 28, 12, 0x30, 0x50, 0x29, 247], # mute states
            [240, 0x43, 0x30, 127, 28, 12, 0x30, 0x51, 0x29, 247],
            [240, 0x43, 0x30, 127, 28, 12, 0x30, 0x52, 0x29, 247],
            [240, 0x43, 0x30, 127, 28, 12, 0x30, 0x53, 0x29, 247],
            [240, 0x43, 0x30, 127, 28, 12, 0x30, 0x54, 0x29, 247],
            [240, 0x43, 0x30, 127, 28, 12, 0x30, 0x55, 0x29, 247],
            [240, 0x43, 0x30, 127, 28, 12, 0x30, 0x56, 0x29, 247],
            [240, 0x43, 0x30, 127, 28, 12, 0x30, 0x57, 0x29, 247],
            [240, 0x43, 0x30, 127, 28, 12, 0x30, 0x58, 0x29, 247],
            [240, 0x43, 0x30, 127, 28, 12, 0x30, 0x59, 0x29, 247],
            [240, 0x43, 0x30, 127, 28, 12, 0x30, 0x5a, 0x29, 247]
        ],
        'x_vars': [999],
        'ignore': [
            ([240, 67, 16, 127, 28, 12, 1, 16, 40, 'n', 247], 9)
        ]
    },
}

c_c = ["", 0]
tempo_tap_start_time = 0
def eval_combo(msg: list) -> list | None:
    global c_c
    x_vars = []
    if match_lists2(msg, c_c[0], c_c[1]):
        #print('succeeded with', c_c[0])
        print(c_c[0], 'step', c_c[1], 'of', len(COMBOS[c_c[0]]['steps_to_activate'])-1)
        if c_c[1] == len(COMBOS[c_c[0]]['steps_to_activate'])-1:
            com = COMBOS[c_c[0]]
            x = msg[com['var']]
            x_vars.append(min(5,x))
            #print(x_vars)
            for t in com['transform']:
                #print('trying here')
                exec(t)
            xc = com['execute']
            if type(xc[0]) is not list: # fill in correct output values
                for xv in com['x_vars']:
                    xc[ xv[1] ] = x_vars[ xv[0] ]
                if 'known_values' in com:
                    y = com['known_values'][x_vars[0]]
                else:
                    y = x_vars[-1]
                print('Combo', c_c[0], 'executed with value', y)
            else:
                print("list to deal with")
            c_c = ['', 0]
            return xc # even if it's a list - parse on other end
        elif not should_ignore(msg, c_c[0]):
            if c_c[0] == 'TapTempo' and c_c[1] == 4:
                global tempo_tap_start_time
                tempo_tap_start_time = time.monotonic()
            c_c[1] += 1

    else:
        #print('fiailed with', c_c[0])
        c_c = ['', 0]
        for c in COMBOS:
            com = COMBOS[c]
            if match_lists2(msg, c):
                c_c = [c, 1]
                return None
    return None


def match_lists2(list1: list, entry: str, step: int = 0):
    if not entry in COMBOS:
        return False
    ent = COMBOS[entry]
    compare = ent['steps_to_activate'][step]
    # ~ print('matching list', entry, 'values are', compare, 'against', list1)
    if should_ignore(list1, entry):
        # ~ print(entry, 'ignore')
        return True
    if len(list1) != len(compare):
        # ~ print(entry, 'length mismatch')
        return False

    for n, i in enumerate(compare):
        if isinstance(i, str):
            pass
        else:
            if i != list1[n]:
                # ~ print(entry, 'value mismatch')
                return False
    # ~ print(entry, 'match')
    return True


def match_lists(list1: list, path: str, entry: str):
    # ~ print('trying to match')
    ent = STRUCTURES[entry]
    if path == 'cc':
        compare = ent['cc']
        ranges = ent['ranges_cc']
    elif path == 'syx':
        compare = ent['syx']
        ranges = ent['ranges_syx']

    if len(list1) != len(compare):
        return False

    for n, i in enumerate(compare):
        if isinstance(i, str):
            x = list1[n]
            if i in ranges:
                is_in_range = eval(ranges[i])
                if not is_in_range:
                    return False
        else:
            if i != list1[n]:
                return False
    return True


def should_ignore(list1: list, entry: str):
    for i in COMBOS[entry]['ignore']:
        ltest = list1.copy()
        ltest[ i[1] ] = 'n'
        if ltest == i[0]:
            return True
    return False


def convert_cc_to_syx(msg: list) -> list:
    if not msg[0] == 191:
        return msg
    for s in STRUCTURES:
        if match_lists(msg, 'cc', s):
            print('CC to SYX', s)
            struct = STRUCTURES[s]
            vars_tally = 0
            syx_out = struct['syx'].copy()
            for n, inp in enumerate(struct['cc']):
                if isinstance(inp, str):
                    if inp in struct['transform_cc']:
                        x = msg[n]
                        value = eval( struct['transform_cc'][inp] ) # undo transform
                    else:
                        value = msg[n]
                    syx_out[ struct['vars_syx'][vars_tally] ] = value
                    vars_tally += 1
            # bink = [] # translate to hex
            # for i in syx_out:
            #     bink.append(hex(i))
            # return bink
            return syx_out
    return msg


def convert_syx_to_cc(msg: list, data) -> list:
    if not (msg[0]==240 and msg[-1]==247):
        # not sysex
        # ~ print('not syx',msg)
        return [] # just wire a new connection if u want to record notes
    for s in STRUCTURES:
        # ~ print(s)
        if match_lists(msg, 'syx', s):
            print('SYX to CC', s)
            struct = STRUCTURES[s]
            vars_tally = 0
            cc_out = struct['cc'].copy()
            for n, inp in enumerate(struct['syx']):
                if isinstance(inp, str):
                    if inp in struct['transform_syx']:
                        x = msg[n]
                        value = eval( struct['transform_syx'][inp] ) # apply transform
                    else:
                        value = msg[n]
                    cc_out[ struct['vars_cc'][vars_tally] ] = value
                    vars_tally += 1
            return cc_out
    #print(f'unknown message {msg}') #uncomment this to examine
    combo_check = eval_combo(msg)
    if combo_check:
        seqtrak_out = data['seqtrak_out']
        if type(combo_check[0]) is list:
            for i in combo_check:
                seqtrak_out.send_message(i)
        else:
            seqtrak_out.send_message(combo_check)
    return msg


def ko2_callback(message, data):
    """Handle messages from KO-2"""
    msg, _ = message
    seqtrak_out = data['seqtrak_out']

    result = convert_cc_to_syx(msg)
    seqtrak_out.send_message(result)
    #seqtrak_out.send_message([240, 67, 16, 127, 28, 12, 0x30, 0x4C, 0x16, 0x00, 247])
    return

def seqtrak_callback(message, data):
    """Handle messages from SEQTRAK"""
    # ~ print(message)
    msg, datatime = message
    ko2_out = data['ko2_out']

    result = convert_syx_to_cc(msg, data)
    if result:
        ko2_out.send_message(result)
    return


def test_callback(*data):
    print(data)

# ~ mido.set_backend('mido.backends.rtmidi')

# ~ ko2_in = mido.open_input('SyxTr_KO2_in', virtual=True)
# ~ ko2_out = mido.open_output('SyxTr_KO2_out', virtual=True)
# ~ seqtrak_in = mido.open_input('SyxTr_sqt_in', virtual=True, callback=test_callback)
# ~ seqtrak_out = mido.open_output('SyxTr_sqt_out', virtual=True)

# ~ seqtrak_in._rt.ignore_types(sysex=False, timing=False, active_sense=False)

# ~ print(mido.backend)
# ~ print(mido.backend.module.get_api_names())

# Setup
ko2_in = rtmidi.MidiIn(rtmidi.API_LINUX_ALSA)
ko2_out = rtmidi.MidiOut(rtmidi.API_LINUX_ALSA)
seqtrak_in = rtmidi.MidiIn(rtmidi.API_LINUX_ALSA)
seqtrak_out = rtmidi.MidiOut(rtmidi.API_LINUX_ALSA)


ko2_in.open_virtual_port("SyxT_KO2")
ko2_out.open_virtual_port("SyxT_KO2")
seqtrak_in.open_virtual_port("SyxT_SQT")
seqtrak_out.open_virtual_port("SyxT_SQT")


ko2_in.ignore_types(sysex=False, timing=False)
seqtrak_in.ignore_types(sysex=False, timing=False)

ko2_in.set_callback(ko2_callback, {'seqtrak_out': seqtrak_out})
seqtrak_in.set_callback(seqtrak_callback, {'ko2_out': ko2_out, 'seqtrak_out': seqtrak_out})

print('SyxTranslator is running')

try:
    while True:
        time.sleep(1)
        if not os.path.isfile('.keep_running_daemons'):
            raise KeyboardInterrupt('doens\'t matter what i type here')
except KeyboardInterrupt:
    print("Shutting down...")
except Exception as e:
    print(e)

    # seqtrak_out.send_message([240, 67, 0x30, 127, 28, 12, 0x30, 0x4c, 0x00, 247]) # input mode = 1
    # seqtrak_out.send_message([240, 67, 0x30, 127, 28, 12, 0x30, 0x4c, 0x16, 247]) # output select = 0
    # seqtrak_out.send_message([240, 67, 0x30, 127, 28, 12, 0x00, 0x00, 0x17, 247]) # usb role = 1
