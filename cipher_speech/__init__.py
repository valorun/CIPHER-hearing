# coding: utf-8
import json
import logging
import paho.mqtt.client as Mqtt
import numpy as np
from os.path import exists
from logging.handlers import RotatingFileHandler
from logging.config import dictConfig
from keras.models import load_model

from .constants import MQTT_CLIENT_ID, MQTT_BROKER_URL, MQTT_BROKER_PORT, LOG_FILE, TRAINED_MODEL_PATH, SAMPLERATE, CHANNELS, WAKE_WORD_CLASS, DETECT_THRESHOLD
from .features import SELECTED_FEATURE, N_SAMPLE_MFCCS, N_MFCC
from .listener import Listener
from .processes import pre_process
from .reader import get_labels

import soundfile as sf

mqtt = None

def predict(model, data):
    data_reshaped = data.reshape(1, N_SAMPLE_MFCCS, N_MFCC)
    prediction = model.predict(data_reshaped)
    
    max_accuracy = np.max(prediction)

    print(get_labels())
    if max_accuracy < DETECT_THRESHOLD:
        return None
    best_class_index = np.argmax(prediction)
    print(max_accuracy)
    print(get_labels()[best_class_index])

    return get_labels()[best_class_index]

def create_app(debug=False):
    global mqtt

    mqtt = Mqtt.Client(MQTT_CLIENT_ID)
    model = None
   
    if exists(TRAINED_MODEL_PATH):
        logging.info("Loading model ...")
        model = load_model(TRAINED_MODEL_PATH)
    else:
        logging.error("No model found ! Exiting ...")
        exit(1)

    def on_wake_word():
        """
        Function called when the wake word is detected.
        """
        rec = listener.record()
        rec = pre_process(rec)
        prediction = predict(model, SELECTED_FEATURE(rec))
        if prediction is not None:
            logging.info("Intent '" + prediction + "' detected.")
            intent_payload = json.dumps({'intentName': prediction})
            mqtt.publish('speech/intent/' + prediction, intent_payload)
        else:
            logging.debug("No intent detected, maybe the threshold is too low ?")
            sf.write("test.wav", rec, SAMPLERATE)


    def on_noise(data):
        """
        Function called when some noise is detected in the microphone.
        """
        data = pre_process(data)
        sf.write('./test.wav', data, SAMPLERATE) # Save as WAV file

        prediction = predict(model, SELECTED_FEATURE(data))
        if prediction == WAKE_WORD_CLASS:
            logging.info("Wake word detected")
            on_wake_word()

    listener = Listener(on_noise)

    def on_disconnect(client, userdata, rc):
        """
        Function called when the client disconnect from the server.
        """
        listener.stop()
        logging.info("Disconnected from server")

    def on_connect(client, userdata, flags, rc):
        """
        Function called when the client connect to the server.
        """
        logging.info("Connected with result code " + str(rc))
        client.subscribe('server/connect')
        client.subscribe('speech/start')
        client.subscribe('speech/stop')
        listener.start()


    def on_message(client, userdata, msg):
        """
        Function called when a message is received from the server.
        """
        topic = msg.topic
        try:
            data = json.loads(msg.payload.decode('utf-8'))
        except ValueError:
            data = msg.payload.decode('utf-8')
        if topic == 'server/connect': #when the server start or restart, notify this raspberry is connected
            pass
        elif topic == 'speech/start':
            listener.start()
        elif topic == 'speech/stop':
            listener.stop()



    mqtt.on_connect = on_connect
    mqtt.on_message = on_message
    mqtt.on_disconnect = on_disconnect
    mqtt.enable_logger()

    mqtt.connect(MQTT_BROKER_URL, MQTT_BROKER_PORT, 60)

    return mqtt

def setup_logger(debug=False):
	if debug:
		log_level = 'DEBUG'
	else:
		log_level = 'INFO'
	
	dictConfig({
        'version': 1,
        'formatters': {'default': {
            'format': '%(asctime)s %(levelname)-8s [%(filename)s:%(lineno)d] %(name)s: %(message)s',
        }},
        'handlers': { 
            'default': { 
                'formatter': 'default',
                'class': 'logging.StreamHandler',
                'stream': 'ext://sys.stdout',  # Default is stderr
            },
            'file': { 
                'formatter': 'default',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': LOG_FILE,
                'maxBytes': 1024
            }
        },

        'root': {
            'level': log_level,
            'handlers': ['default', 'file']
        },
    })
	