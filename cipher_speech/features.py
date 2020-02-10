#from python_speech_features import mfcc
from librosa.feature import mfcc
import numpy as np


def mean_mffcs(data, samplerate):
    #mfccs = mfcc(data, samplerate)
    #mfccs = np.transpose(mfccs)
    mfccs = mfcc(y=data, sr=samplerate, n_mfcc=13, n_fft=int(samplerate*0.025), hop_length=int(samplerate*0.01))
    return [np.mean(feature) for feature in mfccs]