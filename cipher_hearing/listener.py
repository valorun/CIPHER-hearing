import time
from collections import deque
from multiprocessing import Queue
from threading import Lock, Thread

import numpy as np
import sounddevice as sd

from .config import client_config


class Listener:
    q = Queue()

    def __init__(self, samplerate, wakeword_detector=None, on_audio_frame=None):
        self.device_samplerate = samplerate
        self.vad_samplerate = 16000
        
        self.downsample_ratio = max(1, int(self.device_samplerate / self.vad_samplerate))
        
        self.speech_timeout = client_config.SPEECH_TIMEOUT
        self.on_audio_frame = on_audio_frame
        self.listening = Lock()
        
        self.wakeword_detector = wakeword_detector
        
        # OpenWakeWord works best with 80ms frames (1280 samples at 16kHz)
        self.frame_size = 1280
        self.device_blocksize = self.frame_size * self.downsample_ratio
        
        self.vad_threshold = float(client_config.VAD_THRESHOLD) if client_config.VAD_THRESHOLD is not None else 0.5

    @staticmethod
    def _device_callback(indata, frames, time, status):
        Listener.q.put(bytes(indata))
        
    def _process_audio(self, data: bytes) -> tuple[bytes, np.ndarray]:
        audio_data = np.frombuffer(data, dtype=np.int16)
        
        if self.downsample_ratio > 1:
            audio_data = audio_data[::self.downsample_ratio]
            
        return audio_data.tobytes(), audio_data

    def record(self):
        recorded_data = b""
        vad_buffer = deque(
            maxlen=int(self.vad_samplerate / self.frame_size * self.speech_timeout)
        )
        current = time.time()
        end = time.time() + (self.speech_timeout * 2)

        while current <= end:
            raw_data = Listener.q.get()
            data_16k_bytes, audio_16k = self._process_audio(raw_data)
            
            recorded_data += data_16k_bytes

            # Use the VAD from openWakeWord (integrated in WakeDetector)
            if self.wakeword_detector and hasattr(self.wakeword_detector.model, 'vad'):
                is_speech = self.wakeword_detector.model.vad.predict(audio_16k, frame_size=self.frame_size) >= self.vad_threshold
            else:
                is_speech = True  # If no VAD available, assume speech
                
            vad_buffer.append(is_speech)

            num_voiced = len([speech for speech in vad_buffer if speech])

            if vad_buffer.maxlen is not None and num_voiced > 0.9 * vad_buffer.maxlen:
                end = time.time() + self.speech_timeout
            current = time.time()
            time.sleep(0.08)
            
        return recorded_data

    def _start(self):
        self.listening.acquire()
        
        with sd.RawInputStream(
            samplerate=self.device_samplerate,
            channels=1,
            callback=Listener._device_callback,
            dtype="int16",
            blocksize=self.device_blocksize,
        ):
            while self.listening.locked():
                raw_data = Listener.q.get()
                data_16k_bytes, audio_16k = self._process_audio(raw_data)

                if self.on_audio_frame is not None:
                    self.on_audio_frame(data_16k_bytes, audio_16k)

    def start(self):
        Thread(target=self._start).start()

    def stop(self):
        if self.listening.locked():
            self.listening.release()
