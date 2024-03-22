import numpy as np
import torch
import torch.nn as nn
from sonopy import mfcc_spec


class MFCC(nn.Module):

    def __init__(self, sample_rate, fft_size=400, window_stride=(400, 200), num_filt=40, num_coeffs=40):
        super(MFCC, self).__init__()
        self.sample_rate = sample_rate
        self.window_stride = window_stride
        self.fft_size = fft_size
        self.num_filt = num_filt
        self.num_coeffs = num_coeffs
        self.mfcc = lambda x: mfcc_spec(
            x, self.sample_rate, self.window_stride,
            self.fft_size, self.num_filt, self.num_coeffs
        )
    
    def forward(self, x):
        return torch.Tensor(self.mfcc(x.squeeze(0).numpy())).transpose(0, 1).unsqueeze(0)


def get_featurizer(sample_rate):
    return MFCC(sample_rate=sample_rate)

class WakeDetector():
    def __init__(self, wakeword_model_path, threshold, samplerate=16000):
        self.threshold = threshold
        self.featurizer = get_featurizer(sample_rate=samplerate)
        self.model = torch.jit.load(wakeword_model_path)
        self.model.eval().to('cpu') 
        self.detect_in_row = 0

    def detect(self, data):
        prediction = self.predict(data)
        return prediction

    def predict(self, audio):
        with torch.no_grad():
            #waveform, _ = torchaudio.load(fname, normalize=False)
            # waveform = waveform.type('torch.FloatTensor')
            #mfcc = self.featurizer(waveform).transpose(1, 2).transpose(0, 1)
            #print(audio)
            # TODO: read from buffer instead of saving and loading file
            #waveform = torch.Tensor([np.frombuffer(a, dtype=np.int16) for a in audio]).flatten()
            waveform = torch.Tensor(np.frombuffer(audio, dtype=np.int16)).flatten()
            mfcc = self.featurizer(waveform).transpose(1, 2).transpose(0, 1)#.unsqueeze(1)
            out = self.model(mfcc)
            pred = torch.round(torch.sigmoid(out))
            return pred.item()
