import json
import numpy as np
import logging
from .constants import WAKE_WORD_CLASS, DETECT_THRESHOLD
from .features import mfccs, N_SAMPLE_MFCCS, N_MFCC
from .listener import Listener
from .processes import pre_process

from librosa.output import write_wav


class SpeechRecognizer():
    def __init__(self, model, model_data, client):
        self.model = model
        self.model_data = model_data
        self.client = client
        self.intents = model_data['intents']
        self.listener = Listener(model_data['channels'], model_data['samplerate'], self.on_noise)

    def predict(self, data):
        data_reshaped = data.reshape(1, N_SAMPLE_MFCCS, N_MFCC)
        prediction = self.model.predict(data_reshaped)
        
        max_accuracy = np.max(prediction)
        #print(self.intents[np.argmax(prediction)])
        #print(max_accuracy)

        if max_accuracy < DETECT_THRESHOLD:
            return None, 1.0
        best_class_index = np.argmax(prediction)

        return self.intents[best_class_index], max_accuracy

    def on_wake_word(self):
        """
        Function called when the wake word is detected.
        """
        rec = self.listener.record()
        rec = pre_process(rec, self.model_data['samplerate'], self.model_data['default_sample_duration'])
        prediction, accuracy = self.predict(mfccs(rec, self.model_data['samplerate']))
        if prediction is not None:
            logging.info("Intent '%s' detected at %s%%.", prediction, int(accuracy*100))
            self.client.publish('speech/intent/' + prediction)
        else:
            logging.debug("No intent detected, maybe the threshold is too low ?")

    def on_noise(self, data):
        """
        Function called when some noise is detected in the microphone.
        """
        logging.info("Noise detected")
        #write_wav('./test1.wav', data, get_model_data()['samplerate']) # Save as WAV file

        data = pre_process(data, self.model_data['samplerate'], self.model_data['default_sample_duration'])

        #write_wav('./test.wav', data, get_model_data()['samplerate']) # Save as WAV file

        prediction, accuracy = self.predict(mfccs(data, self.model_data['samplerate']))
        if prediction == WAKE_WORD_CLASS:
            logging.info("Wake word detected")
            self.on_wake_word()

    def start(self):
        self.listener.start()
    
    def stop(self):
        self.listener.stop()
