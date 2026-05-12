'''route midi from source to sink'''
import subprocess
import sys
import os
os.chdir(os.path.dirname(os.path.realpath(__file__))) # set cwd to where the script is
import seer_of_wires

def list_nodes(direction: str):
    inputs = ""
    for node in subprocess.check_output(['pw-link',direction]).decode():
        inputs = inputs + node
    inputs = inputs.split('\n')
    return inputs

def get_nodes(direction: str):
    inputs = list_nodes(direction)
    midis = []
    for i in inputs:
        if "Midi" in i:
            midis.append(i)

    binkum = []
    for i in midis:
        name = i.split( ':',1 )[1].split( ' (' )[0].split('Client')[-1]
        if "Virtual RawMIDI" in name:
            name = "Reaper Clock"
        binkum.append( (i, name ) )

    for n, node in enumerate(binkum):
        print(str(n) + ": " + node[1])
    return binkum

def show_connections(backend=False):
    bulk_dump = subprocess.check_output('aconnect -l',shell=True).decode().split('\n')
    last_client = -1
    last_port = -1
    clients = {}
    wires = []
    for line in bulk_dump:
        if line == '':
            continue
        elif 'client' in line:
            last_client = line.split('client ',1)[1].split(': ',1)[0]
            clients[last_client] = {}
        elif 'Connecting' in line:
            connections = line.strip().split(': ',1)[1].split(', ')
            clients[last_client][last_port]['connections'] = connections
        elif 'Connected' in line:
            pass
        else:
            last_port = line.strip().split()[0]
            clients[last_client][last_port] = {}
            name = line.split("'")[1].strip()
            if "Virtual RawMIDI" in name:
                name = "Reaper Clock"
            clients[last_client][last_port]['name'] = name
    for c in clients:
        for p in clients[c]:
            if 'connections' not in clients[c][p]:
                continue
            else:
                for cn in clients[c][p]['connections']:
                    c1, p1 = cn.split(':')
                    if backend:
                        if clients[c][p]["name"] not in ['Timer','Announce']:
                            wires.append( (clients[c][p]["name"], clients[c1][p1]["name"]) )
                    else:
                        wires.append(f'{clients[c][p]["name"]} -> {clients[c1][p1]["name"]}')
    return wires

def match_node(direction: str, name: str):
    if "fluid" in name.lower():
        name = "synth input port"
    elif "reaper clock" in name.lower():
        name = "virtual rawmidi"
    # ~ nodes = list_nodes(direction)
    try:
        nodes = subprocess.check_output(f'aconnect {direction} | grep -B1 -i "{name}"', shell=True).decode().split('\n')
        while '' in nodes:
            nodes.remove('')
        if len(nodes) == 2:
            client = nodes[0].split('client ',1)[1].split(': ',1)[0]
            port = nodes[1].split('    ',1)[1].split(' ',1)[0]
            return f'{client}:{port}'
        else:
            return "nada"
    except subprocess.CalledProcessError:
        #print('failing here')
        return "nada"

def save(source: str, sink: str, connected: bool) -> None:
    # ~ source = source.split( ':',1 )[1].split( ' (' )[0]
    # ~ sink = sink.split( ':',1 )[1].split( ' (' )[0]
    if "synth input port" in sink.lower():
        sink = "fluid"
    elif "virtual rawmidi" in sink.lower():
        sink = "reaper clock"
    status_line = f'route ~ {source} ~ {sink}\n'
    with open('current.sav') as current:
        config = current.readlines()
    while '\n' in config:
        config.remove('\n')
    if status_line in config and not connected:
        config.remove(status_line)
        with open('current.sav','w') as current:
            current.writelines(config)
    elif connected and not status_line in config:
        with open('current.sav','w') as current:
            current.writelines(config)
            current.write(status_line)
    else:
        return

def route(source_in:str, sink_in:str, auto:str=''):
    source = match_node("-i", source_in)
    sink = match_node("-o", sink_in)
    bad_source = source == 'nada'
    bad_sink = sink == 'nada'
    # todo write proper error feedback


    if bad_source and bad_sink:
        print(f"\tSource {source_in} and sink {sink_in} are both bad")
    elif bad_source:
        print(f"\tCannot find source {source_in}")
    elif bad_sink:
        print(f"\tCannot find sink {sink_in}")
        
    else:
        log = ""
        if auto == 'connect':
            try:
                log = subprocess.check_output(['aconnect', source, sink], stderr=subprocess.STDOUT).decode()
                print(f"Connected {source_in} -> {sink_in}")
            except subprocess.CalledProcessError:
                print(f"{source_in} -> {sink_in} threw error")

        elif auto == 'drop':
            subprocess.check_output(['aconnect', '-d', source, sink])
            print(f"Disconnected {source_in} -> {sink_in}")

        elif auto == 'clean':
            return not (bad_source or bad_sink)

        else:
            try:
                log = subprocess.check_output(['aconnect', source, sink], stderr=subprocess.STDOUT).decode()
                print(f"Connected {source_name} -> {sink_name}")
                save(source_in, sink_in, True)
            except subprocess.CalledProcessError:
                subprocess.check_output(['aconnect', '-d', source, sink])
                print(f"Disconnected {source_name} -> {sink_name}")
                save(source_in, sink_in, False)

def disconnect_all():
    for conn in show_connections(True):
        route(conn[0],conn[1],'drop')

if __name__ == '__main__':
    if len(sys.argv) >= 3:
        auto = ''
        if len(sys.argv) == 4:
            auto = sys.argv[3]
        route(sys.argv[1],sys.argv[2],auto)
    else:
        wires = show_connections()
        if wires:
            print("Active connections:")
            for wire in wires:
                print(wire)
        print("\nMIDI Sources:")
        sources = get_nodes('-o')
        source_num = int(input("Run from source #: "))
        print("\nMIDI Sinks:")
        sinks = get_nodes('-i')
        sink_num = int(input("Run to sink #: "))
        try:
            #print(sinks[sink_num][1])
            #print(match_node( '-o', sinks[sink_num][1] ))
            output = subprocess.check_output(['aconnect', match_node('-i', sources[source_num][1]), match_node( '-o', sinks[sink_num][1] )  ])
            if output != b'':
                print(output.decode())
            print("Nodes connected")
            save(sources[source_num][1], sinks[sink_num][1], True)
        except subprocess.CalledProcessError:
            output = subprocess.check_output(['aconnect', '-d', match_node('-i', sources[source_num][1]), match_node( '-o', sinks[sink_num][1] ) ])
            if output != b'':
                print(output)
            print("Nodes disconnected")
            save(sources[source_num][1], sinks[sink_num][1], False)
