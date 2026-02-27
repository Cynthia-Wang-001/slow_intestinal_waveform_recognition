import torch
import torch.nn as nn



class ResidualMLP(nn.Module):
    def __init__(self, in_dim):
        super().__init__()

        self.block1 = nn.Sequential(
            nn.Linear(in_dim, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(),
            nn.Dropout(0.4)
        )
        # definition of shoutcut:in_dim(14 features)->256, add to block1 output
        self.shortcut1 = nn.Linear(in_dim, 256)

        self.block2 = nn.Sequential(
            nn.Linear(256, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Dropout(0.1)
        )
        self.shortcut2 = nn.Linear(256,128)


        # head of classification
        self.classifier = nn.Linear(128, 2)  # 主干 + 两个分支

    def forward(self, x):
        # first layer of residual:
        identity = self.shortcut1(x)
        out = self.block1(x)

        x1 = out + identity  # add residual
        # second layer of residual:
        identity2 = self.shortcut2(x1)
        out2 = self.block2(x1)

        x2 = out2 + identity2   # add residual again


        # x1 = self.block1(x)
        # x2 = self.block2(x1)

        return self.classifier(x2)

