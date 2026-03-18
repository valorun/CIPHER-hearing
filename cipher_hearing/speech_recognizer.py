import logging

import numpy as np
from faster_whisper import WhisperModel

from .listener import Listener


class SpeechRecognizer:
    def __init__(self, whisper_model, wakeword_detector, client, samplerate=16000):
        self.stt = WhisperModel(whisper_model, device="cpu", compute_type="int8")
        self.client = client
        self.samplerate = samplerate
        self.wakeword_detector = wakeword_detector
        self.listener = Listener(samplerate, wakeword_detector, self.on_audio_frame)

    def predict(self, data):
        data = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32767.0
        segments, _ = self.stt.transcribe(
            data, beam_size=5, language="fr", vad_filter=True
        )
        segments = list(segments)
        if len(segments) > 0:
            return segments[0].text
        return None

    def on_wakeword(self):
        self.client.publish("server/hearing/wakeword")
        rec = self.listener.record()
        transcription = self.predict(rec)
        if transcription is not None:
            logging.info("Transcription: '%s'", transcription)
            self.client.publish("server/hearing/transcription", transcription)

    def on_audio_frame(self, data_16k_bytes, audio_16k):
        wake_word_conf = self.wakeword_detector.detect(data_16k_bytes)
        if wake_word_conf:
            logging.info(
                "Wakeword detected at %.2s%%",
                wake_word_conf * 100,
            )
            self.on_wakeword()
            logging.debug("Wakeword timed out")

    def start(self):
        self.listener.start()

    def stop(self):
        self.listener.stop()
