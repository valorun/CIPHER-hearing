from os.path import join, dirname

MQTT_CLIENT_ID='hearing'
MQTT_BROKER_URL='localhost'
MQTT_BROKER_PORT=1883 # default is 1883

LOG_FILE=join(dirname(__file__), 'app.log')

ICON='fas fa-microphone'

VOSK_MODEL_PATH=join(dirname(dirname(__file__)), 'vosk-model-fr-0.6-linto-2.0.0')
RAVEN_PATH=join(dirname(dirname(__file__)), 'rhasspy-wake-raven')
WAKEWORD_MODEL_PATH=join(RAVEN_PATH, 'keyword-dir')
SAMPLERATE=16000

NOISE_THRESHOLD=70
WAKEWORD_THRESHOLD=0.4
STT_THRESHOLD=0.5
SPEECH_TIMEOUT=1
