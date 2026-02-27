import torch
import torch.nn as nn


class SEBlock(nn.Module):
    def __init__(self, channel):
        super().__init__()
        self.fc = nn.Sequential(
            nn.Linear(channel, channel // 8),
            nn.ReLU(),
            nn.Linear(channel // 8, channel),
            nn.Sigmoid()
        )

    def forward(self, x):
        # calculate the importance weight of each properties
        weight = self.fc(x)
        # put weight back into original property value
        return x * weight


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
        self.se1=SEBlock(256)

        self.block2 = nn.Sequential(
            nn.Linear(256, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Dropout(0.4)
        )
        self.shortcut2 = nn.Linear(256,128)
        self.se2=SEBlock(128)
        # for feeding
        self.feeding_branch = nn.Sequential(
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(64, 32),
            nn.ReLU()
        )

        # for postcrandial
        self.post_branch = nn.Sequential(
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(64, 32),
            nn.ReLU()
        )

        # head of classification
        self.classifier = nn.Linear(128 + 32 + 32, 3)  # 主干 + 两个分支

    def forward(self, x):
        # first layer of residual:
        identity = self.shortcut1(x)
        out = self.block1(x)
        out = self.se1(out)
        x1 = out + identity  # add residual
        # second layer of residual:
        identity2 = self.shortcut2(x1)
        out2 = self.block2(x1)
        out2 = self.se2(out2)
        x2 = out2 + identity2   # add residual again


        # x1 = self.block1(x)
        # x2 = self.block2(x1)

        # pro features
        feeding_feat = self.feeding_branch(x2)
        post_feat = self.post_branch(x2)

        # feature combination
        combined = torch.cat([x2, feeding_feat, post_feat], dim=1)
        return self.classifier(combined)

