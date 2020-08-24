from multiprocessing import Queue
from threading import Thread, Lock
import numpy as np
import time
import sounddevice as sd
from librosa.feature import rms 
from .constants import SPEECH_TIMEOUT, NOISE_THRESHOLD

class Listener:
    q = Queue()
    def __init__(self, channels, samplerate, on_noise=None):
        self.channels = channels
        self.samplerate = samplerate
        self.threshold = NOISE_THRESHOLD # noise threshold
        self.speech_timeout = SPEECH_TIMEOUT
        self.on_noise = on_noise
        self.listening = Lock()

    @staticmethod
    def _device_callback(indata, frames, time, status):
        """
        This is called (from a separate thread) for each audio block.
        """
        data = indata.copy()
        if data.ndim > 1:
            # get max value between channels (if there is more than 1)
            data = np.amax(data, axis=1)
        Listener.q.put(data)

    def record(self):
        rec = np.array([])
        current = time.time()
        end = time.time() + self.speech_timeout

        # record until no sound is detected or time is over
        while current <= end:
            data = Listener.q.get()
            if rms(data) >= self.threshold: 
                end = time.time() + self.speech_timeout
            current = time.time()
            rec = np.append(rec, data)
        #print(end - start)
        
        return rec

    def _start(self):
        self.listening.acquire()
        with sd.InputStream(samplerate=self.samplerate, channels=self.channels, callback=Listener._device_callback):
            while self.listening.locked():
                data = Listener.q.get()
                rms_val = rms(data)
                if rms_val > self.threshold:
                    rec = self.record()
                    if self.on_noise is not None:
                        self.on_noise(rec)

    def start(self):
        Thread(target=self._start).start()

    def stop(self):
        self.listening.release()
