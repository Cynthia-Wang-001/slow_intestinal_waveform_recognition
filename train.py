
import torch
import torch.nn as nn
from ResidualMLP import ResidualMLP

def train_RMLP(model,X_train,X_test,y_train,y_test):
    # change to soft balancing
    counts = torch.bincount(y_train).float()

    #weights = 1.0 / torch.sqrt(counts)
    # weights = weights.to(y_train.device)

    weights = torch.tensor([1.0, 1.12])



    #weights = torch.tensor([1.0, 1.5])
    # change optimizer?
    # optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    # add optimizer
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, 'min', patience=8, factor=0.5)
    criterion = nn.CrossEntropyLoss(weight=weights, label_smoothing=0.1)
    # add label smooting because fasting and postcrandial are soooooo same...


    train_losses = []
    test_losses = []
    num_epochs = 90

    for epoch in range(num_epochs):
        # ===== TRAIN =====
        model.train()

        optimizer.zero_grad()

        y_train_pred = model(X_train)
        train_loss = criterion(y_train_pred, y_train)

        train_loss.backward()
        optimizer.step()

        # ===== EVAL =====
        model.eval()
        with torch.no_grad():
            y_test_pred = model(X_test)
            test_loss = criterion(y_test_pred, y_test)
            y_test_label_pred = torch.argmax(y_test_pred, dim=1)

        scheduler.step(test_loss)
        train_losses.append(train_loss.item())
        test_losses.append(test_loss.item())

        print(
            f"Epoch {epoch}: "
            f"train_loss = {train_loss.item():.4f}, "
            f"test_loss = {test_loss.item():.4f}"
        )

    return train_losses, test_losses,y_test_label_pred






