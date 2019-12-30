from record import record
from reader import DATASET_PATH

n_samples = 5

for n in range(n_samples):
    record(DATASET_PATH + str(n) + '.wav')