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
        binkum.append( (i, i.split(") ",1)[1] ) )

    for n, node in enumerate(binkum):
        print(str(n) + ": " + node[1])
    return binkum

def match_node(direction: str, name: str):
    if "fluid" == name.lower():
        name = "synth input port"
    nodes = list_nodes(direction)
    nodes.sort()
    for node in nodes:
        if "Midi" in node and name.lower() in node.lower():
            return node
    return "nada"

def save(source: str, sink: str, connected: bool) -> None:
    source = source.split( ') ',1 )[1]
    sink = sink.split( ') ',1 )[1]
    if "synth input port" in sink.lower():
        sink = "fluid"
    status_line = f'route ~ {source} ~ {sink}\n'
    with open('current.sav') as current:
        config = current.readlines()
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

def route(source_in:str, sink_in:str, auto:str='') -> None:
    source = match_node("-o", source_in)
    sink = match_node("-i", sink_in)
    bad_source = source == 'nada'
    bad_sink = sink == 'nada'
    # todo write proper error feedback
    try:
        source_name = source.split( ') ',1 )[1]
        sink_name = sink.split( ') ' ,1)[1]
    except:
        if bad_source and bad_sink:
            print(f"Source {source_in} and sink {sink_in} are both bad")
        elif bad_source:
            print(f"Cannot find source {source_in}")
        elif bad_sink:
            print(f"Cannot find sink {sink_in}")
        else:
            print("Really bizarre error")
    else:
        log = ""
        if auto == 'connect':
            log = subprocess.check_output(['pw-link', source, sink], stderr=subprocess.STDOUT).decode()
            print(f"Connected {source.split( ') ' ,1)[1]} -> {sink.split( ') ' ,1)[1]}")

        elif auto == 'drop':
            subprocess.check_output(['pw-link', '-d', source, sink])
            print(f"Disconnected {source.split( ') ' ,1)[1]} -> {sink.split( ') ' ,1)[1]}")

        else:
            try:
                log = subprocess.check_output(['pw-link', source, sink], stderr=subprocess.STDOUT).decode()
                print(f"Connected {source.split( ') ' ,1)[1]} -> {sink.split( ') ' ,1)[1]}")
                save(source, sink, True)
            except subprocess.CalledProcessError:
                subprocess.check_output(['pw-link', '-d', source, sink])
                print(f"Disconnected {source.split( ') ' ,1)[1]} -> {sink.split( ') ' ,1)[1]}")
                save(source, sink, False)


if __name__ == '__main__':
    if len(sys.argv) >= 3:
        auto = ''
        if len(sys.argv) == 4:
            auto = sys.argv[3]
        route(sys.argv[1],sys.argv[2],auto)
    else:
        wires = seer_of_wires.see(True)
        if wires:
            print("Active connections:")
            for wire in wires:
                print('   ' + wire)
        print("MIDI Sources:")
        sources = get_nodes('-o')
        source_num = int(input("Run from source #: "))
        print("\nMIDI Sinks:")
        sinks = get_nodes('-i')
        sink_num = int(input("Run to sink #: "))
        try:
            output = subprocess.check_output(['pw-link', sources[source_num][0], sinks[sink_num][0]])
            if output != b'':
                print(output.decode())
            print("Nodes connected")
            save(sources[source_num][0], sinks[sink_num][0], True)
        except subprocess.CalledProcessError:
            output = subprocess.check_output(['pw-link', '-d', sources[source_num][0], sinks[sink_num][0]])
            if output != b'':
                print(output)
            print("Nodes disconnected")
            save(sources[source_num][0], sinks[sink_num][0], False)