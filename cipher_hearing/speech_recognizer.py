import logging
import json
import vosk

from .listener import Listener


class SpeechRecognizer:
    def __init__(self, vosk_model_path, wakeword_detector, client, samplerate=16000):
        self.stt = vosk.KaldiRecognizer(vosk.Model(vosk_model_path), samplerate)
        self.client = client
        self.samplerate = samplerate
        self.listener = Listener(samplerate, self.on_noise)
        self.wakeword_detector = wakeword_detector

    def predict(self, data):
        if self.stt.AcceptWaveform(data):
            result = json.loads(self.stt.Result())
            if "text" in result:
                return result["text"]
        return None

    def on_wakeword(self):
        """
        Function called when the wake word is detected.
        """
        self.client.publish("server/hearing/wakeword")

        rec = self.listener.record()
        transcription = self.predict(rec)
        if transcription is not None:
            logging.info("Transcription: '%s'", transcription)
            self.client.publish('server/hearing/transcription', transcription)

    def on_noise(self, data):
        """
        Function called when some noise is detected in the microphone.
        """
        #self.on_wakeword()
        wake_word_result = self.wakeword_detector.detect(data)
        print(wake_word_result)
        if wake_word_result:
            #logging.info(
            #    "Wakeword detected at %.2s%%",
            #    wake_word_conf * 100,
            #)
            #self.on_wakeword()
            logging.debug("Wakeword timed out")

    def start(self):
        self.listener.start()

    def stop(self):
        self.listener.stop()
