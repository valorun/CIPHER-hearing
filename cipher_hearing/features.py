from librosa.feature import mfcc
import numpy as np

N_MFCC = 13
N_SAMPLE_MFCCS = 301

def mfccs(data, samplerate):
    mfccs = mfcc(y=data, sr=samplerate, n_mfcc=N_MFCC, n_fft=int(samplerate*0.025), hop_length=int(samplerate*0.01))
    return np.transpose(mfccs)
