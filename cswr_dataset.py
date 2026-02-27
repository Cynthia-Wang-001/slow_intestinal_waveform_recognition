import os
import json
import pandas as pd
import re
from sklearn.model_selection import GroupShuffleSplit


def get_dataset_json(data_path='/Users/cynthiawang/Desktop/GI_lab/data_sync/data_segmented',
                     test_size=0.3,
                     random_state=80):
    # scan the folder
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Directory not found: {data_path}")

    all_files = [f for f in os.listdir(data_path) if f.endswith('.mat')]
    file_info = []

    for f in all_files:
        # 0: fast, 1: postprandial
        label = 1 if 'postprandial' in f.lower() else 0

        parts = f.replace('.mat', '').split('_')

        if len(parts) >= 5:
            rat_id = parts[1]  # 006
            channel = parts[3]  # Ch3
            seg_str = parts[4]  # seg01
            # extract number
            seg_num = int(re.search(r'\d+', seg_str).group())

            ch_uid = f"{label}_{rat_id}_{channel}"
        else:
            continue

        file_info.append({
            'file_name': f,
            'label': label,
            'rat_id': rat_id,
            'ch_uid': ch_uid,
            'seg_num': seg_num
        })

    df_files = pd.DataFrame(file_info)
    print(f"Total .mat files found: {len(df_files)}")

    def filter_segments(group):
        # current label 0 or 1?
        current_label = group['label'].iloc[0]

        #0: remove first and last 2 in fast
        if current_label == 0:
            if len(group) <= 4:
                return pd.DataFrame()
            group = group.sort_values('seg_num')
            return group.iloc[2:-2]

        # 1: don't remove!
        else:
            return group.sort_values('seg_num')


    df_cleaned = df_files.groupby('ch_uid', group_keys=False).apply(filter_segments)
    print(f"After removing first/last segments: {len(df_cleaned)} samples remaining")
    removed_count = len(df_files) - len(df_cleaned)
    print(f"Removed {removed_count} transition segments.")


    gss = GroupShuffleSplit(
        n_splits=1,
        test_size=test_size,
        random_state=random_state
    )

    # prevent that 1 same rat is in both train and val
    train_idx, test_idx = next(
        gss.split(df_cleaned, groups=df_cleaned['rat_id'])
    )

    train_df = df_cleaned.iloc[train_idx].reset_index(drop=True)
    test_df = df_cleaned.iloc[test_idx].reset_index(drop=True)

    print(f"Train set: {len(train_df)} samples from rats: {train_df['rat_id'].unique()}")
    print(f"Test set: {len(test_df)} samples from rats: {test_df['rat_id'].unique()}")

    # json  save
    dataset_dict = {
        "train": train_df[['file_name', 'label', 'rat_id']].to_dict(orient="records"),
        "test": test_df[['file_name', 'label', 'rat_id']].to_dict(orient="records")
    }

    json_output_path = os.path.join(data_path, "dataset.json")

    with open(json_output_path, "w") as f:
        json.dump(dataset_dict, f, indent=4)

    print(f"dataset.json saved to: {os.path.abspath(json_output_path)}")

    return train_df, test_df


if __name__ == "__main__":
    get_dataset_json()