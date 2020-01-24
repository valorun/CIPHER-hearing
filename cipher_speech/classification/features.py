from python_speech_features import mfcc
import numpy as np


def mean_mffcs(data, samplerate):
    #print(len(data))
    return [np.mean(feature) for feature in mfcc(data, samplerate)]
