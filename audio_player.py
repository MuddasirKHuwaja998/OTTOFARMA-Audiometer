import numpy as np
import sounddevice as sd
import argparse


class AudioPlayer:

    def __init__(self):
        """Creates an audio player that can play sine beeps at various frequencies, volumes and with various durations.
        Automatically detects current samplerate of selected sound device.
        """
        self.fs = self.get_device_samplerate()
        self.beep_duration = 10
        self.volume = 0
        self.frequency = 440
        self.stream = None
        self.is_playing = False

    def generate_tone(self)->np.array:
        """Generates a sine tone with current audio player settings.

        Returns:
            array: sine wave as numpy array
        """
        t = np.linspace(start=0, 
                        stop=self.beep_duration, 
                        num=int(self.fs * self.beep_duration), 
                        endpoint=False)
        tone = np.sin(2 * np.pi * self.frequency * t) * self.volume

        # Create fade-out envelope
        fade_duration = 0.003  # 3 ms fade-out
        fade_samples = int(self.fs * fade_duration)
        fade_out = np.linspace(1, 0, fade_samples)
        envelope = np.ones_like(tone)
        envelope[-fade_samples:] = fade_out

        # Apply the envelope to the tone
        tone = tone * envelope

        return tone
    
    def play_beep(self, frequency:int, volume:float, duration:int, channel:str='lr'):
        """Sets the frequency, volume and beep duration of the audio player and then plays a beep with those parameters.

        Args:
            frequency (int): frequency in Hz
            volume (float): volume multiplier (between 0 and 1)
            duration (int): duration of the beep in seconds
            channel (string): 'l', 'r' or 'lr' for only left, only right or both channels respectively
        """
        self.frequency = frequency
        self.volume = volume
        self.beep_duration = duration
        tone = self.generate_tone()
        if channel == 'l':
            sd.play(np.array([tone, np.zeros(len(tone))]).T, self.fs)
        elif channel == 'r':
            sd.play(np.array([np.zeros(len(tone)), tone]).T, self.fs)
        else:
            sd.play(tone, self.fs)

    def stop(self):
        """Stops the current playback.
        """
        sd.stop()

    def int_or_str(self, text: str)->int:
        """Helper function for argument parsing.
        """
        try:
            return int(text)
        except ValueError:
            return text

    def get_device_samplerate(self):
        """Gets current samplerate from the selected audio output device.

        Returns:
            float: samplerate of current sound device
        """
        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument(
            '-l', '--list-devices', action='store_true',
            help='show list of audio devices and exit')
        args, remaining = parser.parse_known_args()
        if args.list_devices:
            print(sd.query_devices())
            parser.exit(0)
        parser = argparse.ArgumentParser(
            description=__doc__,
            formatter_class=argparse.RawDescriptionHelpFormatter,
            parents=[parser])
        parser.add_argument(
            'frequency', nargs='?', metavar='FREQUENCY', type=float, default=500,
            help='frequency in Hz (default: %(default)s)')
        parser.add_argument(
            '-d', '--device', type=self.int_or_str,
            help='output device (numeric ID or substring)')
        parser.add_argument(
            '-a', '--amplitude', type=float, default=0.2,
            help='amplitude (default: %(default)s)')
        args = parser.parse_args(remaining)
        return sd.query_devices(args.device, 'output')['default_samplerate']