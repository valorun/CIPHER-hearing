from os.path import join, dirname

MQTT_CLIENT_ID='hearing'
MQTT_BROKER_URL='localhost'
MQTT_BROKER_PORT=1883 # default is 1883

LOG_FILE=join(dirname(__file__), 'app.log')

ICON='fas fa-microphone'

TRAINED_MODEL_PATH=join(dirname(__file__), 'trained_model')
TRAINED_MODEL_DATA_PATH=join(dirname(__file__), 'model_data.json')

NOISE_THRESHOLD = 0.15
DETECT_THRESHOLD = 0.5
SPEECH_TIMEOUT = 1

WAKE_WORD_CLASS = 'WAKE_WORD'
