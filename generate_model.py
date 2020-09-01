#!/usr/bin/python3
# coding: utf-8
import numpy as np
import json
from keras.models import Sequential
from keras.layers import Dense, LSTM
from librosa.core import load
from sklearn.model_selection import train_test_split
from keras.utils import to_categorical
from os.path import join
from pathlib import Path
from os import listdir
from cipher_haring.features import N_SAMPLE_MFCCS, N_MFCC, mfccs
from constants import SAMPLERATE, CHANNELS, DEFAULT_SAMPLE_DURATION, TRAINED_MODEL_PATH, TRAINED_MODEL_DATA_PATH, DATASET_PATH
from cipher_haring.processes import pre_process

def get_labels():
    """
    Get unique labels ordered by their index in the file listing all classes.
    """
    with open(join(DATASET_PATH, 'classes.json'), 'r') as filename:
        return list(dict.fromkeys(json.load(filename).values()))

def get_dataset(split_ratio=0.8, random_state=44):
    """
    Create a dataset from all the samples and their annotation.
    """
    with open(join(DATASET_PATH, 'classes.json'), 'r') as filename:
        dataset_json = json.load(filename)

        X = None
        y = np.array([])

        labels = get_labels()

        for dir_name, class_name in dataset_json.items():
            class_path = join(DATASET_PATH, str(dir_name))
            for file in listdir(class_path):
                if file.endswith('.wav'):
                    data, _rate = load(join(class_path, file), sr=SAMPLERATE)
                    y = np.hstack((y, labels.index(class_name)))
                    file_feature = [mfccs(pre_process(data, SAMPLERATE, DEFAULT_SAMPLE_DURATION), SAMPLERATE)]
                    if X is None:
                        X = np.array(file_feature)
                    else:
                        X = np.append(X, file_feature, axis=0)

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size= (1 - split_ratio), random_state=random_state, shuffle=True)
        #X_train = X_train.reshape(X_train.shape[0], X_train.shape[1], X_train.shape[2], CHANNELS)
        #X_test = X_test.reshape(X_test.shape[0], X_test.shape[1], X_test.shape[2], CHANNELS)
        y_train_hot = to_categorical(y_train)
        y_test_hot = to_categorical(y_test)

        return X_train, X_test, y_train_hot, y_test_hot

def get_model():
    model = Sequential()
    model.add(LSTM(128, activation='tanh', input_shape=(N_SAMPLE_MFCCS, N_MFCC)))
    model.add(Dense(len(get_labels()), activation='softmax'))
    model.compile(loss='categorical_crossentropy',
                optimizer='adam',
                metrics=['accuracy'])
    return model

if __name__ == '__main__':
    print("Creating model ...")
    model = get_model()
    print("Extracting dataset ...")
    X_train, X_test, y_train, y_test = get_dataset()
    print("Training model ...")

    epochs = 70
    batch_size = 50
    print(X_train.shape)

    model.fit(X_train, y_train, batch_size=batch_size, epochs=epochs, verbose=1, validation_data=(X_test, y_test))
    
    print("Saving model ...")
    model.save(TRAINED_MODEL_PATH)

    print("Saving model data ...")
    data = {}
    data['intents'] = get_labels()
    data['samplerate'] = SAMPLERATE
    data['channels'] = CHANNELS
    data['default_sample_duration'] = DEFAULT_SAMPLE_DURATION
    with open(TRAINED_MODEL_DATA_PATH, 'w') as file:
        file.write(json.dumps(data))