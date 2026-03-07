import json
import torch
import numpy as np
import random
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from dataset_load import SlowWaveDataset
from model import SlowWaveNet
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, classification_report
import os
from sklearn.metrics import f1_score

# --- Configuration ---
DATA_DIR = "/Users/cynthiawang/Desktop/GI_lab/data_sync/data_segmented"
JSON_PATH = "/Users/cynthiawang/Desktop/GI_lab/data_sync/data_segmented/dataset.json"
WINDOW_SIZE = 6000
BATCH_SIZE = 16
EPOCHS = 25
LEARNING_RATE = 1e-5
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu")
SAVE_PATH = "best_slow_wave_model.pth"

def train_one_epoch(model, dataloader, criterion, optimizer, device):
    model.train()
    running_loss, correct, total = 0.0, 0, 0
    for signals, features, labels in dataloader: #0306 add features
        signals, features, labels = signals.to(device), features.to(device), labels.to(device)
        optimizer.zero_grad()
        outputs = model(signals,features)
        loss = criterion(outputs, labels)
        loss.backward()
        #add gradient clipping for noise reduction!
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        optimizer.step()

        running_loss += loss.item() * signals.size(0)
        _, predicted = torch.max(outputs, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()
    return running_loss / total, correct / total


def validate(model, dataloader, criterion, device):
    model.eval()
    running_loss, correct, total = 0.0, 0, 0
    all_preds, all_labels = [], []
    with torch.no_grad():
        for signals, features,labels in dataloader:
            signals, features,labels = signals.to(device), features.to(device),labels.to(device)
            outputs = model(signals,features)
            loss = criterion(outputs, labels)
            running_loss += loss.item() * signals.size(0)
            _, predicted = torch.max(outputs, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
            all_preds.extend(predicted.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
    return running_loss / total, correct / total, all_labels, all_preds


def main():
    with open(JSON_PATH, 'r') as f:
        data_info = json.load(f)


    # def set_seed(seed=20):
    #     random.seed(seed)
    #     np.random.seed(seed)
    #     torch.manual_seed(seed)
    #     torch.cuda.manual_seed_all(seed)
    #
    # set_seed(20)

    weights = torch.tensor([1.0, 1.6],dtype=torch.float).to(DEVICE)
    train_criterion = nn.CrossEntropyLoss(weight=weights)
    val_criterion = nn.CrossEntropyLoss()

    train_set = SlowWaveDataset(data_info['train'], DATA_DIR, window_size=WINDOW_SIZE, is_train=True)
    test_set = SlowWaveDataset(data_info['test'], DATA_DIR, window_size=WINDOW_SIZE, is_train=False)

    train_loader = DataLoader(train_set, batch_size=BATCH_SIZE, shuffle=True, num_workers=0)
    test_loader = DataLoader(test_set, batch_size=BATCH_SIZE, shuffle=False, num_workers=0)

    model = SlowWaveNet(num_classes=2).to(DEVICE)
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, 'min', patience=2, factor=0.5)

    print(f"Starting training on {DEVICE}...")
    best_loss = float('inf')
    best_f1 = 0

    for epoch in range(EPOCHS):
        #train
        train_loss, train_acc = train_one_epoch(model, train_loader, train_criterion, optimizer, DEVICE)

        #val
        val_loss, val_acc, y_true, y_pred = validate(model, test_loader, val_criterion, DEVICE)
        scheduler.step(val_loss)

        # this one macro f1
        macro_f1 = f1_score(y_true, y_pred, average='macro')

        print(f"Epoch [{epoch}/{EPOCHS}] Loss: {val_loss:.4f}, Acc: {val_acc:.4f} | F1: {macro_f1:.4f}")

        # save model by macro_f1
        if macro_f1 > best_f1:
            best_f1 = macro_f1
            torch.save(model.state_dict(), SAVE_PATH)
            print(f"-->New Best Macro F1: {best_f1:.4f} saved at epoch {epoch}")

    #load the best one
    if os.path.exists(SAVE_PATH):
        model.load_state_dict(torch.load(SAVE_PATH, map_location=DEVICE))
        print(f"Successfully loaded best model from {SAVE_PATH}")
    else:
        print("Warning: Save path not found, using current model weights.")

    #visulization
    eval_criterion = nn.CrossEntropyLoss()

    # best again, for confusion matrix
    _, _, final_true, final_pred = validate(model, test_loader, eval_criterion, DEVICE)

    from sklearn.metrics import classification_report
    print("\nFinal Classification Report:")
    print(classification_report(final_true, final_pred, target_names=['Fast', 'Post']))

    # confusion
    cm = confusion_matrix(final_true, final_pred)
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=['Fast', 'Post'], yticklabels=['Fast', 'Post'])
    plt.xlabel('Predicted')
    plt.ylabel('True')
    plt.title(f'Confusion Matrix (Best F1: {best_f1:.4f})')
    plt.savefig('confusion_matrix.png')
    plt.show()

    # 5 f1-score
    print("\nDetailed Report:")
    print(classification_report(final_true, final_pred, target_names=['Fast', 'Post']))


if __name__ == "__main__":
    main()