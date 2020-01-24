from os.path import join, dirname
MQTT_CLIENT_ID='recognizer'
MQTT_BROKER_URL='localhost'
MQTT_BROKER_PORT=1883 # default is 1883

LOG_FILE=join(dirname(__file__), 'app.log')

DATASET_PATH=join(dirname(__file__), 'dataset/')

TRAINED_MODEL_PATH=join(dirname(__file__), 'knn_model.joblib')