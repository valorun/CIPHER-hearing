from math import sqrt

import sounddevice as sd
import soundfile as sf
import logging
from .constants import SAMPLERATE, CHANNELS, DEFAULT_SAMPLE_DURATION


def rms(frame):
    # RMS amplitude is defined as the square root of the 
    # mean over time of the square of the amplitude.

    # iterate over the block.
    sum_squares = 0.0
    for sample in frame:
        # sample is a signed short in +/- 32768. 
        # normalize it to 1.0
        n = sum(sample) / len(sample)
        sum_squares += n*n

    return sqrt(sum_squares / len(frame))


def record(filename=None):
    record = sd.rec(int(DEFAULT_SAMPLE_DURATION * SAMPLERATE), samplerate=SAMPLERATE, channels=2)
    sd.wait()  # Wait until recording is finished
    if filename is not None:
        logging.info("Saving " + filename)
        sf.write(filename, record, SAMPLERATE) # Save as WAV file
    return record