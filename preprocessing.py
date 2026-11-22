import os
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer


from function import (
    load_heart_disease, load_diabetes130, plot_data_heatmap, plot_umap,
    num_cols, cat_cols,
    num_cols_diabetes130, cat_cols_diabetes130,
    get_output_dirs,
)

# Main preprocessing function: load the raw records and hold out an untouched, stratified 20%
# test split. dataset: "heart_disease" (default) or "diabetes130".
#
# No imputation and no oversampling of the records that get embedded:
# - a missing value stays missing and becomes "not recorded" in the generated text, so an absent
#   measurement is never presented to the encoder as if it had been observed;
# - class imbalance is handled by the decision threshold (function.fit_classifier), not by
#   oversampling. SMOTENC applied before cross-validation inflated the Diabetes130 CV AUC from
#   ~0.55 to ~0.76 (synthetic positives interpolated from records in other folds); see
#   docs/CHANGES.md.
def preprocessing_data(dataset="heart_disease"):
    dirs = get_output_dirs(dataset)
    sample_size = 20000
    if dataset == "diabetes130":
        dataset_chosen = load_diabetes130(sample_size=sample_size)
        target_col = "readmitted"
        num_cols_used = num_cols_diabetes130
        cat_cols_used = cat_cols_diabetes130
    else:
        dataset_chosen = load_heart_disease()
        target_col = "num"
        num_cols_used = num_cols
        cat_cols_used = cat_cols

    #first look at the dataset
    print(dataset_chosen.shape)
    print(dataset_chosen.head())

    # split dataset into features and target variable (the rest are features)
    X = dataset_chosen.drop(target_col, axis=1)
    y = (dataset_chosen[target_col] > 0).astype(int)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    X_train, X_test = X_train.reset_index(drop=True), X_test.reset_index(drop=True)
    y_train, y_test = y_train.reset_index(drop=True), y_test.reset_index(drop=True)

    # Visualization only (UMAP + correlation heatmap): StandardScaler/UMAP cannot take NaN, so a
    # *copy* of the training split is imputed with training statistics. These imputed values are
    # never written into the text descriptions or seen by any classifier.
    fill_values = fit_imputation_values(X_train, num_cols_used, cat_cols_used)
    X_train_viz = apply_imputation(X_train, fill_values)
    encoder = build_encoder(X_train_viz, y_train, num_cols_used, cat_cols_used)
    X_train_emb_df = data_processed(X_train_viz, y_train, encoder, num_cols_used, cat_cols_used)
    plot_umap(X_train_emb_df.drop("target", axis=1), X_train_emb_df["target"], "Preprocessed Data",
              graphics_dir=dirs["graphics"])
    plot_data_heatmap(X_train_emb_df, num_cols_used, graphics_dir=dirs["graphics"])

    # Raw training features (missing values left as empty cells), row-aligned with the training
    # embeddings, so error_analysis.py can trace predictions back to the original record.
    X_train.to_csv(os.path.join(dirs["preprocessing"], "X_train_raw.csv"), index=False)
    # Held-out test split, persisted for traceability; never used by any training,
    # threshold-selection or model-comparison step.
    X_test.to_csv(os.path.join(dirs["preprocessing"], "X_test_raw.csv"), index=False)
    np.save(os.path.join(dirs["preprocessing"], "y_test.npy"), np.asarray(y_test).astype(np.int32))

    return X_train, X_test, y_train, y_test


# Visualization-only helpers: impute, encode

def fit_imputation_values(X, num_cols, cat_cols):
    """Compute the fill value (median for numeric columns, mode for categorical ones) for each
    column, from X alone. Kept separate from apply_imputation so fitting and applying can never
    be accidentally done on different data."""
    fill_values = {}
    for col in num_cols:
        fill_values[col] = X[col].median()
    for col in cat_cols:
        fill_values[col] = X[col].mode().iloc[0]
    return fill_values


def apply_imputation(X, fill_values):
    """Fill missing values in X using already-fitted fill_values (see fit_imputation_values)."""
    X = X.copy()
    for col, value in fill_values.items():
        X[col] = X[col].fillna(value)
    return X


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
    if hasattr(X_train_emb, "toarray"):
        X_train_emb = X_train_emb.toarray()
    num_features = num_cols
    cat_features = list(
        preprocessor.named_transformers_['cat'].get_feature_names_out(cat_cols)
    )
    feature_names = num_features + cat_features
    X_train_emb_df = pd.DataFrame(X_train_emb, columns=feature_names)
    X_train_emb_df['target'] = np.asarray(y_train)
    return X_train_emb_df
