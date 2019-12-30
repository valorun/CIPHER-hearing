#!/usr/bin/python3
# coding: utf-8
from features import mean_mffcs
from models import KNNModel
from reader import get_dataset
from record import record

#dataset = get_dataset(mean_mffcs)
model = KNNModel(2)
#model.train(dataset)
model.load('knn_model.joblib')
record('test.wav')
print(model.predict([mean_mffcs('test.wav')]))

#model.save('knn_model.joblib')
