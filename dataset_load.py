import torch
from torch.utils.data import Dataset
import scipy.io as sio
import numpy as np
import os
from scipy import signal
import json

DATASET_JSON_PATH = "/Users/cynthiawang/Desktop/GI_lab/data_sync/data_segmented/dataset.json"

def count_dataset_distribution(json_path=DATASET_JSON_PATH):
    if not os.path.exists(json_path):
        print(f"wrong:no datasetjson file {json_path}")
        return

    with open(json_path, 'r') as f:
        data = json.load(f)

    # calculate
    def get_counts(samples):
        # 0: fast, 1: postprandial
        fast = sum(1 for item in samples if item['label'] == 0)
        post = sum(1 for item in samples if item['label'] == 1)
        return fast, post

    # in train:
    train_fast, train_post = get_counts(data['train'])
    # in test:
    test_fast, test_post = get_counts(data['test'])

    print("-" * 30)
    print(f"{'categories':<15} | {'train':<8} | {'val':<8}")
    print("-" * 30)
    print(f"{'Fast (0)':<15} | {train_fast:<8} | {test_fast:<8}")
    print(f"{'Post (1)':<15} | {train_post:<8} | {test_post:<8}")
    print("-" * 30)
    print(f"overall: {train_fast + train_post + test_fast + test_post}")


class SlowWaveDataset(Dataset):
    def __init__(self, json_list, root_dir, window_size=6000, is_train=True):
        self.samples = json_list
        self.root_dir = root_dir
        self.window_size = window_size
        self.is_train = is_train
        self.fs_original = 200  # I dont know this sampling rate but i think maybe it's 200hz
        self.fs_new = 20 # downsampling!
        self.lowcut = 0.1
        self.highcut = 2.0
        # bandpass filter
        self.b, self.a = signal.butter(4, [self.lowcut, self.highcut], fs=self.fs_original, btype='band')

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        item = self.samples[idx]
        file_path = os.path.join(self.root_dir, item['file_name'])

        try:
            mat_data = sio.loadmat(file_path)
            raw_signal = mat_data['segment_data'].flatten()
            #filter(no delay)
            filtered_signal = signal.filtfilt(self.b, self.a, raw_signal)
            down_factor = self.fs_original // self.fs_new
            downsampled_signal = signal.decimate(filtered_signal, down_factor)

        except Exception as e:
            return torch.zeros(1, self.window_size), torch.tensor(item['label'])

        #windows
        total_len = len(downsampled_signal)
        if total_len > self.window_size:
            if self.is_train:
                start = np.random.randint(0, total_len - self.window_size)
            else:
                start = (total_len - self.window_size) // 2
            segment = filtered_signal[start: start + self.window_size]
        else:
            segment = np.pad(filtered_signal, (0, self.window_size - total_len), 'constant')

        #standardlization?
        #segment = (segment - np.mean(segment)) / (np.std(segment) + 1e-8)
        segment = segment / 10
        segment_tensor = torch.FloatTensor(segment).unsqueeze(0)
        label_tensor = torch.tensor(item['label']).long()

        return segment_tensor, label_tensor

if __name__ == "__main__":
    count_dataset_distribution()