#!/bin/bash

../rustpotter-cli train -t small --train-dir records/train --test-dir records/test --test-epochs 10 --epochs 2500 -l 0.017 trained-small.rpw
