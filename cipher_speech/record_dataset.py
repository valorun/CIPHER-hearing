from record import record
from .constants import DATASET_PATH
from os.path import join, exists
from os import listdir

if __name__ == '__main__':
    n_samples = 1
    dir_number = 2

    samples_path = join(DATASET_PATH, str(dir_number))

    i = 0
    for n in range(n_samples):
        while exists(join(samples_path, str(i) + '.wav')):
            i += 1
        new_file_name = join(samples_path, str(i) + '.wav')
        record(new_file_name)