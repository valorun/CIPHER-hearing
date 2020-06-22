#from python_speech_features import mfcc
from librosa.feature import mfcc
import numpy as np


def mean_mffcs(data, samplerate):
    #mfccs = mfcc(data, samplerate)
    #mfccs = np.transpose(mfccs)
    mfccs = mfcc(y=data, sr=samplerate, n_mfcc=13, n_fft=int(samplerate*0.025), hop_length=int(samplerate*0.01))
    mfccs = np.transpose(mfccs)
    #result = np.zeros((samplerate*3, 13))
    #result[:mfccs.shape[0],:mfccs.shape[1]] = mfccs
    #print(len(mfccs))
    return np.mean(mfccs, axis = 0) #result.flatten()