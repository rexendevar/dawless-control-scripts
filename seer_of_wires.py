import subprocess
import os
os.chdir(os.path.dirname(os.path.realpath(__file__))) # set cwd to where the script is
import json


MONITOR = False

def see(sane: bool = False) -> list[str]:
    try:
        data = subprocess.check_output('pw-link -l | grep Midi', shell=True).decode().split('\n')
    except subprocess.CalledProcessError:
        data = []

    for i, line in enumerate(data):
        if '|<-' in line:
            data[i] = ''
            data[i-1] = ''
        elif '|->' in line:
            data[i] = ' ~ ' + line.split(   ":(playback"   ,1)[1].split(' ',1)[1]
            if 'Synth input port' in data[i]:
                data[i] = " ~ fluid"
        elif line != '' and "capture" in line:
            data[i] = line.split(   ":(capture"   ,1)[1].split(' ',1)[1]
    while '' in data:
        data.remove('')

    last_source = ''
    for i, line in enumerate(data):
        if not line.startswith(' ~ '):
            last_source = line
            data[i] = ''
        else:
            if sane:
                line = line[3:]
                data[i] = last_source + ' -> ' + line
            else:
                data[i] = 'route ~ ' + last_source + line
    while '' in data:
        data.remove('')

    return data

def fs() -> bool:
    try:
        output = subprocess.check_output('pgrep fluidsynth',shell=True)
        return True
    except:
        return False



def read_dump() -> dict:
    result = subprocess.check_output('pw-dump', shell=True).decode()
    data = json.loads(result)

    nodes = {}

    for obj in data:
        if obj.get('type') == 'PipeWire:Interface:Node':
            props = obj.get('info', {}).get('props', {})
            # if props.get('node.description',''):
            #     name = props.get('node.description','')
            if props.get('node.nick', ''):
                name = props.get('node.nick', '')
            else:
                name = props.get('node.name', '')
            nodes[ obj['id'] ] = {
                'name': name,
                'hardware': bool(props.get('alsa.name', '')),
                'source_sink': '',
                'connections': set(),
                'ports': {}
            }

    # Find ports for this node
    for obj in data:
        if obj.get('type') == 'PipeWire:Interface:Port':
            props = obj.get('info', {}).get('props', {})
            node = props.get('node.id')
            if 'monitor' in props.get('port.name').lower() and not MONITOR:
                #print(f"won't attach port {props.get('port.name')} to node {nodes[node]['name']}")
                continue
            nodes[node]['ports'][obj['id']] = {
                'name': props.get('port.name'),
                'direction': props.get('port.direction'),
                'connections': {}
            }

    for node in nodes:
        source_sink = [False, False]
        for port_id in nodes[node]['ports']:
            port = nodes[node]['ports'][port_id]
            if 'monitor' in port['name'].lower() and not MONITOR:
                continue
            if port['direction'] == 'in':
                source_sink[1] = True
            elif port['direction'] == 'out':
                source_sink[0] = True

            if ") " in port['name']:
                port['name'] = port['name'].split(') ',1)[1]
            if "Synth input port" in port['name']:
                port['name'] = "Fluidsynth"
        match source_sink:
            case [False, False]:
                nodes[node]['source_sink'] = 'XXX'
            case [True, False]:
                nodes[node]['source_sink'] = 'SRC'
            case [False, True]:
                nodes[node]['source_sink'] = 'SNK'
            case [True, True]:
                nodes[node]['source_sink'] = 'S&S'

    for obj in data:
        if obj.get('type') == 'PipeWire:Interface:Link':
            props = obj.get('info', {})
            node_in = props.get('input-node-id')
            port_in = props.get('input-port-id')
            node_out = props.get('output-node-id')
            port_out = props.get('output-port-id')
            try:
                nodes[node_in]['ports'][port_in]['connections'][node_out].append(port_out)
            except:
                nodes[node_in]['ports'][port_in]['connections'][node_out] = [port_out]
            nodes[node_in]['connections'].add(node_out)
            try:
                nodes[node_out]['ports'][port_out]['connections'][node_in].append(port_in)
            except:
                nodes[node_out]['ports'][port_out]['connections'][node_in] = [port_in]
            nodes[node_out]['connections'].add(node_in)

    return nodes



def disconnect_all(src: int=-1, snk: int=-1):
    result = subprocess.check_output('pw-dump', shell=True).decode()
    data = json.loads(result)
    for obj in data:
        if obj.get('type') == 'PipeWire:Interface:Link':
            if src != -1 and snk != -1:
                if obj.get('info', {}).get('output-node-id','') == src and obj.get('info', {}).get('input-node-id','') == snk:
                    subprocess.call(f"pw-link -d {obj['id']}",shell=True)
            else:
                subprocess.call(f"pw-link -d {obj['id']}",shell=True)



def show_hw():
    nodes = read_dump()
    hw = []
    for id in nodes:
        node = nodes[id]
        if node['hardware']:
            hw.append(node['name']+nodes[id]['source_sink'])

    for line in hw:
        print(line)
