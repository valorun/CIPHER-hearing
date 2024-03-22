#!/bin/bash

export HSA_OVERRIDE_GFX_VERSION=10.3.0
export CUDA_VISIBLE_DEVICES=0

../venv/bin/python train.py --save_checkpoint_path checkpoint/ --train_positive_data data/wakeword_train.parquet --test_positive_data data/wakeword_test.parquet --train_negative_data data/common_voices_train.parquet --test_negative_data data/common_voices_test.parquet --batch_size 256
