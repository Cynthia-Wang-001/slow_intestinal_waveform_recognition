import torch
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import GroupShuffleSplit

def load_preprocess_waveform(file_path):
    df = pd.read_excel(file_path)
    # check the excel reading state
    print(df.shape)
    print(df.columns)
    df = df.dropna() #2 use this, 3 don't use this
    # data processing
    exclude_cols = ["Label", "Rat_ID"]

    feature_cols = [
        col for col in df.columns
        if col not in exclude_cols and not col.startswith("Unnamed")
    ]

    print(feature_cols)
    # create x,y function
    #

    # Select features by excluding non-biological columns
    exclude_cols = ["Label", "Rat_ID"]
    feature_cols = [
        col for col in df.columns
        if col not in exclude_cols and not col.startswith("Unnamed")
    ]

    # Extract raw values and labels
    X_raw = df[feature_cols].values
    y = df["Label"].values
    rat_ids = df["Rat_ID"].values

    # Define group-based split to keep rats separate
    gss = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
    train_idx, test_idx = next(gss.split(X_raw, y, groups=rat_ids))

    # Initialize scaler and normalize features
    scaler = StandardScaler()

    # Fit and transform training data then transform test data
    X_train_np = scaler.fit_transform(X_raw[train_idx])
    X_test_np = scaler.transform(X_raw[test_idx])

    # Convert processed data and labels into tensors
    X_train = torch.tensor(X_train_np, dtype=torch.float32)
    X_test = torch.tensor(X_test_np, dtype=torch.float32)
    y_train = torch.tensor(y[train_idx], dtype=torch.long)
    y_test = torch.tensor(y[test_idx], dtype=torch.long)

    # Set input dimension for the model architecture
    in_dim = X_train.shape[1]

    train_rats = set(rat_ids[train_idx])
    test_rats = set(rat_ids[test_idx])

    print("Overlap rats:", train_rats & test_rats)
    # no overlap in the train and test set

    return X_train, X_test, y_train, y_test,in_dim,scaler