from os.path import join, dirname

DATASET_PATH=join(dirname(__file__), 'dataset')

TRAINED_MODEL_PATH=join(join(dirname(__file__), 'cipher_speech'), 'trained_model')
TRAINED_MODEL_DATA_PATH=join(join(dirname(__file__), 'cipher_speech'), 'model_data.json')

SAMPLERATE = 16000  # Sample rate
CHANNELS = 1
DEFAULT_SAMPLE_DURATION = 3  # Duration of recording