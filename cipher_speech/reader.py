import json
import os
import numpy as np
from librosa.core import load
from sklearn.model_selection import train_test_split
from keras.utils import to_categorical
from .constants import DATASET_PATH, SAMPLERATE

def get_labels():
    """
    Get unique labels ordered by their index in the file listing all classes.
    """
    with open(os.path.join(DATASET_PATH, 'classes.json'), 'r') as filename:
        return list(dict.fromkeys(json.load(filename).values()))


def get_dataset(feature, pre_process, split_ratio=0.8, random_state=44):
    """
    Create a dataset from all the samples and their annotation.
    """
    with open(os.path.join(DATASET_PATH, 'classes.json'), 'r') as filename:
        dataset_json = json.load(filename)

        X = None
        y = np.array([])

        labels = get_labels()

        for dir_name, class_name in dataset_json.items():
            class_path = os.path.join(DATASET_PATH, str(dir_name))
            for file in os.listdir(class_path):
                if file.endswith('.wav'):
                    data, rate = load(os.path.join(class_path, file), sr=SAMPLERATE)
                    y = np.hstack((y, labels.index(class_name)))
                    if X is None:
                        X = np.array([feature(pre_process(data))])
                    else:
                        X = np.append(X, [feature(pre_process(data))], axis=0)

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size= (1 - split_ratio), random_state=random_state, shuffle=True)
        #X_train = X_train.reshape(X_train.shape[0], X_train.shape[1], X_train.shape[2], CHANNELS)
        #X_test = X_test.reshape(X_test.shape[0], X_test.shape[1], X_test.shape[2], CHANNELS)
        y_train_hot = to_categorical(y_train)
        y_test_hot = to_categorical(y_test)

        return X_train, X_test, y_train_hot, y_test_hot