#!/usr/bin/python3
# coding: utf-8
import numpy as np
from keras.models import Sequential
from keras.layers import Dense, Dropout, Flatten, Conv2D, MaxPooling2D, LSTM
from cipher_speech.reader import get_dataset, get_labels
from cipher_speech.features import N_SAMPLE_MFCCS, N_MFCC, SELECTED_FEATURE
from cipher_speech.constants import CHANNELS, TRAINED_MODEL_PATH
from cipher_speech.processes import pre_process

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
    X_train, X_test, y_train, y_test = get_dataset(SELECTED_FEATURE, pre_process)
    print("Training model ...")

    epochs = 60
    batch_size = 30
    print(X_train.shape)

    model.fit(X_train, y_train, batch_size=batch_size, epochs=epochs, verbose=1, validation_data=(X_test, y_test))
    model.save(TRAINED_MODEL_PATH)