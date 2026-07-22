import os
import json
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.cluster import KMeans
from sklearn.neighbors import LocalOutlierFactor
import tensorflow as tf
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import Conv1D, MaxPooling1D, Flatten, Dense, Dropout, Input
import joblib

def load_processed_data(processed_dir="Dataset/processed"):
    print("Loading preprocessed splits...")
    X_train = pd.read_csv(os.path.join(processed_dir, "X_train.csv"))
    X_test = pd.read_csv(os.path.join(processed_dir, "X_test.csv"))
    y_train = pd.read_csv(os.path.join(processed_dir, "y_train.csv")).values.ravel()
    y_test = pd.read_csv(os.path.join(processed_dir, "y_test.csv")).values.ravel()
    return X_train, X_test, y_train, y_test

def train_random_forest(X_train, X_test, y_train, y_test, output_dir):
    print("\n--- Training Random Forest ---")
    rf = RandomForestClassifier(n_estimators=100, class_weight='balanced', random_state=42)
    rf.fit(X_train, y_train)
    
  
    y_pred = rf.predict(X_test)
    y_prob = rf.predict_proba(X_test)[:, 1]
    

    metrics = evaluate_model("Random Forest", y_test, y_pred, y_prob)

    joblib.dump(rf, os.path.join(output_dir, "model_random_forest.joblib"))
    return metrics

def train_cnn(X_train, X_test, y_train, y_test, output_dir):
    print("\n--- Training 1D CNN ---")
    
    X_train_cnn = np.expand_dims(X_train.values, axis=-1)
    X_test_cnn = np.expand_dims(X_test.values, axis=-1)
    
    num_features = X_train_cnn.shape[1]
    

    model = Sequential([
        Input(shape=(num_features, 1)),
        Conv1D(filters=32, kernel_size=3, activation='relu', padding='same'),
        MaxPooling1D(pool_size=2),
        Conv1D(filters=64, kernel_size=3, activation='relu', padding='same'),
        MaxPooling1D(pool_size=2),
        Flatten(),
        Dense(64, activation='relu'),
        Dropout(0.3),
        Dense(1, activation='sigmoid')
    ])
    
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    
    
    neg = np.sum(y_train == 0)
    pos = np.sum(y_train == 1)
    total = neg + pos
    weight_for_0 = (1 / neg) * (total / 2.0)
    weight_for_1 = (1 / pos) * (total / 2.0)
    class_weight = {0: weight_for_0, 1: weight_for_1}

    model.fit(
        X_train_cnn, y_train,
        epochs=10,
        batch_size=64,
        validation_split=0.1,
        class_weight=class_weight,
        verbose=1
    )
    
 
    y_prob = model.predict(X_test_cnn).ravel()
    y_pred = (y_prob >= 0.5).astype(int)

    metrics = evaluate_model("1D CNN", y_test, y_pred, y_prob)
    

    model.save(os.path.join(output_dir, "model_cnn.keras"))
    return metrics

def train_autoencoder(X_train, X_test, y_train, y_test, output_dir):
    print("\n--- Training Autoencoder (Unsupervised) ---")
    
    X_train_normal = X_train[y_train == 0]
    
    input_dim = X_train.shape[1]
    
    
    input_layer = Input(shape=(input_dim,))
 
    encoded = Dense(16, activation='relu')(input_layer)
    encoded = Dense(8, activation='relu')(encoded)

    decoded = Dense(16, activation='relu')(encoded)
    decoded = Dense(input_dim, activation='linear')(decoded)
    
    autoencoder = Model(inputs=input_layer, outputs=decoded)
    autoencoder.compile(optimizer='adam', loss='mse')
    
   
    autoencoder.fit(
        X_train_normal, X_train_normal,
        epochs=15,
        batch_size=64,
        validation_split=0.1,
        verbose=1
    )
    
   
    X_train_pred = autoencoder.predict(X_train)
    mse_train = np.mean(np.power(X_train - X_train_pred, 2), axis=1)
    
    
    threshold = np.percentile(mse_train, 96.2)
    

    X_test_pred = autoencoder.predict(X_test)
    mse_test = np.mean(np.power(X_test - X_test_pred, 2), axis=1)
    y_pred = (mse_test > threshold).astype(int)
    
    
    min_mse, max_mse = mse_test.min(), mse_test.max()
    y_prob = (mse_test - min_mse) / (max_mse - min_mse + 1e-5)
    
  
    metrics = evaluate_model("Autoencoder", y_test, y_pred, y_prob)
    

    autoencoder.save(os.path.join(output_dir, "model_autoencoder.keras"))
    joblib.dump({'threshold': threshold}, os.path.join(output_dir, "autoencoder_meta.joblib"))
    
    return metrics

def train_kmeans(X_train, X_test, y_train, y_test, output_dir):
    print("\n--- Training K-Means Anomaly Detection ---")
    # Train K-Means with k clusters (e.g. 5)
    kmeans = KMeans(n_clusters=5, random_state=42)
    kmeans.fit(X_train)
    
    # Anomaly score is distance to nearest cluster center
    distances = kmeans.transform(X_train)
    min_distances_train = np.min(distances, axis=1)
    
    # Set anomaly threshold at 96.2% percentile of training distances
    threshold = np.percentile(min_distances_train, 96.2)
    
    # Predict test set
    test_distances = kmeans.transform(X_test)
    min_distances_test = np.min(test_distances, axis=1)
    y_pred = (min_distances_test > threshold).astype(int)
    
    # Normalize distances for probability simulation
    min_d, max_d = min_distances_test.min(), min_distances_test.max()
    y_prob = (min_distances_test - min_d) / (max_d - min_d + 1e-5)
    
    # Metrics
    metrics = evaluate_model("K-Means", y_test, y_pred, y_prob)
    
    # Save
    joblib.dump(kmeans, os.path.join(output_dir, "model_kmeans.joblib"))
    joblib.dump({'threshold': threshold}, os.path.join(output_dir, "kmeans_meta.joblib"))
    
    return metrics

def train_lof(X_train, X_test, y_train, y_test, output_dir):
    print("\n--- Training Local Outlier Factor ---")
   
    lof = LocalOutlierFactor(n_neighbors=20, novelty=True, contamination=0.038)
   
    sample_size = min(3000, len(X_train))
    lof.fit(X_train.sample(n=sample_size, random_state=42))
    
   
    y_pred_lof = lof.predict(X_test)
    y_pred = (y_pred_lof == -1).astype(int)
    
    
    scores = -lof.score_samples(X_test)
    min_s, max_s = scores.min(), scores.max()
    y_prob = (scores - min_s) / (max_s - min_s + 1e-5)
    
   
    metrics = evaluate_model("Local Outlier Factor", y_test, y_pred, y_prob)
    
  
    joblib.dump(lof, os.path.join(output_dir, "model_lof.joblib"))
    
    return metrics

def evaluate_model(name, y_true, y_pred, y_prob):
    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred, zero_division=0)
    rec = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    auc = roc_auc_score(y_true, y_prob)
    
    print(f"Results for {name}:")
    print(f"  Accuracy : {acc:.4f}")
    print(f"  Precision: {prec:.4f}")
    print(f"  Recall   : {rec:.4f}")
    print(f"  F1 Score : {f1:.4f}")
    print(f"  ROC-AUC  : {auc:.4f}")
    
    return {
        "accuracy": round(float(acc), 4),
        "precision": round(float(prec), 4),
        "recall": round(float(rec), 4),
        "f1_score": round(float(f1), 4),
        "auc": round(float(auc), 4)
    }

def main():
    processed_dir = "Dataset/processed"
    X_train, X_test, y_train, y_test = load_processed_data(processed_dir)
    
    all_metrics = {}
    
    all_metrics["Random Forest"] = train_random_forest(X_train, X_test, y_train, y_test, processed_dir)
    all_metrics["1D CNN"] = train_cnn(X_train, X_test, y_train, y_test, processed_dir)
    all_metrics["Autoencoder"] = train_autoencoder(X_train, X_test, y_train, y_test, processed_dir)
    all_metrics["K-Means"] = train_kmeans(X_train, X_test, y_train, y_test, processed_dir)
    all_metrics["Local Outlier Factor"] = train_lof(X_train, X_test, y_train, y_test, processed_dir)
    
    # Save all metrics to JSON
    with open(os.path.join(processed_dir, "metrics.json"), "w") as f:
        json.dump(all_metrics, f, indent=4)
        
    print("\nAll models trained and comparative metrics saved successfully!")

if __name__ == "__main__":
    main()
