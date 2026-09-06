import os
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
    get_output_dirs,
)

# A column missing more often than this, in the training split, gets an explicit "<col>_missing"
# indicator added before imputation (see add_missing_indicators below) instead of having its
# imputed value written into the record silently, indistinguishable from a real observation.
# Chosen once, dataset-agnostically, rather than hardcoding which columns of which dataset need
# it: it correctly picks out `ca`/`thal` for Heart Disease (missing in >90% of three of its four
# source centres) and `max_glu_serum`/`A1Cresult` for Diabetes130 (missing in 95%/83% of the raw
# file) without naming either dataset's columns here.
MISSING_INDICATOR_THRESHOLD = 0.30

#main preprocessing function: load, clean, encode, scale data, save preprocessed data for embedding phase
#dataset: "heart_disease" (default) or "diabetes130"
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
    print(dataset_chosen.columns)

    # split dataset into features and target variable (the rest are features)
    X = dataset_chosen.drop(target_col, axis=1)
    y = dataset_chosen[target_col]
    y = (y > 0).astype(int)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    # Flag, from the training split only, which columns are missing so often that imputing them
    # would fabricate a large fraction of the feature outright. The indicator is added to both
    # splits before imputation and treated as categorical from here on (SMOTENC, the encoder, and
    # record_to_text_*() in embedding.py all need to see it) so a downstream reader — human or
    # language model — can tell an imputed value from an observed one instead of receiving both
    # presented identically.
    missing_flagged_cols = columns_needing_missing_indicator(
        X_train, num_cols_used + cat_cols_used, threshold=MISSING_INDICATOR_THRESHOLD
    )
    X_train = add_missing_indicators(X_train, missing_flagged_cols)
    X_test = add_missing_indicators(X_test, missing_flagged_cols)
    cat_cols_used = cat_cols_used + [f"{c}_missing" for c in missing_flagged_cols]

    # impute missing values in the raw feature space (required before SMOTE, and so every
    # record stays interpretable for the text description used in the embedding phase).
    # Fill values are fitted on the training split only, then re-applied as-is to the test split:
    # previously the same fillna(median()/mode()) call ran independently on whatever frame it
    # received, so a caller that (as this function itself now does) also needed to impute the
    # test split would have leaked test-set statistics into its own imputation — fit_imputation_
    # values/apply_imputation below separate "learn the fill value" from "use it" so that can't happen.
    fill_values = fit_imputation_values(X_train, num_cols_used, cat_cols_used)
    X_train_imputed = apply_imputation(X_train, fill_values)
    X_test_imputed = apply_imputation(X_test, fill_values)

    # balance the target class on the raw/interpretable features with SMOTENC, so synthetic
    # records keep realistic values (real scale numerics + valid categorical codes) and can be
    # converted to text just like real records — plain SMOTE only works in encoded vector space
    # and its synthetic rows can't be mapped back to a clinical record description.
    X_train_bal, y_train_bal = balance_classes(X_train_imputed, y_train, cat_cols_used)

    # fit the encoder (scaling + one-hot) on the balanced raw data, used for UMAP/heatmap only
    encoder = build_encoder(X_train_bal, y_train_bal, num_cols_used, cat_cols_used)
    X_train_emb_df = data_processed(X_train_bal, y_train_bal, encoder, num_cols_used, cat_cols_used)
    plot_umap(X_train_emb_df.drop("target", axis=1), X_train_emb_df["target"], "Preprocessed Data + Embeddings",
              graphics_dir=dirs["graphics"])
    print(X_train_emb_df.head())
    save_data_processed(X_train_emb_df, dirs["preprocessing"])
    plot_data_heatmap(X_train_emb_df, num_cols_used, graphics_dir=dirs["graphics"])

    # Raw (pre-encoding) clinical features, row-order aligned with the embeddings generated from
    # X_train_bal, so predictions can be traced back to the original/synthetic record for error analysis.
    X_train_bal.reset_index(drop=True).to_csv(
        os.path.join(dirs["preprocessing"], "X_train_raw.csv"), index=False
    )

    # Held-out test split: imputed with training statistics only, never balanced by SMOTENC, and
    # never used by any training or model-selection decision. Persisted here so a later phase
    # (holdout_evaluation.py) can embed it and report a genuine generalization estimate — this
    # replaces a version of this function that computed the same 80/20 split and then discarded
    # X_test/y_test without using them for anything (see docs/CHANGES.md).
    X_test_imputed.reset_index(drop=True).to_csv(
        os.path.join(dirs["preprocessing"], "X_test_raw.csv"), index=False
    )
    np.save(os.path.join(dirs["preprocessing"], "y_test.npy"), np.asarray(y_test).astype(np.int32))

    return X_train_bal, y_train_bal


def columns_needing_missing_indicator(X, columns, threshold=0.30):
    """Names of columns in `columns` whose fraction of missing values in X exceeds `threshold`."""
    rates = X[columns].isna().mean()
    return list(rates[rates > threshold].index)


def add_missing_indicators(X, columns):
    """Return a copy of X with one extra "<col>_missing" 0/1 column per name in `columns`,
    computed before any imputation touches those columns."""
    X = X.copy()
    for col in columns:
        X[f"{col}_missing"] = X[col].isna().astype(int)
    return X



#preparation functions: impute, balance, encode data, save preprocessed data

def fit_imputation_values(X, num_cols, cat_cols):
    """Compute the fill value (median for numeric columns, mode for categorical ones) for each
    column, from X alone. Kept separate from apply_imputation so the same fitted values can be
    re-applied to a different split (the test set) without recomputing them from it."""
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


def impute_raw(X, num_cols, cat_cols):
    """Fit-and-apply imputation on X in one step. Equivalent to the original single-frame
    behaviour of this function; preprocessing_data() itself now calls fit_imputation_values() /
    apply_imputation() directly so it can fit once on the training split and apply the same
    values to the test split, but this convenience form is kept for any other caller (including
    tests) that only ever has one frame to impute."""
    return apply_imputation(X, fit_imputation_values(X, num_cols, cat_cols))

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

def save_data_processed(X_train_emb_df, preprocessing_dir):
    np.save(os.path.join(preprocessing_dir, "preprocessed_data.npy"), X_train_emb_df.values)
    np.save(os.path.join(preprocessing_dir, "preprocessed_labels.npy"), X_train_emb_df['target'].values)