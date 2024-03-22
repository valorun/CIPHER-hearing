import numpy as np
from datasets import load_dataset, Audio, concatenate_datasets
# %%
dataset = load_dataset('mozilla-foundation/common_voice_16_1', data_dir='fr/partial-validation', revision='refs/convert/parquet', split='train')

dataset.cleanup_cache_files()
# %%

def audio_to_chunks(examples, chunk_duration=1000):
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
            #chunk = chunk * (2 ** 31 - 1)
            # audio = AudioSegment(
            #     data=chunk.astype(np.int32).tobytes(),
            #     sample_width=4,
            #     frame_rate=audio_data['sampling_rate'],
            #     channels=1  # Mono
            # )
        
            # audio.export(f'test{i}.mp3', format='mp3')
        #chunks += [chunk.get_array_of_samples() for chunk in make_chunks(audio, chunk_duration)]
    return {'audio': chunks, 'label': 0}
# %%
dataset.dataset_size
# %%
chunks_df = dataset.map(audio_to_chunks, remove_columns=dataset.column_names, batched=True)
# %%
chunks_df = chunks_df.train_test_split(test_size=0.1)
# %%
chunks_df['train'].to_parquet('common_voices_train.parquet')
chunks_df['test'].to_parquet('common_voices_test.parquet')
# %%
len(chunks_df)
# %%
chunks_df.to_parquet('data/common_voices_test.parquet')

# %%
chunks_df = load_dataset('parquet', data_files='data/common_voices_test.parquet', split='train')
chunks_df = chunks_df.filter(lambda x: x['audio']['array'].shape[0] >= 48000)

# %%
chunks_df
# %%
test_data[86915]['audio']['array'].shape
# %%
pos_test_data = load_dataset('parquet', data_files='wakeword_train.parquet', split='train')
neg_test_data = load_dataset('parquet', data_files='common_voices_train.parquet', split='train')

# merge positive and negative data
test_data = concatenate_datasets([neg_test_data, pos_test_data])
# %%
test_data
