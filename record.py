import sounddevice as sd
from scipy.io.wavfile import write

fs = 44100  # Sample rate
seconds = 3  # Duration of recording

def record(filename):
    record = sd.rec(int(seconds * fs), samplerate=fs, channels=2)
    print("Speak now")
    sd.wait()  # Wait until recording is finished
    print("Saving ...")
    write(filename, fs, record)  # Save as WAV file 