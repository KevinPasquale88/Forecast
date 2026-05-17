import numpy as np
import pandas as pd
from imblearn.pipeline import Pipeline as ImbPipeline
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from imblearn.over_sampling import SMOTE


from function import plot_data_heatmap, columns, num_cols, cat_cols, plot_pca

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

    # create and fit the full pipeline
    clean_pipeline = clean_data(X_train, y_train)

    X_train_emb_df = data_processed(X_train, y_train, clean_pipeline)
    plot_pca(X_train_emb_df.drop("target", axis=1), X_train_emb_df["target"], "Preprocessed Data + Embeddings")
    print(X_train_emb_df.head())
    save_data_processed(X_train_emb_df)
    plot_data_heatmap(X_train_emb_df)
    return X_train, y_train
    
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
    return df

def clean_data(X, y):
    numeric_transformer = ImbPipeline(steps=[('imputer', SimpleImputer(strategy='median')),('scaler', StandardScaler())])

    categorical_transformer = ImbPipeline(steps=[
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('onehot', OneHotEncoder(handle_unknown='ignore'))
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, num_cols),
            ('cat', categorical_transformer, cat_cols)
        ]
    )

    full_pipeline = ImbPipeline(steps=[
        ('preprocessor', preprocessor),
        ('smote', SMOTE(random_state=42))
    ])

    full_pipeline = full_pipeline.fit(X, y)
    return full_pipeline

def data_processed(X_train, y_train, pipeline):
    preprocessor = pipeline.named_steps['preprocessor']
    X_train_emb = preprocessor.transform(X_train)
    num_features = num_cols
    cat_features = list(
        preprocessor.named_transformers_['cat']
        .named_steps['onehot']
        .get_feature_names_out(cat_cols)
    )
    feature_names = num_features + cat_features
    X_train_emb_df = pd.DataFrame(X_train_emb, columns=feature_names)
    X_train_emb_df['target'] = y_train.values
    return X_train_emb_df

def save_data_processed(X_train_emb_df):
    np.save("datas/preprocessing/preprocessed_data.npy", X_train_emb_df.values)
    np.save("datas/preprocessing/preprocessed_labels.npy", X_train_emb_df['target'].values)