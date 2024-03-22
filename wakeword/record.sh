#!/bin/bash
#
WAKEWORD="Clarius"
WAKEWORD_FILENAME="${WAKEWORD// /_}"


# take 10 records, waiting one second after each.
# echo "Recording wakeword sample files"
# sleep 2
# for i in {0..20}; do
#     arecord -r 8000 -f S16_LE -c 1 -d 2 records/wakeword/$WAKEWORD_FILENAME$i.wav
#     sleep 1
# done

echo "Recording environment sample files"
sleep 2
for i in {0..20}; do
    arecord -r 8000 -f S16_LE -c 1 -d 2 records/environment/noise$i.wav
    sleep 1
done
