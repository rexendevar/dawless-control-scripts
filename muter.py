import sys
import time
import os
os.chdir(os.path.dirname(os.path.realpath(__file__))) # set cwd to where the script is
import threading
from typing import Set
with open('.sqtmute_instructions','w'):
    pass

output = '.sqtmute_output'
def print(out:str):
    with open(output,'a') as log:
        log.write(out+'\n')


try:
    import rtmidi
except ImportError:
    print("Error: python-rtmidi not installed")
    print("Install with: pip install python-rtmidi")
    sys.exit(1)


class MIDIChannelMuter:
    def __init__(self, client_name="SQTMuter"):
        # Create MIDI input and output
        self.midi_in = rtmidi.MidiIn()
        self.midi_out = rtmidi.MidiOut()

        # Open virtual ports
        self.midi_in.open_virtual_port(f"{client_name}_input")
        self.midi_out.open_virtual_port(f"{client_name}_output")

        self.muted_channels: Set[int] = set()
        self.running = True

        # Set up callback for incoming MIDI
        self.midi_in.set_callback(self.midi_callback)

        print(f"Created virtual MIDI ports:")
        print(f"  Input:  {client_name}_input")
        print(f"  Output: {client_name}_output")

    def midi_callback(self, event, data=None):
        """Callback for incoming MIDI messages"""
        message, deltatime = event

        if len(message) == 0:
            return

        # Parse MIDI message
        status = message[0]

        # Check if it's a channel message (128-239)
        if status >= 128 and status < 240:
            channel = status & 0x0F  # Bottom 4 bits = channel (0-15)

            # Skip if channel is muted
            if channel in self.muted_channels:
                return

        # Forward to output
        self.midi_out.send_message(message)

    def mute_channel(self, *channels: int):
        """Mute a MIDI channel (0-15)"""
        for channel in channels:
            if 0 <= channel <= 15:
                self.muted_channels.add(channel)
                print(f"Muted channel {channel + 1} (0x{channel:X})")
            else:
                print(f"Invalid channel: {channel}")

    def unmute_channel(self, *channels: int):
        """Unmute a MIDI channel (0-15)"""
        for channel in channels:
            if 0 <= channel <= 15:
                self.muted_channels.discard(channel)
                print(f"Unmuted channel {channel + 1} (0x{channel:X})")
            else:
                print(f"Invalid channel: {channel}")

    def toggle_mute(self, *channels:int):
        """toggle mute for MIDI channels (0-15)"""
        muted = []
        unmuted = []
        for channel in channels:
            if 0 <= channel <= 15:
                if channel in self.muted_channels:
                    self.muted_channels.discard(channel)
                    unmuted.append(channel+1)
                    # print(f"Unmuted channel {channel + 1} (0x{channel:X})")
                else:
                    muted.append(channel+1)
                    self.muted_channels.add(channel)
            else:
                print(f"Invalid channel: {channel}")
        print(f'Muted {muted}, unmuted {unmuted}')

    def unmute_all(self):
        """Unmute all channels"""
        self.muted_channels.clear()
        print("Unmuted all channels")

    def show_status(self):
        """Show current mute status"""
        if self.muted_channels:
            muted = " ".join(str(ch + 1) for ch in sorted(self.muted_channels))
            print(f"Muted_channels: {muted}")
        else:
            print("No channels muted")

    def print_help(self):
        """Print available commands"""
        print("\nCommands:")
        print("  m <channel>  - Mute channel (1-16)")
        print("  u <channel>  - Unmute channel (1-16)")
        print("  t <channel>  - Toggle channel (1-16)")
        print("  a            - Unmute all channels")
        print("  s            - Show status")
        print("  h            - Show this help")
        print("  q            - Quit")
        print("\nExamples:")
        print("  echo 'm 10' > /tmp/cmd")
        print("  echo 'u 10' > /tmp/cmd")
        print("")

    def process_command(self, cmd: str):
        """Process a command"""
        cmd = cmd.strip().lower()
        if not cmd:
            return

        parts = cmd.split()
        command = parts[0]

        if command == 'q' or command == 'quit':
            print("Shutting down...")
            self.running = False

        elif command == 'h' or command == 'help':
            self.print_help()

        elif command == 's' or command == 'status':
            self.show_status()

        elif command == 'a' or command == 'all':
            self.unmute_all()

        elif command == 'm' or command == 'mute':
            if len(parts) < 2:
                print("Usage: m <channels>")
                return
            try:
                channels = list( int(part)-1 for part in parts[1:]) # Convert from 1-16 to 0-15
                self.mute_channel(*channels)
            except ValueError:
                print(f"Invalid channel number: {parts[1]}")

        elif command == 'u' or command == 'unmute':
            if len(parts) < 2:
                print("Usage: u <channels>")
                return
            try:
                channels = list( int(part)-1 for part in parts[1:]) # Convert from 1-16 to 0-15
                self.unmute_channel(*channels)
            except ValueError:
                print(f"Invalid channel number: {parts[1]}")

        elif command == 't' or command == 'toggle':
            if len(parts) < 2:
                print("Usage: t <channels>")
                return
            try:
                channels = list( int(part)-1 for part in parts[1:]) # Convert from 1-16 to 0-15
                self.toggle_mute(*channels)
            except ValueError:
                print(f"Invalid channel number: {parts[1]}")

        else:
            print(f"Unknown command: {command}")
            print("Type 'h' for help")

    def stdin_reader(self):
        """Read from stdin line by line"""
        while self.running:
            try:
                lines = open(".sqtmute_instructions").readlines()
                if not lines:  # EOF
                    time.sleep(0.1)
                    continue
                for line in lines:
                    self.process_command(line.strip())
                with open(".sqtmute_instructions",'w'):
                    pass
            except FileNotFoundError:
                pass
            #print(f"Error: blah blah")
                time.sleep(0.1)

    def run(self):
        """Start the MIDI muter"""
        print(f"\nStarting MIDI Channel Muter")

        self.print_help()

        # Start stdin reader in a thread
        reader_thread = threading.Thread(target=self.stdin_reader, daemon=True)
        reader_thread.start()

        # Main loop - just keep alive
        try:
            while self.running:
                time.sleep(0.3)
        except KeyboardInterrupt:
            print("\nInterrupted")
        finally:
            self.running = False
            del self.midi_in
            del self.midi_out
            print("Shutdown complete")
            os.remove('.sqtmute_instructions')


if __name__ == "__main__":
    muter = MIDIChannelMuter()
    muter.run()