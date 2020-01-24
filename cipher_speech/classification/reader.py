#!/usr/bin/python3
import json
import soundfile as sf
import os
from cipher_speech.constants import DATASET_PATH
from .models import LabeledDataset

WAKE_WORD = 'WAKE_WORD'

def get_dataset(feature):
    """
    Create a dataset from all the samples and their annotation.
    The function extract feature according to the function in parameter.
    """
    with open(os.path.join(DATASET_PATH, 'classes.json'), 'r') as filename:
        dataset_json = json.load(filename)
        dataset = []
        labels = []
        for class_name, class_path in dataset_json.items():
            class_path = os.path.join(DATASET_PATH, class_path)
            for file in os.listdir(class_path):
                if file.endswith('.wav'):
                    (data, rate) = sf.read(os.path.join(class_path, file))
                    dataset.append(feature(data, rate))
                    labels.append(class_name)
        return LabeledDataset(dataset, labels)