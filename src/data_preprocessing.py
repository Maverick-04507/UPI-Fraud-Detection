import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
import joblib

def preprocess_data(data_dir="Dataset", output_dir="Dataset/processed"):
    print("Loading datasets...")
    # Load the datasets
    transactions = pd.read_csv(os.path.join(data_dir, "transactions.csv"))
    users = pd.read_csv(os.path.join(data_dir, "users.csv"))
    merchants = pd.read_csv(os.path.join(data_dir, "merchants.csv"))
    
    print(f"Loaded {len(transactions)} transactions, {len(users)} users, and {len(merchants)} merchants.")
    
    # 1. Merge User profiles
    # Select non-overlapping behavioral/demographic columns from users.csv
    users_subset = users[['user_id', 'age_group', 'city', 'account_age_days', 'linked_bank_count', 'is_high_risk_user']]
    df = transactions.merge(users_subset, on='user_id', how='left')
    
    # 2. Merge Merchant metadata for P2M transactions
    merchants_subset = merchants[['merchant_id', 'merchant_category', 'merchant_size', 'avg_daily_transactions', 'is_registered', 'rating']]
    df = df.merge(merchants_subset, left_on='receiver_id', right_on='merchant_id', how='left')
    df.drop(columns=['merchant_id'], inplace=True)
    
    # 3. Handle Missing Values
    # Missing transaction values (intentionally introduced in dataset)
    df['time_since_last_txn_min'] = df['time_since_last_txn_min'].fillna(-1.0) # -1 representing no previous txn (first txn)
    df['transaction_velocity'] = df['transaction_velocity'].fillna(df['transaction_velocity'].median())
    df['amount_deviation_score'] = df['amount_deviation_score'].fillna(0.0)
    
    # Missing merchant features (occur for P2P transactions since they do not link to merchants.csv)
    df['merchant_category'] = df['merchant_category'].fillna('P2P_Transfer')
    df['merchant_size'] = df['merchant_size'].fillna('None')
    df['avg_daily_transactions'] = df['avg_daily_transactions'].fillna(0.0)
    df['is_registered'] = df['is_registered'].fillna(0.0)
    df['rating'] = df['rating'].fillna(0.0)
    
    # 4. Feature Engineering
    # Ratio of transaction amount to the user's average historical transaction amount
    df['amount_to_avg_ratio'] = df['amount'] / (df['user_avg_txn_value'] + 1e-5)
    
    # Target and identifier columns
    target_col = 'is_fraud'
    drop_cols = ['transaction_id', 'user_id', 'receiver_id', 'timestamp', 'date', 'day_of_week', 'status', target_col]
    
    # Identify numerical and categorical columns
    categorical_cols = [
        'receiver_type', 'transaction_type', 'payment_app', 'device_type', 
        'user_city_tier', 'user_kyc_status', 'age_group', 'city', 
        'merchant_category', 'merchant_size'
    ]
    
    numerical_cols = [
        'amount', 'hour_of_day', 'is_weekend', 'is_night_transaction', 
        'time_since_last_txn_min', 'user_avg_monthly_txn', 'user_avg_txn_value', 
        'user_loyalty_score', 'new_device_flag', 'ip_location_mismatch', 
        'failed_attempts_last_24h', 'transaction_velocity', 'amount_deviation_score', 
        'recurring_payment_flag', 'balance_after_transaction', 'transaction_frequency_score',
        'account_age_days', 'linked_bank_count', 'is_high_risk_user',
        'avg_daily_transactions', 'is_registered', 'rating', 'amount_to_avg_ratio'
    ]
    
    # 5. Label Encoding for Categorical Columns
    os.makedirs(output_dir, exist_ok=True)
    label_encoders = {}
    
    print("Encoding categorical features...")
    for col in categorical_cols:
        # Convert column to string to prevent mismatch with None/NaN values
        df[col] = df[col].astype(str)
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col])
        label_encoders[col] = le
        # Save the encoder for backend serving
        joblib.dump(le, os.path.join(output_dir, f"encoder_{col}.joblib"))
    
    # Prepare feature matrix X and target vector y
    X = df[numerical_cols + categorical_cols].copy()
    y = df[target_col].copy()
    
    # 6. Scaling Numerical Columns
    print("Scaling numerical features...")
    scaler = StandardScaler()
    X[numerical_cols] = scaler.fit_transform(X[numerical_cols])
    joblib.dump(scaler, os.path.join(output_dir, "scaler.joblib"))
    
    # Save column ordering for consistency in inference
    joblib.dump({'numerical_cols': numerical_cols, 'categorical_cols': categorical_cols}, 
                os.path.join(output_dir, "feature_columns.joblib"))
    
    # 7. Split into Train/Test Sets
    print("Splitting datasets...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Save processed splits
    print(f"Saving preprocessed data to {output_dir}...")
    X_train.to_csv(os.path.join(output_dir, "X_train.csv"), index=False)
    X_test.to_csv(os.path.join(output_dir, "X_test.csv"), index=False)
    y_train.to_csv(os.path.join(output_dir, "y_train.csv"), index=False)
    y_test.to_csv(os.path.join(output_dir, "y_test.csv"), index=False)
    
    print("Preprocessing completed successfully!")

if __name__ == "__main__":
    preprocess_data()
