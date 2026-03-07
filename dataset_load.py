import json
import os
import numpy as np
import scipy.io as sio
import torch
from scipy import signal
from scipy.stats import skew,kurtosis
from torch.utils.data import Dataset


DATASET_JSON_PATH = "/Users/cynthiawang/Desktop/GI_lab/data_sync/data_segmented/dataset.json"
#features: 8
#amplitude, std, dominant_freq, mean_spike_interval, skewness,rms, band_power,kurtosis

def count_dataset_distribution(json_path=DATASET_JSON_PATH):
    if not os.path.exists(json_path):
        print(f"wrong:no datasetjson file {json_path}")
        return

    with open(json_path, 'r') as f:
        data = json.load(f)

    def get_counts(samples):
        fast = sum(1 for item in samples if item['label'] == 0)
        post = sum(1 for item in samples if item['label'] == 1)
        return fast, post

    train_fast, train_post = get_counts(data['train'])
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

        self.fs_original = 200
        self.fs_new = 20

        self.lowcut = 0.1
        self.highcut = 2.0

        self.b, self.a = signal.butter(
            4,
            [self.lowcut, self.highcut],
            fs=self.fs_original,
            btype='band'
        )

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):

        item = self.samples[idx]
        file_path = os.path.join(self.root_dir, item['file_name'])

        try:

            mat_data = sio.loadmat(file_path)

            raw_signal = mat_data['segment_data'].flatten()

            filtered_signal = signal.filtfilt(self.b, self.a, raw_signal)

            down_factor = self.fs_original // self.fs_new

            downsampled_signal = signal.decimate(filtered_signal, down_factor)

        except Exception:
            return torch.zeros(1, self.window_size), torch.zeros(5), torch.tensor(item['label'])

        total_len = len(downsampled_signal)

        if total_len > self.window_size:

            if self.is_train:
                start = np.random.randint(0, total_len - self.window_size)
            else:
                start = (total_len - self.window_size) // 2

            segment = downsampled_signal[start:start + self.window_size]

        else:

            segment = np.pad(
                downsampled_signal,
                (0, self.window_size - total_len),
                'constant'
            )

        if self.is_train:

            scale = np.random.uniform(0.9, 1.1)
            segment = segment * scale

            shift = np.random.randint(-300, 300)
            segment = np.roll(segment, shift)

        # ---------- feature extraction ----------

        amplitude = np.max(segment) - np.min(segment)

        std = np.std(segment)

        fft = np.fft.rfft(segment)

        freqs = np.fft.rfftfreq(len(segment), d=1 / self.fs_new)

        dominant_freq = freqs[np.argmax(np.abs(fft))]

        # spike interval feature
        peaks, _ = signal.find_peaks(segment, distance=self.fs_new)

        if len(peaks) > 1:
            isi = np.diff(peaks) / self.fs_new
            mean_spike_interval = np.mean(isi)
        else:
            mean_spike_interval = 0.0

        # 5 skewness
        skewness = skew(segment)

        #6 RMS
        rms = np.sqrt(np.mean(segment ** 2))

        # kurtosis
        kurt = kurtosis(segment)

        # band power (0.02–0.1 Hz)
        freqs_psd, psd = signal.welch(segment, fs=self.fs_new, nperseg=256)

        band_mask = (freqs_psd >= 0.02) & (freqs_psd <= 0.1)

        band_power = np.trapz(psd[band_mask], freqs_psd[band_mask])


        #9 spectral centroid
        spectral_centroid = np.sum(freqs * np.abs(fft)) / (np.sum(np.abs(fft)) + 1e-8)

        # 10 zero-crossing rate
        zero_crossings = np.where(np.diff(np.sign(segment)))[0]
        zero_crossing_rate = len(zero_crossings) / len(segment)



        feature = np.array(
            [
                amplitude,
                std,
                dominant_freq,
                mean_spike_interval,
                skewness,
                rms,
                band_power,
                kurt,
                spectral_centroid,
                zero_crossing_rate
            ],
            dtype=np.float32
        )


        # ---------- normalization ----------

        segment = (segment - np.mean(segment)) / (np.std(segment) + 1e-8)

        segment_tensor = torch.FloatTensor(segment).unsqueeze(0)

        feature_tensor = torch.FloatTensor(feature)

        label_tensor = torch.tensor(item['label']).long()

        return segment_tensor, feature_tensor, label_tensor


if __name__ == "__main__":
    count_dataset_distribution()