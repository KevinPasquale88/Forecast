import csv

from ollama import Client, embeddings
from sklearn.model_selection import train_test_split
from function import delete_files_embeddings, evaluate_embeddings, models_ollama, data_processed, load_heart_disease, clean_data, plot_data, record_to_text, save_embeddindgs_label_to_npy, save_embeddings_to_npy, training_classifier  

#clean up old npy files
delete_files_embeddings()
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
full_pipeline = clean_data(X_train, y_train)
print("Pipeline creata e addestrata con successo!")

X_train_emb_df = data_processed(X_train, y_train, full_pipeline)

texts = [record_to_text(r) for _, r in X_train.iterrows()]

#embedding generation
client = Client()
for model in models_ollama:
    embeddings = []
    print(f"Generating embeddings for model: {model['name']}")
    for t in texts:
        emb = client.embed(model['name'], input=t).embeddings
        embeddings.append(emb[0])
    # save embeddings to csv
    save_embeddings_to_npy(embeddings, filename=model["filename"])
    save_embeddindgs_label_to_npy(y_train.values, filename=model["filename_label"] )
    acc, f1 = evaluate_embeddings(embeddings, y_train)
    print(f"{model['name']} → accuracy: {acc:.3f}, F1: {f1:.3f}")
    plot_data(embeddings, y_train)

training_classifier()



