import logging
import json
import vosk
from snips_nlu import SnipsNLUEngine, load_resources
from snips_nlu.default_configs import CONFIG_FR

from .listener import Listener

class SpeechRecognizer():
    def __init__(self, vosk_model_path, wakeword_detector, nlu_dataset, client, samplerate=16000):
        self.stt = vosk.KaldiRecognizer(vosk.Model(vosk_model_path), samplerate)
        self.client = client
        self.samplerate = samplerate
        self.listener = Listener(samplerate, self.on_noise)
        self.wakeword_detector = wakeword_detector
        self.nlu_engine = SnipsNLUEngine(config=CONFIG_FR)
        self.nlu_engine.fit(json.load(open(nlu_dataset)))

    def train_nlu(self, dataset):
        self.nlu_engine = self.nlu_engine.fit(dataset)

    def predict(self, data):
        if self.stt.AcceptWaveform(data):
            result = json.loads(self.stt.Result())
            if 'text' in result:
                return result['text']
        return None

    def on_wakeword(self):
        """
        Function called when the wake word is detected.
        """
        self.client.publish('server/hearing/wakeword')

        rec = self.listener.record()
        transcription = self.predict(rec)
        if transcription is not None:
            logging.info("Transcription: '%s'", transcription)
            parsing = self.nlu_engine.parse(transcription)
            intent = parsing['intent']['intentName']
            if intent is not None:
                logging.info("Intent '%s' detected.", intent)
                self.client.publish('server/hearing/intent/' + intent, json.dumps(parsing))
            else:
                logging.debug("No intent detected, maybe the threshold is too low ?")


    def on_noise(self, data):
        """
        Function called when some noise is detected in the microphone.
        """
        wake_word_result = self.wakeword_detector.detect(data)
        if wake_word_result is not None:
            logging.info("Wakeword detected at %.2s%%", wake_word_result['raven']['probability']*100)
            self.on_wakeword()
            logging.debug("Wakeword timed out")

    def start(self):
        self.listener.start()
    
    def stop(self):
        self.listener.stop()
