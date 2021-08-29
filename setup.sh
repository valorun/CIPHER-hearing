# install raven
git clone https://github.com/rhasspy/rhasspy-wake-raven.git
cd rhasspy-wake-raven
./configure
make
make install

# record templates, at least 3
arecord -r 16000 -f S16_LE -c 1 -t raw | \
    bin/rhasspy-wake-raven --record keyword-dir/

#arecord -r 16000 -f S16_LE -c 1 -t raw | \
#    bin/rhasspy-wake-raven --keyword keyword-dir/

# install vosk
https://alphacephei.com/vosk/models/vosk-model-fr-0.6-linto-2.2.0.zip
unzip vosk-model-fr-0.6-linto-2.2.0.zip


python -m snips_nlu download fr
python -m snips-nlu generate-dataset fr dataset.yaml > dataset.json

