import logging
import vosk
from snips_nlu import SnipsNLUEngine
from snips_nlu.default_configs import CONFIG_FR

from .constants import STT_THRESHOLD
from .listener import Listener

class SpeechRecognizer():
    def __init__(self, vosk_model_path, wakeword_detector, client, samplerate=16000):
        self.stt = vosk.KaldiRecognizer(vosk.Model(vosk_model_path), samplerate)
        self.client = client
        self.samplerate = samplerate
        self.listener = Listener(samplerate, self.on_noise)
        self.wakeword_detector = wakeword_detector
        self.nlu_engine = SnipsNLUEngine(config=CONFIG_FR)

    def train_nlu(self, dataset):
        self.nlu_engine = self.nlu_engine.fit(dataset)

    def predict(self, data):
        if self.stt.AcceptWaveform(data):
            result = self.stt.Result()
            if 'text' in result:
                return result['text']
        return None
            #return self.stt.PartialResult()
        #if max_accuracy < STT_THRESHOLD:
        #    return None, 1.0
        #best_class_index = np.argmax(prediction)

    def on_wakeword(self):
        """
        Function called when the wake word is detected.
        """
        self.client.publish('server/hearing/wakeword')
        print("Speak now")
        rec = self.listener.record()
        for r in rec:
            transcription = self.predict(r)
            if transcription is not None:
                logging.info("Transcription: '%s'", transcription)
                parsing = self.nlu_engine.parse(transcription)
                if parsing is not None:
                    intent = parsing["intent"]["intentName"]
                    logging.info("Intent '%s' detected.", intent)
                    self.client.publish('server/hearing/intent/' + intent)
                else:
                    logging.debug("No intent detected, maybe the threshold is too low ?")
        print("END")


    def on_noise(self, data):
        """
        Function called when some noise is detected in the microphone.
        """
        if self.wakeword_detector.detect(data) is not None:
            self.on_wakeword()

    def start(self):
        self.listener.start()
    
    def stop(self):
        self.listener.stop()
