import queue
import numpy as np
import logging
import time
import sounddevice as sd
from librosa.feature import rms 
from .constants import SAMPLERATE, CHANNELS, SPEECH_TIMEOUT, NOISE_THRESHOLD

class Listener:
    q = queue.Queue()
    def __init__(self, on_noise = None):
        self.channels = CHANNELS
        self.samplerate = SAMPLERATE
        self.threshold = NOISE_THRESHOLD # noise threshold
        self.on_noise = on_noise

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
        start = time.time()
        current = time.time()
        end = time.time() + SPEECH_TIMEOUT
        logging.info("Recording started")

        while current <= end:
            data = Listener.q.get()
            if rms(data) >= self.threshold: 
                end = time.time() + SPEECH_TIMEOUT
            current = time.time()
            rec = np.append(rec, data)
        logging.info("Recording ended")
        print(end - start)
        return rec

    def start(self):
        logging.info("Listener started")
        self.listening = True
        logging.info("Starting listening ...")
        with sd.InputStream(samplerate=self.samplerate, channels=self.channels, callback=Listener._device_callback):
            while self.listening:
                data = Listener.q.get()
                rms_val = rms(data)
                #print(rms(y=data))
                #print("> " + str(rms_val))
                if rms_val > self.threshold:
                    logging.info("Noise detected")
                    rec = self.record()
                    if self.on_noise is not None:
                        self.on_noise(rec)

    def stop(self):
        logging.info("Listener stopped")
        self.listening = False
