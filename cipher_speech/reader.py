#!/usr/bin/python3
import json
import os
from librosa.core import load
from .constants import DATASET_PATH
from .models import LabeledDataset

WAKE_WORD = 'WAKE_WORD'

def get_dataset(feature, pre_process):
    """
    Create a dataset from all the samples and their annotation.
    """
    with open(os.path.join(DATASET_PATH, 'classes.json'), 'r') as filename:
        dataset_json = json.load(filename)
        dataset = []
        labels = []
        for class_name, class_path in dataset_json.items():
            class_path = os.path.join(DATASET_PATH, class_path)
            for file in os.listdir(class_path):
                if file.endswith('.wav'):
                    data, rate = load(os.path.join(class_path, file), sr=None)
                    dataset.append(feature(pre_process(data, rate), rate))
                    labels.append(class_name)
        return LabeledDataset(dataset, labels)