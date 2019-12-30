from python_speech_features import mfcc
import numpy as np
import scipy.io.wavfile as wav

def mean_mffcs(filename):
    (rate, sig) = wav.read(filename)
    return [np.mean(feature) for feature in mfcc(sig, rate)]