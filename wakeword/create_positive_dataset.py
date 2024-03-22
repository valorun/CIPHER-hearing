from os import listdir, mkdir
from os.path import exists

from datasets import Audio, Dataset

dataset = Dataset.from_dict({'audio': [f'records/{f}' for f in listdir('records/')]}).cast_column('audio', Audio(sampling_rate=48000))
dataset = dataset.map(lambda x: {'audio': {'array': x['audio']['array'], 'sampling_rate': x['audio']['sampling_rate']}})
dataset = dataset.map(lambda x: {'label': 1})

dataset = dataset.train_test_split(test_size=0.1)

if not exists('data'):
    mkdir('data')

dataset['train'].to_parquet('data/wakeword_train.parquet')
dataset['test'].to_parquet('data/wakeword_test.parquet')
