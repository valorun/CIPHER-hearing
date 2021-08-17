from os.path import join, dirname

MQTT_CLIENT_ID='hearing'
MQTT_BROKER_URL='localhost'
MQTT_BROKER_PORT=1883 # default is 1883

LOG_FILE=join(dirname(__file__), 'app.log')

ICON='fas fa-microphone'

VOSK_MODEL_PATH=join(dirname(__file__), 'vosk_model')
WAKEWORD_MODEL_PATH=join(dirname(__file__), 'wakeword_model')
WAKEWORD_MODEL='clarius'
SAMPLERATE=16000

NOISE_THRESHOLD=70
DETECT_THRESHOLD=0.5
SPEECH_TIMEOUT=1
