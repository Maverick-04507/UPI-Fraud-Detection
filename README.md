# UPI Fraud Detection System

This is a comprehensive end-to-end Machine Learning project designed to detect fraudulent UPI (Unified Payments Interface) transactions. It features a complete pipeline from data preprocessing to model training, as well as a FastAPI-based backend API for real-time predictions and a frontend dashboard.

## Features

- **Multiple Machine Learning Models**: Utilizes both supervised and unsupervised models for robust fraud detection:
  - **Supervised Learning**: Random Forest, 1D CNN (Convolutional Neural Network)
  - **Unsupervised Anomaly Detection**: Autoencoder, K-Means Clustering, Local Outlier Factor (LOF)
- **Data Preprocessing**: Includes robust scripts to merge transaction logs, user profiles, and merchant metadata, followed by feature engineering, scaling, and label encoding.
- **Real-time API**: A FastAPI backend providing endpoints for prediction, dataset statistics, chart data for visualizations, and triggering model re-training.
- **Rule-based Risk Signals**: Heuristic checks to flag high-risk transactions instantly (e.g., location mismatch, unusual hours, new devices).
- **Web Dashboard**: Statically served UI (HTML/CSS/JS) interacting with the APIs for monitoring and manual transaction checks.

## Project Structure

```text
.
├── Dataset/                     # Raw datasets (transactions, users, merchants)
│   ├── processed/               # Preprocessed splits and exported models/scalers/encoders
│   └── ...                      
├── src/                         # Source code directory
│   ├── app.py                   # FastAPI backend server
│   ├── data_preprocessing.py    # Data merging, scaling, and feature engineering script
│   ├── model_training.py        # Model training script for RF, CNN, LOF, Autoencoder, K-Means
│   └── static/                  # Frontend UI files (HTML, CSS, JS)
├── requirements.txt             # Python dependencies
├── run.py                       # Application entrypoint
└── .gitignore                   # Excludes datasets, model blobs, and cache files
```

## Getting Started

### Prerequisites

- Python 3.8+
- Create a virtual environment (recommended):
  ```bash
  python -m venv venv
  source venv/bin/activate  # On Windows use: venv\Scripts\activate
  ```

### Installation

1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Make sure the dataset CSVs are present in the `Dataset/` directory:
   - `transactions.csv`
   - `users.csv`
   - `merchants.csv`

### Preparing the Data

Before running the API or training models, preprocess the raw datasets:
```bash
python src/data_preprocessing.py
```
This script merges the CSVs, performs feature engineering, and exports the scaled data and encoders to `Dataset/processed/`.

### Training the Models

Once the data is preprocessed, train the ensemble of machine learning models:
```bash
python src/model_training.py
```
This will train the Random Forest, CNN, Autoencoder, K-Means, and LOF models, saving the architectures, weights, and a `metrics.json` file to `Dataset/processed/`.

### Running the Application

To start the FastAPI backend and serve the dashboard locally:
```bash
python run.py
```
Alternatively, you can run uvicorn directly:
```bash
uvicorn src.app:app --host 127.0.0.1 --port 8000 --reload
```

- **Dashboard**: Access the web interface at [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **API Documentation**: Interactive Swagger UI at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## API Endpoints Overview

- `POST /api/train`: Triggers the `model_training.py` script and dynamically reloads the models.
- `GET /api/stats`: Returns broad dataset statistics (total transactions, fraud rate, success rate).
- `GET /api/charts`: Returns formatted data for dashboard charts (amount distribution, fraud vs. safe, payment app distribution).
- `POST /api/predict`: Takes a JSON payload of transaction details and returns an aggregated risk score (0-1), a binary fraud prediction, individual model scores, and any triggered heuristic risk signals.

## License

This project is licensed under the MIT License.
