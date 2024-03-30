from os import mkdir
from os.path import exists

import numpy as np
from datasets import load_dataset
import soundfile as sf

dataset = load_dataset('mozilla-foundation/common_voice_16_1', data_dir='fr/partial-validation', revision='refs/convert/parquet', split='train[:2%]')
dataset.cleanup_cache_files()

def audio_to_chunks(examples, chunk_duration=2000):
    chunks = []
    for audio_data in examples['audio']:
        # Audio duration based on sampling rate
        #duration = audio_data['array'].shape[0] / audio_data['sampling_rate']

        # Make chunks based on chunk duration and sampling rate. 
        for i in range(0, len(audio_data['array']),
                       int(np.floor(chunk_duration / 1000 * audio_data['sampling_rate']))):
            chunk = audio_data['array'][i:i + int(np.floor(chunk_duration / 1000 * audio_data['sampling_rate']))]
            # Keep only chunks that are long enough
            if len(chunk) == int(np.floor(chunk_duration / 1000 * audio_data['sampling_rate'])):
                chunks.append({'array': chunk,
                               'sampling_rate': audio_data['sampling_rate']})
    return {'audio': chunks, 'label': np.repeat(0, len(chunks))}

chunks_df = dataset.map(audio_to_chunks, remove_columns=dataset.column_names, batched=True, num_proc=4, batch_size=256)
chunks_df = chunks_df.train_test_split(test_size=0.1)

if not exists('records'):
    mkdir('records')
    mkdir('records/train')
    mkdir('records/test')

for i, row in enumerate(chunks_df['train']):
    sf.write(f'records/train/{i}.wav', row['audio']['array'], row['audio']['sampling_rate'])

for i, row in enumerate(chunks_df['test']):
    sf.write(f'records/test/{i}.wav', row['audio']['array'], row['audio']['sampling_rate'])
