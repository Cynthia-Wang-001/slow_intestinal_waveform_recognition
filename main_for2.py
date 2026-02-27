import numpy as np
import scipy.signal as signal
import torch
import torch.nn as nn
from sklearn.metrics import f1_score
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.metrics import confusion_matrix
import seaborn as sns

from ReadData import load_preprocess_waveform
from train import train_RMLP
from seremlp_for2 import ResidualMLP


def main():
    file_path = "/Users/cynthiawang/Desktop/GI_lab/combined_fasting_post.xlsx"
    X_train, X_test, y_train, y_test,in_dim,scaler= load_preprocess_waveform(file_path)
    in_dim = X_train.shape[1]
    model = ResidualMLP(in_dim)


    train_losses, test_losses, y_test_label_pred = train_RMLP(model,X_train, X_test, y_train, y_test)
    # test the accuracy of function
    from sklearn.metrics import accuracy_score, f1_score

    y_true = y_test.cpu().numpy()
    y_pred = y_test_label_pred.cpu().numpy()

    acc = accuracy_score(y_true, y_pred)
    macro_f1 = f1_score(y_true, y_pred, average="macro")

    print(f"Test accuracy: {acc:.4f}")
    print(f"Test macro-F1: {macro_f1:.4f}")


    # After loss training and validation: the model has learned phase-discriminative
    # patterns that generalize across rats.
    # Min loss: for early stopping to avoid overfitting (about rat-specific characteristics in the training set)

    # confusion matrix to test the accuracy

    cm = confusion_matrix(
        y_test.cpu().numpy(),
        y_test_label_pred.cpu().numpy()
    )

    print(cm)

    # visualization

    plt.figure(figsize=(6, 4))
    plt.plot(train_losses, label="Train loss")
    plt.plot(test_losses, label="Test loss")
    plt.xlabel("Epoches")
    plt.ylabel("Label-Smoothing Cross-entropy loss")
    plt.title("Training and Test Loss")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    plt.figure(figsize=(5, 4))
    sns.heatmap(
    cm,
    annot=True,
    fmt="d",
    cmap="Blues",
    xticklabels=["Fasting","Postprandial"],
    yticklabels=["Fasting","Postprandial"]
    )
    plt.xlabel("Predicted label")
    plt.ylabel("True label")
    plt.title("Confusion Matrix (Test Set)")
    plt.tight_layout()
    plt.show()

    recall = np.diag(cm) / cm.sum(axis=1)
    print("Per-class recall:", recall)



if __name__ == "__main__":
    main()