#!/bin/bash

export HSA_OVERRIDE_GFX_VERSION=10.3.0
export CUDA_VISIBLE_DEVICES=0
export KERAS_BACKEND="torch"
../venv/bin/python train.py --save_checkpoint_path checkpoint/ --train_data_json data/wakeword_train.json --test_data_json data/wakeword_test.json --sample_rate 8000 --batch_size 512 --eval_batch_size 512
