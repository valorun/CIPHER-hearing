from os import mkdir
from os.path import exists

import numpy as np
from datasets import load_dataset

dataset = load_dataset('mozilla-foundation/common_voice_16_1', data_dir='fr/partial-validation', revision='refs/convert/parquet', split='train')
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
    return {'audio': chunks, 'label': 0}

chunks_df = dataset.map(audio_to_chunks, remove_columns=dataset.column_names, batched=True)
chunks_df = chunks_df.train_test_split(test_size=0.1)

if not exists('data'):
    mkdir('data')

chunks_df['train'].to_parquet('data/common_voices_train.parquet')
chunks_df['test'].to_parquet('data/common_voices_test.parquet')
