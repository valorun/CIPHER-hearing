import queue
import logging
import sounddevice as sd
from .utils import rms, record
from .constants import SAMPLERATE, CHANNELS, DEFAULT_SAMPLE_DURATION


class Listener:
    q = queue.Queue()
    def __init__(self, on_noise = None):
        self.channels = CHANNELS
        self.samplerate = SAMPLERATE
        self.threshold = 0.2 # noise threshold
        self.on_noise = on_noise

    @staticmethod
    def _device_callback(indata, frames, time, status):
        """
        This is called (from a separate thread) for each audio block.
        """
        Listener.q.put(indata.copy())
        
    def start(self):
        self.listening = True
        logging.info("Starting listening ...")
        with sd.InputStream(samplerate=self.samplerate, channels=self.channels, callback=Listener._device_callback):
            while self.listening:
                data = Listener.q.get()
                rms_val = rms(data)
                if rms_val > self.threshold:
                    logging.info("Noise detected")
                    rec = record()
                    if self.on_noise is not None:
                        self.on_noise(rec)

    def stop(self):
        self.listening = False