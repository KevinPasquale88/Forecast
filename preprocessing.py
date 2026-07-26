import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from imblearn.over_sampling import SMOTENC


from function import (
    load_heart_disease, load_diabetes130, plot_data_heatmap, plot_umap,
    num_cols, cat_cols,
    num_cols_diabetes130, cat_cols_diabetes130,
)

#main preprocessing function: load, clean, encode, scale data, save preprocessed data for embedding phase
#dataset: "heart_disease" (default) or "diabetes130"
def preprocessing_data(dataset="heart_disease"):
    sample_size = 20000
    if dataset == "diabetes130":
        datasetChoosen = load_diabetes130(sample_size=sample_size)
        target_col = "readmitted"
        num_cols_used = num_cols_diabetes130
        cat_cols_used = cat_cols_diabetes130
    else:
        datasetChoosen = load_heart_disease()
        target_col = "num"
        num_cols_used = num_cols
        cat_cols_used = cat_cols

    #first look at the dataset
    print(datasetChoosen.shape)
    print(datasetChoosen.head())
    print(datasetChoosen.columns)

    # split dataset into features and target variable (the rest are features)
    X = datasetChoosen.drop(target_col, axis=1)
    y = datasetChoosen[target_col]
    y = (y > 0).astype(int)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    # impute missing values in the raw feature space (required before SMOTE, and so every
    # record stays interpretable for the text description used in the embedding phase)
    X_train_imputed = impute_raw(X_train, num_cols_used, cat_cols_used)

    # balance the target class on the raw/interpretable features with SMOTENC, so synthetic
    # records keep realistic values (real scale numerics + valid categorical codes) and can be
    # converted to text just like real records — plain SMOTE only works in encoded vector space
    # and its synthetic rows can't be mapped back to a clinical record description.
    X_train_bal, y_train_bal = balance_classes(X_train_imputed, y_train, cat_cols_used)

    # fit the encoder (scaling + one-hot) on the balanced raw data, used for UMAP/heatmap only
    encoder = build_encoder(X_train_bal, y_train_bal, num_cols_used, cat_cols_used)
    X_train_emb_df = data_processed(X_train_bal, y_train_bal, encoder, num_cols_used, cat_cols_used)
    plot_umap(X_train_emb_df.drop("target", axis=1), X_train_emb_df["target"], "Preprocessed Data + Embeddings")
    print(X_train_emb_df.head())
    save_data_processed(X_train_emb_df)
    plot_data_heatmap(X_train_emb_df, num_cols_used)

    # Raw (pre-encoding) clinical features, row-order aligned with the embeddings generated from
    # X_train_bal, so predictions can be traced back to the original/synthetic record for error analysis.
    X_train_bal.reset_index(drop=True).to_csv("datas/preprocessing/X_train_raw.csv", index=False)

    return X_train_bal, y_train_bal



#preparation functions: impute, balance, encode data, save preprocessed data

def impute_raw(X, num_cols, cat_cols):
    X = X.copy()
    for col in num_cols:
        X[col] = X[col].fillna(X[col].median())
    for col in cat_cols:
        X[col] = X[col].fillna(X[col].mode().iloc[0])
    return X

def balance_classes(X, y, cat_cols):
    # SMOTENC handles the mix of numeric and categorical columns directly on the raw
    # feature space: numeric features are interpolated, categorical ones are set to the
    # majority value among nearest neighbors, so every synthetic row is still a valid
    # (interpretable) clinical record.
    cat_idx = [X.columns.get_loc(c) for c in cat_cols]
    smote_nc = SMOTENC(categorical_features=cat_idx, random_state=42)
    X_res, y_res = smote_nc.fit_resample(X, y)
    return X_res, y_res

def build_encoder(X, y, num_cols, cat_cols):
    numeric_transformer = StandardScaler()
    categorical_transformer = OneHotEncoder(handle_unknown='ignore')

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, num_cols),
            ('cat', categorical_transformer, cat_cols)
        ]
    )

    return preprocessor.fit(X, y)

def data_processed(X_train, y_train, preprocessor, num_cols, cat_cols):
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