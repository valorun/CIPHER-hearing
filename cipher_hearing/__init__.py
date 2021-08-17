import json
import logging
import paho.mqtt.client as Mqtt
from os.path import exists
from logging.handlers import RotatingFileHandler
from logging.config import dictConfig

from .constants import MQTT_CLIENT_ID, MQTT_BROKER_URL, MQTT_BROKER_PORT, LOG_FILE, ICON, WAKEWORD_MODEL_PATH, VOSK_MODEL_PATH, SAMPLERATE
from .speech_recognizer import SpeechRecognizer

mqtt = None

def create_app(debug=False):
    global mqtt

    mqtt = Mqtt.Client(MQTT_CLIENT_ID)
   
    if not exists(WAKEWORD_MODEL_PATH):
        logging.error("No wakeword model found ! Exiting ...")
        exit(1)

    if not exists(VOSK_MODEL_PATH):
        logging.error("No vosk model found ! Exiting ...")
        exit(1)

    recognizer = SpeechRecognizer(VOSK_MODEL_PATH, WAKEWORD_MODEL_PATH, SAMPLERATE, mqtt)

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
        client.subscribe('client/' + MQTT_CLIENT_ID + '/#')
        notify_server_connection()
        #recognizer.start()

    def notify_server_connection():
        """
        Give all information about the connected client to the server when needed.
        """
        mqtt.publish('client/connect', json.dumps({'id':MQTT_CLIENT_ID, 'icon':ICON}))

    def on_message(client, userdata, msg):
        """
        Function called when a message is received from the server.
        """
        topic = msg.topic
        try:
            data = json.loads(msg.payload.decode('utf-8'))
        except ValueError:
            data = msg.payload.decode('utf-8')
        if topic == 'server/connect': #when the server start or restart, notify this client is connected
            notify_server_connection()
        elif topic == 'client/' + MQTT_CLIENT_ID +'/start':
            recognizer.start()
            logging.info("Started speech recognition")
        elif topic == 'client/' + MQTT_CLIENT_ID + '/stop':
            recognizer.stop()
            logging.info("Stopped speech recognition")
        elif topic == 'client/' + MQTT_CLIENT_ID + '/exit':
            exit(0)

    mqtt.on_connect = on_connect
    mqtt.on_message = on_message
    mqtt.on_disconnect = on_disconnect
    #mqtt.enable_logger()

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
            'format': '%(asctime)s %(levelname)-8s [%(name)s] %(message)s',
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