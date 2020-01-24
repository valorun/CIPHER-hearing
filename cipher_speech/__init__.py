# coding: utf-8
import numpy as np
import json
import os
import logging
import paho.mqtt.client as Mqtt
from logging.handlers import RotatingFileHandler
from logging.config import dictConfig
from .constants import MQTT_CLIENT_ID, MQTT_BROKER_URL, MQTT_BROKER_PORT, LOG_FILE

from .classification import models, reader, features
from .record import Listener, record, SAMPLERATE

mqtt = None


def create_app(debug=False):
    global mqtt

    mqtt = Mqtt.Client(MQTT_CLIENT_ID)
    dataset = reader.get_dataset(features.mean_mffcs)
    model = models.KNNModel(3, 0.6)
    model.train(dataset)
    #model.load('knn_model.joblib')

    def on_wake_word():
        """
        Function called when the wake word is detected.
        """
        rec = record()
        prediction = model.predict([features.mean_mffcs(data, SAMPLERATE)])
        if len(prediction) > 0:
            logging.info("Intent '" + prediction[0] + "' detected.")
            intent_payload = json.dumps({'intent': {'intentName': prediction[0]}})
            mqtt.publish('speech/intent' + prediction[0], intent_payload)
        else:
            logging.debug("No intent detected, maybe the threshold is too low ?")


    def on_noise(data):
        """
        Function called when some noise is detected in the microphone.
        """
        data = np.concatenate(data)
        prediction = model.predict([features.mean_mffcs(data, SAMPLERATE)])
        if len(prediction) > 0 and prediction[0] == reader.WAKE_WORD:
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
            print()


    #print(model.predict([mean_mffcs('test.wav')]))
    #print(model.predict_proba([mean_mffcs('test.wav')]))

    #model.save('knn_model.joblib')

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
	