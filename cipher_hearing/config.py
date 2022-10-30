from os.path import isfile, join, exists, dirname
from configparser import ConfigParser, _UNSET
from .constants import CONFIG_FILE

class ConfigFile(ConfigParser):
    def __init__(self, filepath):
        ConfigParser.__init__(self)
        self.filepath = filepath
        if exists(filepath):
            self.read(filepath)

class ClientConfig(ConfigFile):

    def __init__(self, filepath):
        ConfigFile.__init__(self, filepath)

        self.MQTT_CLIENT_ID = self.get('GENERAL', 'MQTT_CLIENT_ID', 
            fallback='UNKNOWN')

        self.ICON = self.get('GENERAL', 'ICON', 
            fallback='fas fa-microphone')
    
        self.MQTT_BROKER_URL = self.get('MQTT_BROKER', 'URL', 
            fallback='localhost')

        self.MQTT_BROKER_PORT = self.getint('MQTT_BROKER', 'PORT', 
            fallback=1883)

        self.LOG_FILE = self.get('GENERAL', 'LOG_FILE', 
            fallback=join(dirname(__file__), 'app.log'))


        self.RAVEN_PATH = self.get('WAKEWORD', 'RAVEN_PATH', 
            fallback=join(dirname(dirname(__file__)), 'rhasspy-wake-raven'))
        self.WAKEWORD_MODEL_PATH = self.get('WAKEWORD', 'RAVEN_PATH', 
            fallback=join(self.RAVEN_PATH, 'keyword-dir'))
        self.SAMPLERATE = self.getint('SOUND', 'SAMPLERATE', 
            fallback=16000)
        self.NLU_DATASET = self.get('RECOGNIZER', 'NLU_DATASET',
            fallback=join(dirname(dirname(__file__)), 'dataset/default.json'))
        self.VOSK_MODEL_PATH = self.get('RECOGNIZER', 'VOSK_MODEL_PATH',
            fallback=join(dirname(dirname(__file__)), 'vosk-model-fr-0.6-linto-2.2.0'))


        self.WAKEWORD_THRESHOLD = self.getfloat('WAKEWORD', 'WAKEWORD_THRESHOLD', 
            fallback=0.4)
        self.SPEECH_TIMEOUT = self.getfloat('SOUND', 'SPEECH_TIMEOUT', 
            fallback=2.0)

        self.DEBUG = self.getboolean('GENERAL', 'DEBUG', 
            fallback=False)


client_config = ClientConfig(CONFIG_FILE)