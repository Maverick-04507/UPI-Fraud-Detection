import os
import json
import joblib
import pandas as pd
import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import tensorflow as tf

app = FastAPI(title="UPI Fraud Detection API", description="API for predicting UPI transaction fraud using multiple models")

PROCESSED_DIR = "Dataset/processed"
DATASET_DIR = "Dataset"

models = {}
encoders = {}
scaler = None
feature_cols = None
autoencoder_meta = None
kmeans_meta = None

models_loaded = False

def load_all_artifacts():
    global scaler, feature_cols, autoencoder_meta, kmeans_meta, models_loaded
    try:
        if not os.path.exists(PROCESSED_DIR):
            print(f"Directory {PROCESSED_DIR} does not exist. Please run preprocessing first.")
            return False
            
        print("Loading encoders and scaling artifacts...")
        scaler = joblib.load(os.path.join(PROCESSED_DIR, "scaler.joblib"))
        feature_cols = joblib.load(os.path.join(PROCESSED_DIR, "feature_columns.joblib"))
        
        categorical_cols = feature_cols['categorical_cols']
        for col in categorical_cols:
            encoders[col] = joblib.load(os.path.join(PROCESSED_DIR, f"encoder_{col}.joblib"))
            
        print("Loading ML models...")
        if os.path.exists(os.path.join(PROCESSED_DIR, "model_random_forest.joblib")):
            models["Random Forest"] = joblib.load(os.path.join(PROCESSED_DIR, "model_random_forest.joblib"))
            
        if os.path.exists(os.path.join(PROCESSED_DIR, "model_kmeans.joblib")):
            models["K-Means"] = joblib.load(os.path.join(PROCESSED_DIR, "model_kmeans.joblib"))
            kmeans_meta = joblib.load(os.path.join(PROCESSED_DIR, "kmeans_meta.joblib"))
            
        if os.path.exists(os.path.join(PROCESSED_DIR, "model_lof.joblib")):
            models["Local Outlier Factor"] = joblib.load(os.path.join(PROCESSED_DIR, "model_lof.joblib"))
            
        if os.path.exists(os.path.join(PROCESSED_DIR, "model_cnn.keras")):
            models["1D CNN"] = tf.keras.models.load_model(os.path.join(PROCESSED_DIR, "model_cnn.keras"))
            
        if os.path.exists(os.path.join(PROCESSED_DIR, "model_autoencoder.keras")):
            models["Autoencoder"] = tf.keras.models.load_model(os.path.join(PROCESSED_DIR, "model_autoencoder.keras"))
            autoencoder_meta = joblib.load(os.path.join(PROCESSED_DIR, "autoencoder_meta.joblib"))
            
        print("Artifacts loaded successfully!")
        models_loaded = True
        return True
    except Exception as e:
        print(f"Error loading models or encoders: {e}")
        return False

class TransactionInput(BaseModel):
    amount: float
    hour_of_day: int
    is_weekend: int
    is_night_transaction: int
    time_since_last_txn_min: float
    user_avg_monthly_txn: int
    user_avg_txn_value: float
    user_loyalty_score: float
    new_device_flag: int
    ip_location_mismatch: int
    failed_attempts_last_24h: int
    transaction_velocity: int
    amount_deviation_score: float
    recurring_payment_flag: int
    balance_after_transaction: float
    transaction_frequency_score: float
    account_age_days: int
    linked_bank_count: int
    is_risk_user: int  
    avg_daily_transactions: float  
    is_registered: int  
    rating: float  
    
    receiver_type: str
    transaction_type: str
    payment_app: str
    device_type: str
    user_city_tier: str
    user_kyc_status: str
    age_group: str
    city: str
    merchant_category: str
    merchant_size: str

def safe_encode(col_name, val):
    le = encoders.get(col_name)
    if le is None:
        return 0
    val_str = str(val)
    if val_str in le.classes_:
        return int(le.transform([val_str])[0])
    return 0

@app.on_event("startup")
def startup_event():
    load_all_artifacts()

@app.post("/api/train")
def train_models():
    import subprocess
    try:
        print("Starting model training subprocess...")
        process = subprocess.run(["python", "src/model_training.py"], capture_output=True, text=True)
        if process.returncode != 0:
            raise HTTPException(status_code=500, detail=f"Training failed: {process.stderr}")
        
        success = load_all_artifacts()
        if not success:
            raise HTTPException(status_code=500, detail="Failed to load trained models after retraining")
            
        metrics_path = os.path.join(PROCESSED_DIR, "metrics.json")
        if os.path.exists(metrics_path):
            with open(metrics_path, "r") as f:
                metrics = json.load(f)
            return {"status": "success", "metrics": metrics}
        return {"status": "success", "message": "Models trained, but metrics file not found"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stats")
def get_stats():
    try:
        transactions_path = os.path.join(DATASET_DIR, "transactions.csv")
        if not os.path.exists(transactions_path):
            raise HTTPException(status_code=404, detail="Dataset not found")
            
        df_txn = pd.read_csv(transactions_path)
        
        total_txns = len(df_txn)
        success_rate = (df_txn['status'] == 'Success').mean() * 100
        avg_amount = df_txn['amount'].mean()
        fraud_rate = df_txn['is_fraud'].mean() * 100

        metrics = {}
        metrics_path = os.path.join(PROCESSED_DIR, "metrics.json")
        if os.path.exists(metrics_path):
            with open(metrics_path, "r") as f:
                metrics = json.load(f)
                
        return {
            "total_transactions": total_txns,
            "success_rate": round(success_rate, 2),
            "avg_transaction_amount": round(avg_amount, 2),
            "fraud_rate": round(fraud_rate, 2),
            "models_trained": list(metrics.keys()),
            "metrics": metrics
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/charts")
def get_charts():
    try:
        transactions_path = os.path.join(DATASET_DIR, "transactions.csv")
        if not os.path.exists(transactions_path):
            raise HTTPException(status_code=404, detail="Dataset not found")
            
        df_txn = pd.read_csv(transactions_path)

        amounts = df_txn['amount'].values
        hist, bin_edges = np.histogram(amounts, bins=10, range=(0, 5000))
        amount_dist = {
            "labels": [f"₹{int(bin_edges[i])}-{int(bin_edges[i+1])}" for i in range(len(hist))],
            "data": hist.tolist()
        }
        
        fraud_counts = df_txn['is_fraud'].value_counts().to_dict()
        fraud_vs_safe = {
            "labels": ["Legitimate", "Fraudulent"],
            "data": [fraud_counts.get(0, 0), fraud_counts.get(1, 0)]
        }
        
        app_counts = df_txn['payment_app'].value_counts()
        payment_apps = {
            "labels": app_counts.index.tolist(),
            "data": app_counts.values.tolist()
        }
        
        hour_counts = df_txn['hour_of_day'].value_counts().sort_index()
        hourly_dist = {
            "labels": [f"{h:02d}:00" for h in hour_counts.index],
            "data": hour_counts.values.tolist()
        }
        
        metrics = {}
        metrics_path = os.path.join(PROCESSED_DIR, "metrics.json")
        if os.path.exists(metrics_path):
            with open(metrics_path, "r") as f:
                metrics = json.load(f)
                
        return {
            "amount_distribution": amount_dist,
            "fraud_vs_safe": fraud_vs_safe,
            "payment_apps": payment_apps,
            "hourly_distribution": hourly_dist,
            "metrics": metrics
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/predict")
def predict_transaction(tx: TransactionInput):
    global models_loaded
    if not models_loaded:
        success = load_all_artifacts()
        if not success:
            raise HTTPException(status_code=500, detail="Models and scaling artifacts are not loaded. Run training script first.")
            
    try:
        input_dict = tx.dict()
        
        input_dict['amount_to_avg_ratio'] = input_dict['amount'] / (input_dict['user_avg_txn_value'] + 1e-5)
        input_dict['is_high_risk_user'] = input_dict.pop('is_risk_user')
        encoded_dict = {}
        for col in feature_cols['categorical_cols']:
            raw_val = input_dict.get(col, "None")
            encoded_dict[col] = safe_encode(col, raw_val)
        num_dict = {}
        for col in feature_cols['numerical_cols']:
            num_dict[col] = float(input_dict.get(col, 0.0))
            
        all_features = {**num_dict, **encoded_dict}
        df_inf = pd.DataFrame([all_features])
        
        numerical_cols = feature_cols['numerical_cols']
        df_inf[numerical_cols] = scaler.transform(df_inf[numerical_cols])
        
        ordered_features = feature_cols['numerical_cols'] + feature_cols['categorical_cols']
        X_inf = df_inf[ordered_features].copy()
        
        results = {}
        risk_signals = []

        if input_dict['new_device_flag'] == 1:
            risk_signals.append("Transaction from a new unrecognized device")
        if input_dict['ip_location_mismatch'] == 1:
            risk_signals.append("IP location differs from user's registered city")
        if input_dict['failed_attempts_last_24h'] >= 3:
            risk_signals.append(f"Multiple failed PIN attempts in last 24h ({input_dict['failed_attempts_last_24h']} attempts)")
        if input_dict['transaction_velocity'] >= 3:
            risk_signals.append("High transaction velocity (multiple successive transactions)")
        if input_dict['amount_deviation_score'] > 3.0:
            risk_signals.append("Transaction amount deviates significantly from historical average")
        if input_dict['is_night_transaction'] == 1:
            risk_signals.append("Transaction made during unusual late-night hours (10 PM - 6 AM)")
        if input_dict['is_high_risk_user'] == 1:
            risk_signals.append("User is flagged with a high risk profile")
        if "Random Forest" in models:
            rf_model = models["Random Forest"]
            prob = rf_model.predict_proba(X_inf)[0][1]
            results["Random Forest"] = {
                "score": round(float(prob), 4),
                "is_fraud": int(prob >= 0.5)
            }
            
        if "1D CNN" in models:
            cnn_model = models["1D CNN"]
            X_inf_cnn = np.expand_dims(X_inf.values, axis=-1)
            prob = cnn_model.predict(X_inf_cnn)[0][0]
            results["1D CNN"] = {
                "score": round(float(prob), 4),
                "is_fraud": int(prob >= 0.5)
            }
            
        if "Autoencoder" in models:
            ae_model = models["Autoencoder"]
            X_inf_pred = ae_model.predict(X_inf)
            mse = np.mean(np.power(X_inf - X_inf_pred, 2), axis=1)[0]
            
            threshold = autoencoder_meta['threshold']
            is_fraud = int(mse > threshold)
            
            score = min(1.0, float(mse / (threshold * 2.0)))
            results["Autoencoder"] = {
                "score": round(score, 4),
                "is_fraud": is_fraud,
                "reconstruction_loss": round(float(mse), 6)
            }
            
        if "K-Means" in models:
            kmeans_model = models["K-Means"]
            dist = kmeans_model.transform(X_inf)
            min_dist = np.min(dist, axis=1)[0]
            threshold = kmeans_meta['threshold']
            is_fraud = int(min_dist > threshold)
            score = min(1.0, float(min_dist / (threshold * 2.0)))
            results["K-Means"] = {
                "score": round(score, 4),
                "is_fraud": is_fraud,
                "distance": round(float(min_dist), 4)
            }
            
        if "Local Outlier Factor" in models:
            lof_model = models["Local Outlier Factor"]
            pred = lof_model.predict(X_inf)[0]
            is_fraud = int(pred == -1)
            score = 0.85 if is_fraud else 0.15 
            results["Local Outlier Factor"] = {
                "score": score,
                "is_fraud": is_fraud
            }
            
        scores = [res["score"] for res in results.values() if "score" in res]
        avg_risk_score = np.mean(scores) if scores else 0.0
        
        return {
            "risk_score": round(float(avg_risk_score), 4),
            "is_fraud": int(avg_risk_score >= 0.5),
            "risk_signals": risk_signals,
            "model_predictions": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@app.get("/")
def read_root():
    static_index = "src/static/index.html"
    if os.path.exists(static_index):
        return FileResponse(static_index)
    return {"message": "UPI Fraud Detection System is running. Add UI components to src/static/ to view dashboard."}

if os.path.exists("src/static"):
    app.mount("/static", StaticFiles(directory="src/static"), name="static")
