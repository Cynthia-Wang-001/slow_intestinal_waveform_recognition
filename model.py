import torch
import torch.nn as nn


class ResNetBlock1D(nn.Module):
    """Basic Residual Block for 1D signal processing"""

    def __init__(self, in_channels, out_channels, kernel_size=7, stride=1):
        super().__init__()

        self.conv1 = nn.Conv1d(
            in_channels,
            out_channels,
            kernel_size,
            stride=stride,
            padding=kernel_size // 2
        )

        self.bn1 = nn.BatchNorm1d(out_channels)

        self.relu = nn.ReLU()

        self.conv2 = nn.Conv1d(
            out_channels,
            out_channels,
            kernel_size,
            stride=1,
            padding=kernel_size // 2
        )

        self.bn2 = nn.BatchNorm1d(out_channels)

        self.shortcut = nn.Sequential()

        if stride != 1 or in_channels != out_channels:

            self.shortcut = nn.Sequential(
                nn.Conv1d(in_channels, out_channels, kernel_size=1, stride=stride),
                nn.BatchNorm1d(out_channels)
            )

    def forward(self, x):

        residual = self.shortcut(x)

        out = self.relu(self.bn1(self.conv1(x)))

        out = self.bn2(self.conv2(out))

        out += residual

        return self.relu(out)


class SlowWaveNet(nn.Module):

    def __init__(self, num_classes=2, feature_dim=10): #8 features

        super().__init__()

        # initial convolution
        self.init_conv = nn.Sequential(
            nn.Conv1d(1, 32, kernel_size=31, stride=2, padding=3),
            nn.BatchNorm1d(32),
            nn.ReLU()
        )

        # resnet blocks
        self.layer1 = ResNetBlock1D(32, 64, stride=2)
        self.layer2 = ResNetBlock1D(64, 128, stride=2)
        self.layer3 = ResNetBlock1D(128, 256, stride=2)

        # pooling
        self.gap = nn.AdaptiveAvgPool1d(1)

        self.dropout = nn.Dropout(0.4)

        # CNN feature + handcrafted feature
        self.fc = nn.Linear(256 + feature_dim, num_classes)

    def forward(self, x, feature):

        x = self.init_conv(x)

        x = self.layer1(x)

        x = self.layer2(x)

        x = self.layer3(x)

        x = self.gap(x)

        x = x.view(x.size(0), -1)

        x = self.dropout(x)

        # concatenate CNN feature + handcrafted feature
        x = torch.cat([x, feature], dim=1)

        return self.fc(x)