import json
import logging
import paho.mqtt.client as Mqtt
import numpy as np
from os.path import exists
from logging.handlers import RotatingFileHandler
from logging.config import dictConfig
from keras.models import load_model

from .constants import MQTT_CLIENT_ID, MQTT_BROKER_URL, MQTT_BROKER_PORT, LOG_FILE, TRAINED_MODEL_PATH, TRAINED_MODEL_DATA_PATH, WAKE_WORD_CLASS, DETECT_THRESHOLD
from .speech_recognizer import SpeechRecognizer

mqtt = None

def create_app(debug=False):
    global mqtt

    mqtt = Mqtt.Client(MQTT_CLIENT_ID)
    model = None
    model_data = None
   
    if exists(TRAINED_MODEL_PATH):
        logging.info("Loading model ...")
        model = load_model(TRAINED_MODEL_PATH)
    else:
        logging.error("No model found ! Exiting ...")
        exit(1)

    if exists(TRAINED_MODEL_PATH):
        logging.info("Loading model data ...")
        with open(TRAINED_MODEL_DATA_PATH) as file:
            model_data = json.load(file)
    else:
        logging.error("No model data found ! Exiting ...")
        exit(1)

    recognizer = SpeechRecognizer(model, model_data, mqtt)

    def on_disconnect(client, userdata, rc):
        """
        Function called when the client disconnect from the server.
        """
        recognizer.stop()
        logging.info("Disconnected from server")

    def on_connect(client, userdata, flags, rc):
        """
        Function called when the client connect to the server.
        """
        logging.info("Connected with result code " + str(rc))
        client.subscribe('server/connect')
        client.subscribe('speech/start')
        client.subscribe('speech/stop')
        recognizer.start()


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
            recognizer.start()
        elif topic == 'speech/stop':
            recognizer.stop()



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