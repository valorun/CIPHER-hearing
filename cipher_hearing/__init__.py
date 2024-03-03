import json
import logging
import paho.mqtt.client as Mqtt
from os.path import exists
from logging.handlers import RotatingFileHandler
from logging.config import dictConfig
from .config import client_config

from .speech_recognizer import SpeechRecognizer
from .wakeword_detector import WakeDetector

mqtt = None

def create_app(debug=False):
    global mqtt

    mqtt = Mqtt.Client(Mqtt.CallbackAPIVersion.VERSION2, client_id=client_config.MQTT_CLIENT_ID)
   
    if not exists(client_config.WAKEWORD_MODEL_PATH):
        logging.error("No wakeword model found ! Exiting ...")
        exit(1)
    print(client_config.VOSK_MODEL_PATH)
    if not exists(client_config.VOSK_MODEL_PATH):
        logging.error("No vosk model found ! Exiting ...")
        exit(1)
    wakeword_detector = None
    wakeword_detector = WakeDetector(client_config.RAVEN_PATH, 
                                    client_config.WAKEWORD_MODEL_PATH, 
                                    client_config.WAKEWORD_THRESHOLD, 
                                    client_config.SAMPLERATE)
    recognizer = SpeechRecognizer(client_config.VOSK_MODEL_PATH, 
                                    wakeword_detector, 
                                    mqtt, 
                                    client_config.SAMPLERATE)

    def on_disconnect(client, userdata, flags, reason_code, properties):
        """
        Function called when the client disconnect from the server.
        """
        recognizer.stop()
        logging.info("Disconnected from server")

    def on_connect(client, userdata, flags, reason_code, properties):
        """
        Function called when the client connect to the server.
        """
        logging.info("Connected with result code " + str(reason_code))
        client.subscribe('server/connect')
        client.subscribe('client/' + client_config.MQTT_CLIENT_ID + '/#')
        notify_server_connection()
        recognizer.start()

    def notify_server_connection():
        """
        Give all information about the connected client to the server when needed.
        """
        mqtt.publish('client/connect', json.dumps({'id':client_config.MQTT_CLIENT_ID, 'icon':client_config.ICON}))

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
        elif topic == 'client/' + client_config.MQTT_CLIENT_ID +'/start':
            recognizer.start()
            logging.info("Started speech recognition")
        elif topic == 'client/' + client_config.MQTT_CLIENT_ID + '/stop':
            recognizer.stop()
            logging.info("Stopped speech recognition")
        elif topic == 'client/' + client_config.MQTT_CLIENT_ID + '/exit':
            exit(0)

    mqtt.on_connect = on_connect
    mqtt.on_message = on_message
    mqtt.on_disconnect = on_disconnect
    #mqtt.enable_logger()

    mqtt.connect(client_config.MQTT_BROKER_URL, client_config.MQTT_BROKER_PORT, 60)

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
                'filename': client_config.LOG_FILE,
                'maxBytes': 1024
            }
        },

        'root': {
            'level': log_level,
            'handlers': ['default', 'file']
        },
    })
