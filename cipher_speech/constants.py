import os

MQTT_CLIENT_ID='recognizer'
MQTT_BROKER_URL='localhost'
MQTT_BROKER_PORT=1883 # default is 1883

LOG_FILE=os.path.join(os.path.dirname(__file__), 'app.log')

DATASET_PATH = os.path.join(os.path.dirname(__file__), 'dataset')
