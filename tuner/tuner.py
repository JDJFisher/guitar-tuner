
######################################################################
# Author:  Matt Zucker
# Date:    July 2016
# License: Creative Commons Attribution-ShareAlike 3.0
#          https://creativecommons.org/licenses/by-sa/3.0/us/
######################################################################

# Third party imports
import numpy as np
import pyaudio

NOTE_MIN = 47       # C4
NOTE_MAX = 69       # A4
FSAMP = 22050       # Sampling frequency in Hz
FRAME_SIZE = 2048   # How many samples per frame?
FRAMES_PER_FFT = 16 # FFT takes average across how many frames?

SAMPLES_PER_FFT = FRAME_SIZE*FRAMES_PER_FFT
FREQ_STEP = float(FSAMP)/SAMPLES_PER_FFT
NOTE_NAMES = 'C D♭ D E♭ E F G♭ G A♭ A B♭ B'.split()

def freq_to_number(f): return 69 + 12*np.log2(f/440.0)
def number_to_freq(n): return 440 * 2.0**((n-69)/12.0)
def note_name(n): return NOTE_NAMES[n % 12]
def note_to_fftbin(n): return number_to_freq(n)/FREQ_STEP

I_MIN = max(0, int(np.floor(note_to_fftbin(NOTE_MIN-1))))
I_MAX = min(SAMPLES_PER_FFT, int(np.ceil(note_to_fftbin(NOTE_MAX+1))))


class Tuner(object):
  
    def __init__(self, dev_index=None):
        # Initialize audio stream
        self.stream = pyaudio.PyAudio().open(format=pyaudio.paInt16,
                                        channels=1,
                                        rate=FSAMP,
                                        input=True,
                                        output=False,
                                        input_device_index=dev_index,
                                        frames_per_buffer=FRAME_SIZE)


    def __del__(self):
        # Cleanup audio stream
        self.stop()
        self.stream.close()


    def go(self, verbose):
        # Allocate space to run an FFT.
        buf = np.zeros(SAMPLES_PER_FFT, dtype=np.float32)
        num_frames = 0

        # Start stream
        self.stream.start_stream()

        # Create Hanning window function
        window = 0.5 * (1 - np.cos(np.linspace(0, 2*np.pi, SAMPLES_PER_FFT, False)))

        # Log info
        if verbose:
            print(f'Sampling at {FSAMP} Hz with max resolution of {FREQ_STEP} Hz')

        while self.stream.is_active():

            # Shift the buffer down and new data in
            buf[:-FRAME_SIZE] = buf[FRAME_SIZE:]
            buf[-FRAME_SIZE:] = np.frombuffer(self.stream.read(FRAME_SIZE), np.int16)

            # Run the FFT on the windowed buffer
            fft = np.fft.rfft(buf * window)

            # Get frequency of maximum response in range
            freq = (np.abs(fft[I_MIN:I_MAX]).argmax() + I_MIN) * FREQ_STEP

            # Get note number and nearest note
            n = freq_to_number(freq)
            n0 = int(round(n))

            # Console output once we have a full buffer
            num_frames += 1

            if num_frames >= FRAMES_PER_FFT:
                print(' freq: {:7.2f} Hz   note: {:>3s} {:+.2f}'.format(freq, note_name(n0), n-n0), end='\r')


    def stop(self):
        self.stream.stop_stream()

