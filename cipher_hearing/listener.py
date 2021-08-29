from multiprocessing import Queue
from threading import Thread, Lock
from webrtcvad import Vad
import numpy as np
import time
import sounddevice as sd
from .constants import SPEECH_TIMEOUT, NOISE_THRESHOLD

def rms(arr):
    return np.sqrt(np.mean(arr**2))

class Listener:
    q = Queue()
    def __init__(self, samplerate, on_noise=None):
        self.samplerate = samplerate
        self.threshold = NOISE_THRESHOLD # noise threshold
        self.speech_timeout = SPEECH_TIMEOUT
        self.on_noise = on_noise
        self.listening = Lock()
        self.vad = Vad()
        self.vad.set_mode(3) # very restrictive filtering

    @staticmethod
    def _device_callback(indata, frames, time, status):
        """
        This is called (from a separate thread) for each audio block.
        """
        Listener.q.put(bytes(indata))

    def record(self):
        recorded_data = []
        current = time.time()
        end = time.time() + self.speech_timeout

        # record until no sound is detected or time is over
        while current <= end:
            data = Listener.q.get()
            recorded_data.append(data)
            if self.vad.is_speech(data, self.samplerate):
                end = time.time() + self.speech_timeout
            current = time.time()
        #print(end - start)
        return recorded_data
        
    def _start(self):
        self.listening.acquire()
        with sd.RawInputStream(samplerate=self.samplerate, channels=1, callback=Listener._device_callback, dtype='int16', blocksize=int(self.samplerate * 0.03)):
            while self.listening.locked():
                data = Listener.q.get()
                #if self.vad.is_speech(data.tobytes(), self.samplerate):
                if self.on_noise is not None:
                    self.on_noise(data)

    def start(self):
        Thread(target=self._start).start()

    def stop(self):
        if self.listening.locked():
            self.listening.release()
