import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from imblearn.over_sampling import SMOTENC


from function import plot_data_heatmap, columns, num_cols, cat_cols, plot_umap

#main preprocessing function: load, clean, encode, scale data, save preprocessed data for embedding phase
def preprocessing_data():
    # fetch dataset from data files
    heart_disease= load_heart_disease()
    #first look at the dataset
    print(heart_disease.shape)
    print(heart_disease.head())
    print(heart_disease.columns)

    # split dataset into features and target variable  (num is the target variable, the rest are features)
    X = heart_disease.drop('num', axis=1)
    y = heart_disease['num']
    y = (y > 0).astype(int)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    # impute missing values in the raw feature space (required before SMOTE, and so every
    # record stays interpretable for the text description used in the embedding phase)
    X_train_imputed = impute_raw(X_train)

    # balance the target class on the raw/interpretable features with SMOTENC, so synthetic
    # records keep realistic values (real scale numerics + valid categorical codes) and can be
    # converted to text just like real records — plain SMOTE only works in encoded vector space
    # and its synthetic rows can't be mapped back to a clinical record description.
    X_train_bal, y_train_bal = balance_classes(X_train_imputed, y_train)

    # fit the encoder (scaling + one-hot) on the balanced raw data, used for UMAP/heatmap only
    encoder = build_encoder(X_train_bal, y_train_bal)
    X_train_emb_df = data_processed(X_train_bal, y_train_bal, encoder)
    plot_umap(X_train_emb_df.drop("target", axis=1), X_train_emb_df["target"], "Preprocessed Data + Embeddings")
    print(X_train_emb_df.head())
    save_data_processed(X_train_emb_df)
    plot_data_heatmap(X_train_emb_df)

    # Raw (pre-encoding) clinical features, row-order aligned with the embeddings generated from
    # X_train_bal, so predictions can be traced back to the original/synthetic record for error analysis.
    X_train_bal.reset_index(drop=True).to_csv("datas/preprocessing/X_train_raw.csv", index=False)

    return X_train_bal, y_train_bal

#load data from files and concatenate into one dataframe
def load_heart_disease():
    files = [
        "datas/heart+disease/processed.cleveland.data",
        "datas/heart+disease/processed.hungarian.data",
        "datas/heart+disease/processed.switzerland.data",
        "datas/heart+disease/processed.va.data"
    ]
    dfs = [pd.read_csv(f, header=None, na_values="?") for f in files]
    df = pd.concat(dfs, ignore_index=True)
    df.columns = columns

    # In some source files (notably Switzerland and Hungary) missing cholesterol/resting
    # blood pressure readings are encoded as 0 rather than "?". 0 mg/dl or 0 mm Hg is not a
    # physiologically valid value for either, so treat it as missing like the rest of the pipeline.
    df["chol"] = df["chol"].replace(0, np.nan)
    df["trestbps"] = df["trestbps"].replace(0, np.nan)

    return df

#preparation functions: impute, balance, encode data, save preprocessed data

def impute_raw(X):
    X = X.copy()
    for col in num_cols:
        X[col] = X[col].fillna(X[col].median())
    for col in cat_cols:
        X[col] = X[col].fillna(X[col].mode().iloc[0])
    return X

def balance_classes(X, y):
    # SMOTENC handles the mix of numeric and categorical columns directly on the raw
    # feature space: numeric features are interpolated, categorical ones are set to the
    # majority value among nearest neighbors, so every synthetic row is still a valid
    # (interpretable) clinical record.
    cat_idx = [X.columns.get_loc(c) for c in cat_cols]
    smote_nc = SMOTENC(categorical_features=cat_idx, random_state=42)
    X_res, y_res = smote_nc.fit_resample(X, y)
    return X_res, y_res

def build_encoder(X, y):
    numeric_transformer = StandardScaler()
    categorical_transformer = OneHotEncoder(handle_unknown='ignore')

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, num_cols),
            ('cat', categorical_transformer, cat_cols)
        ]
    )

    return preprocessor.fit(X, y)

def data_processed(X_train, y_train, preprocessor):
    X_train_emb = preprocessor.transform(X_train)
    num_features = num_cols
    cat_features = list(
        preprocessor.named_transformers_['cat'].get_feature_names_out(cat_cols)
    )
    feature_names = num_features + cat_features
    X_train_emb_df = pd.DataFrame(X_train_emb, columns=feature_names)
    X_train_emb_df['target'] = np.asarray(y_train)
    return X_train_emb_df

def save_data_processed(X_train_emb_df):
    np.save("datas/preprocessing/preprocessed_data.npy", X_train_emb_df.values)
    np.save("datas/preprocessing/preprocessed_labels.npy", X_train_emb_df['target'].values)