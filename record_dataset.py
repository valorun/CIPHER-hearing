from cipher_speech.record import SAMPLERATE, CHANNELS
from cipher_speech.constants import DATASET_PATH
from os.path import join, exists
from os import listdir
import soundfile as sf
import sounddevice as sd

DEFAULT_SAMPLE_DURATION = 3  # Duration of recording


def record(filename=None):
    record = sd.rec(int(DEFAULT_SAMPLE_DURATION * SAMPLERATE), samplerate=SAMPLERATE, channels=CHANNELS)
    sd.wait()  # Wait until recording is finished
    if filename is not None:
        sf.write(filename, record, SAMPLERATE) # Save as WAV file
    return record

if __name__ == '__main__':
    n_samples = 1
    dir_number = "2"

    samples_path = join(DATASET_PATH, str(dir_number))

    i = 0
    for n in range(n_samples):
        while exists(join(samples_path, str(i) + '.wav')):
            i += 1
        new_file_name = join(samples_path, str(i) + '.wav')
        print("Speak now ... Iteration " + str(n))
        record(new_file_name)
