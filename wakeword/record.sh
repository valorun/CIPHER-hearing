#!/bin/bash
#
WAKEWORD="Clarius"
WAKEWORD_FILENAME="[${WAKEWORD// /_}]"

if [ "$1" = "test" ]; then
    FOLDER="records/test"
else
    FOLDER="records/train"
fi

if [ ! -d "records" ]; then
    mkdir records
fi
if [ ! -d "records/train" ]; then
    mkdir records/train
fi
if [ ! -d "records/test" ]; then
    mkdir records/test
fi

# take 10 records, waiting one second after each.
echo "Recording wakeword sample files"
sleep 2
for i in {0..10}; do
    arecord -r 16000 -f S16_LE -c 1 -d 2 $FOLDER/$WAKEWORD_FILENAME$i.wav
    sleep 1
done

echo "Recording environment sample files"
sleep 2
for i in {0..10}; do
    arecord -r 16000 -f S16_LE -c 1 -d 2 $FOLDER/noise$i.wav
    sleep 1
done
