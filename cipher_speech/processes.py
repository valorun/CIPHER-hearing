import numpy as np
from librosa.core import magphase, istft, stft
from librosa.util import softmask
from librosa.decompose import nn_filter
from librosa.effects import trim, split

def voice_separation(data, samplerate):
    S_full, phase = magphase(stft(data))

    S_filter = nn_filter(S_full,
                                       aggregate=np.median,
                                       metric='cosine')
                                       #width=int(librosa.time_to_frames(2, sr=samplerate)))

    S_filter = np.minimum(S_full, S_filter)
    margin_i, margin_v = 2, 10
    power = 2

    mask_i = softmask(S_filter,
                                margin_i * (S_full - S_filter),
                                power=power)

    mask_v = softmask(S_full - S_filter,
                                margin_v * S_filter,
                                power=power)

    S_foreground = mask_v * S_full
    S_background = mask_i * S_full
    return istft(S_foreground)

def pre_process(data, samplerate):
    data = voice_separation(data, samplerate)
    data, trim_interval = trim(data, top_db=20, frame_length=2048, hop_length=512)
    non_silent_intervals = split(data, top_db=40, frame_length=100, hop_length=25)
    # get only the non silent intervals in the signal
    data = data[non_silent_intervals[0][0]:non_silent_intervals[0][1]]
    return data

