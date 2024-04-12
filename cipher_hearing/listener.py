import time
from collections import deque
from multiprocessing import Queue
from threading import Lock, Thread

import sounddevice as sd
from webrtcvad import Vad

from .config import client_config


class Listener:
    q = Queue()

    def __init__(self, samplerate, on_noise=None):
        self.samplerate = samplerate
        self.speech_timeout = client_config.SPEECH_TIMEOUT
        self.on_noise = on_noise
        self.listening = Lock()
        self.vad = Vad()
        self.vad.set_mode(2)  # restrictive filtering
        self.blocksize = int(
            samplerate * 0.03
        )  # VAD only accept 10, 20 or 30ms per frame
        self.on_noise_rate = int(
            round(samplerate * 0.5 / self.blocksize)
        )  # pass data to on_noise every x frames (here every 200ms)

    @staticmethod
    def _device_callback(indata, frames, time, status):
        """
        This is called (from a separate thread) for each audio block.
        """
        Listener.q.put(bytes(indata))

    def record(self):
        recorded_data = b""
        vad_buffer = deque(
            maxlen=int(self.samplerate / self.blocksize * self.speech_timeout)
        )  # rolling buffer, frames from last seconds to match VAD window size
        current = time.time()
        end = time.time() + (self.speech_timeout * 2)


        # record until no sound is detected or time is over
        while current <= end:
            data = Listener.q.get()
            recorded_data += data

            vad_buffer.append(self.vad.is_speech(data, self.samplerate))

            num_voiced = len([speech for speech in vad_buffer if speech])

            if num_voiced > 0.9 * vad_buffer.maxlen:
                end = time.time() + self.speech_timeout
            current = time.time()
            time.sleep(0.03)
        # print(end - start)
        return recorded_data

    def _start(self):
        self.listening.acquire()
        recorded_data = deque(
            maxlen=int(self.samplerate / self.blocksize) * 2
        )  # rolling buffer, frames from last seconds to match VAD window size

        on_noise_counter = 0
        with sd.RawInputStream(
            samplerate=self.samplerate,
            channels=1,
            callback=Listener._device_callback,
            dtype="int16",
            blocksize=self.blocksize,
        ):
            while self.listening.locked():
                data = Listener.q.get()

                if self.on_noise is not None:
                    is_speech = self.vad.is_speech(data, self.samplerate)
                    recorded_data.append((data, is_speech))
                    on_noise_counter += 1

                    num_voiced = len([f for f, speech in recorded_data if speech])
                    # Noise is detected when there is enough data
                    # and when VAD confirm there is speech in a significant portion of the data
                    # and on_noise hasn't been called recently
                    if (
                        num_voiced > 0.6 * recorded_data.maxlen
                        and on_noise_counter >= self.on_noise_rate
                    ):
                        self.on_noise(b"".join([f[0] for f in recorded_data]))
                        on_noise_counter = 0

    def start(self):
        Thread(target=self._start).start()

    def stop(self):
        if self.listening.locked():
            self.listening.release()
