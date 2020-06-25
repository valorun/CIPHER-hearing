#from python_speech_features import mfcc
from librosa.feature import mfcc
from .constants import SAMPLERATE, DEFAULT_SAMPLE_DURATION
import numpy as np

N_MFCC = 13
N_SAMPLE_MFCCS = 301

def mffcs(data):
    # if the sample is shorter, pad it
    padded = np.zeros(SAMPLERATE*DEFAULT_SAMPLE_DURATION)
    padded[:data.shape[0]] = data

    mfccs = mfcc(y=padded, sr=SAMPLERATE, n_mfcc=N_MFCC, n_fft=int(SAMPLERATE*0.025), hop_length=int(SAMPLERATE*0.01))
    return np.transpose(mfccs)

SELECTED_FEATURE = mffcs
