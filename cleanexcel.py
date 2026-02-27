import pandas as pd

file_path = "/Users/cynthiawang/Desktop/GI_lab/combined_fasting_post.xlsx"
def clean_excel_data(file_path):

    df = pd.read_excel(file_path)
    df_cleaned = df.dropna(how='all')

    return df_cleaned

