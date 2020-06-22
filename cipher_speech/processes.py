import numpy as np
from librosa.core import magphase, istft, stft
from librosa.util import softmask, frame
from librosa.decompose import nn_filter
from librosa.effects import trim, split
from librosa.feature import spectral_centroid


#def ambiant_noice_reduction(data, samplerate):
    # Divide the audio in frames of 25ms with hop length of 10ms.
    #frames = frame(data, frame_length=round(samplerate*(0.025/60)), hop_length=round(samplerate*(0.010/60)))
    # Calculate the spectral centroids for each window.
   # centroids = spectral_centroid(y=data, sr=samplerate, win_length=round(samplerate*(0.025/60)), hop_length=round(samplerate*(0.010/60)))
    ##centroids = [spectral_centroid(y=f, sr=samplerate) for f in frames]
    #lower_threshold = np.min(centroids)
    #upper_threshold = np.max(centroids)
    # Apply a lowshelf filter for gain=-30 and frequency as the lower threshold. Apply a highshelf filter for gain=-30 and higher threshold.
    # Apply limiter with a gain of +10 to increase the volume.
    #less_noise = AudioEffectsChain().lowshelf(gain=-30.0, frequency=lower_threshold, slope=0.5).highshelf(gain=-30.0, frequency=upper_threshold, slope=0.5).limiter(gain=20.0)
    #data_cleaned = less_noise(data)
    #return data_cleaned

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
    #data = ambiant_noice_reduction(data, samplerate)
    #data = voice_separation(data, samplerate)
    data, trim_interval = trim(data, top_db=20, frame_length=2048, hop_length=512)
    non_silent_intervals = split(data, top_db=40, frame_length=100, hop_length=25)
    # get only the non silent intervals in the signal
    data = data[non_silent_intervals[0][0]:non_silent_intervals[0][1]]
    return data

