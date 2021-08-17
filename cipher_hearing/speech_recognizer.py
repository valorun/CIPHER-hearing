import json
import numpy as np
import logging
import vosk

from .constants import DETECT_THRESHOLD
from .listener import Listener
from .wakeword_detector import WakeDetector

class SpeechRecognizer():
    def __init__(self, vosk_model_path, wakeword_model_path, samplerate, client):
        self.stt = vosk.KaldiRecognizer(vosk.Model(vosk_model_path), samplerate)
        self.samplerate = samplerate
        self.client = client
        self.listener = Listener(samplerate, self.on_noise)
        self.wakeword_detector = WakeDetector(8000, wakeword_model_path)

    def predict(self, data):
        if self.stt.AcceptWaveform(data):
            result = self.stt.Result()
            if 'test' in result:
                return result['text']
            else:
                return None
        else:
            return None
            #return self.stt.PartialResult()
        #if max_accuracy < DETECT_THRESHOLD:
        #    return None, 1.0
        #best_class_index = np.argmax(prediction)

    def on_wakeword(self):
        """
        Function called when the wake word is detected.
        """
        rec = self.listener.record()
        pred = self.predict(rec)
       
        #if prediction is not None:
        #    logging.info("Intent '%s' detected at %s%%.", prediction, int(accuracy*100))
        #    self.client.publish('server/hearing/intent/' + prediction)
        #else:
        #    logging.debug("No intent detected, maybe the threshold is too low ?")

    def on_noise(self):
        """
        Function called when some noise is detected in the microphone.
        """
        logging.info("Noise detected")

        if self.wakeword_detector.detect():
            logging.info("Wake word detected")
            self.on_wakeword()

    def start(self):
        self.listener.start()
    
    def stop(self):
        self.listener.stop()
