#!/usr/bin/python3
import json
import os
from models import LabeledDataset

DATASET_PATH = os.path.join(os.path.dirname(__file__), 'dataset')

def get_dataset(feature):
    with open(os.path.join(DATASET_PATH, 'classes.json'), 'r') as filename:
        dataset_json = json.load(filename)
        dataset = []
        labels = []
        for class_name, class_path in dataset_json.items():
            class_path = os.path.join(DATASET_PATH, class_path)
            for file in os.listdir(class_path):
                if file.endswith('.wav'):
                    dataset.append(feature(os.path.join(class_path, file)))
                    labels.append(class_name)
        return LabeledDataset(dataset, labels)