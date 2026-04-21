# 🏦 Banking Fraud Detection System
### End-to-End Machine Learning Application for Real-Time Transaction Fraud Detection

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Scikit-learn](https://img.shields.io/badge/Scikit--learn-RandomForest-F7931E?style=flat-square&logo=scikit-learn&logoColor=white)](https://scikit-learn.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-REST%20API-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Jupyter](https://img.shields.io/badge/Jupyter-Notebook-F37626?style=flat-square&logo=jupyter&logoColor=white)](https://jupyter.org)
[![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square)](LICENSE)

> **The Problem:** Banks process millions of transactions daily. A single fraudulent transfer can drain a customer's account in seconds — and manual review is too slow, too costly, and doesn't scale. This system uses machine learning to flag suspicious transactions instantly, with a human-readable explanation for every decision.

---

## 🚨 Live Demo — What It Does

| Scenario | Input | Output |
|---|---|---|
| High-risk transaction | Large amount, odd hour, international flag | 🔴 **FRAUD ALERT** — 94% probability |
| Normal transaction | Regular amount, business hours, known location | 🟢 **LEGITIMATE** — 3% probability |

Every prediction includes a **reason** — not just a label. Example:
> *"Flagged due to: unusually high transaction amount (₹85,000), late night hour (2:47 AM), international transaction flag, and 3x above account average."*

---

## 🎯 Business Impact

| Metric | Value |
|---|---|
| **Model Accuracy** | *[Add your accuracy %]* |
| **Precision (Fraud)** | *[Add precision %]* — low false alarms |
| **Recall (Fraud)** | *[Add recall %]* — catches actual fraud |
| **F1-Score** | *[Add F1 score]* |
| **AUC-ROC** | *[Add AUC score]* |
| **Avg Prediction Time** | < 100ms per transaction |

> 💡 **Why Recall matters more than Accuracy here:** A fraud detection model that catches 95% of fraud cases (high recall) but flags 5% of legitimate transactions is far better than a 99% accurate model that misses half of actual fraud.

---

## 🧠 Machine Learning Solution

### Algorithm: Random Forest Classifier

**Why Random Forest for fraud detection?**
- Handles highly imbalanced datasets (fraud is rare — typically <1% of transactions)
- No assumption about data distribution — ideal for financial transaction patterns
- Built-in feature importance — explains *which* factors drove the prediction
- Resistant to overfitting on noisy transaction data
- Fast inference — critical for real-time banking systems

### Pipeline Architecture

```
Raw Transaction Data
        ↓
Feature Engineering (time features, ratio features)
        ↓
Preprocessing (StandardScaler + OneHotEncoder)
        ↓
Random Forest Classifier
        ↓
Fraud Probability + Prediction Label + Reason Text
        ↓
FastAPI REST Endpoint → UI → SQLite Log
```

---

## 📊 Features Used for Fraud Detection

| Feature | Type | Why It Matters |
|---|---|---|
| `transaction_amount` | Numeric | Unusually large amounts are high risk |
| `account_balance` | Numeric | Amount vs balance ratio signals fraud |
| `transaction_hour` | Derived | Late-night transactions are suspicious |
| `is_weekend` | Derived | Fraud spikes on weekends |
| `is_international` | Binary | Cross-border transactions are higher risk |
| `customer_age` | Numeric | Elderly customers are targeted more |
| `transaction_frequency` | Numeric | Sudden frequency spikes = red flag |
| `avg_account_amount` | Numeric | Deviation from personal baseline |
| `transaction_type` | Categorical | ATM / POS / Online / Transfer |
| `channel` | Categorical | Branch / ATM / Mobile / Online |
| `account_type` | Categorical | Savings / Current / Credit |
| `location` | Categorical | Known vs unknown location |

---

## 🖥️ System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    USER INTERFACE                       │
│              (HTML Form — Input Transaction)            │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTP POST
┌──────────────────────▼──────────────────────────────────┐
│                   FastAPI Backend                       │
│                     api.py                              │
│  • Receives transaction JSON                            │
│  • Runs fraud_rf_pipeline.joblib                        │
│  • Returns: probability + label + reason text           │
└──────────┬──────────────────────────┬───────────────────┘
           │                          │
┌──────────▼──────────┐   ┌───────────▼───────────────────┐
│   ML Model Pipeline │   │      SQLite Database          │
│ fraud_rf_pipeline   │   │  Logs every prediction for    │
│       .joblib       │   │  audit trail & analytics      │
└─────────────────────┘   └───────────────────────────────┘
```

---

## 📁 Project Structure

```
Banking-Fraud-Detection-Project/
│
├── fraud_detection.ipynb       # Full ML notebook:
│                               #   EDA → Feature Engineering →
│                               #   Model Training → Evaluation
│
├── api.py                      # FastAPI REST API
│                               #   POST /predict → fraud decision
│                               #   Logs to SQLite
│
├── fraud_rf_pipeline.joblib    # Trained & serialised model pipeline
│                               #   (Preprocessor + Random Forest)
│
├── screenshots/                # App UI screenshots
│   ├── ui_input_form.png
│   ├── fraud_alert.png
│   └── not_fraud_alert.png
│
├── requirements.txt            # Python dependencies
├── .gitignore                  # Excludes __pycache__, .db files
├── LICENSE                     # MIT License
└── README.md
```

---

## 🚀 How to Run

### 1. Clone the Repository
```bash
git clone https://github.com/Suresh-Note/Banking-Fraud-Detection-Project.git
cd Banking-Fraud-Detection-Project
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Start the API Server
```bash
uvicorn api:app --reload
```

### 4. Open the UI
Navigate to `http://localhost:8000` in your browser, fill in a transaction, and get an instant fraud prediction.

### 5. Test via API directly
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_amount": 85000,
    "account_balance": 12000,
    "transaction_hour": 2,
    "is_international": 1,
    "customer_age": 67,
    "transaction_type": "Online",
    "channel": "Mobile"
  }'
```

**Response:**
```json
{
  "fraud_probability": 0.94,
  "prediction": "FRAUD",
  "reason": "High-risk: large amount relative to balance, late-night hour, international flag"
}
```

---

## 🖼️ Screenshots

### Input Form
![UI Input Form](https://github.com/user-attachments/assets/0f74d198-e6d3-4b9e-98a3-15dca6a6ee21)

> Enter transaction details — amount, time, type, customer info — and submit for instant analysis.

### 🔴 Fraud Alert
![Fraud Alert](https://github.com/user-attachments/assets/e7a25a40-a876-4c60-b96a-1c0c785f513d)

> High-risk transaction flagged with fraud probability and human-readable reason for the decision.

### 🟢 Legitimate Transaction
![Not Fraud](https://github.com/user-attachments/assets/9d60cea4-6987-49ba-85bd-bd7f2d5b6fa5)

> Normal transaction cleared with low fraud probability score.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **ML Model** | Scikit-learn — Random Forest Classifier |
| **Model Serialisation** | Joblib Pipeline (Preprocessor + Model) |
| **API Framework** | FastAPI |
| **API Server** | Uvicorn (ASGI) |
| **Data Processing** | Pandas, NumPy |
| **Logging / Storage** | SQLite |
| **Notebook / EDA** | Jupyter Notebook |
| **Frontend** | HTML + CSS |

---

## 📌 What Makes This Project Stand Out

✅ **Full ML lifecycle** — EDA → Feature Engineering → Training → Serialisation → API → UI → Logging  
✅ **Explainable predictions** — not a black box; every decision comes with a human-readable reason  
✅ **Production patterns** — REST API, model pipeline, persistent audit log  
✅ **Domain-relevant features** — time-of-day, international flag, amount-to-balance ratio  
✅ **Real-world problem** — fraud detection is a top priority in every bank and FinTech  

---

## 🔭 Improvements Planned

- [ ] Add SHAP values for feature-level explainability per prediction
- [ ] Handle class imbalance with SMOTE oversampling
- [ ] Compare models: Random Forest vs XGBoost vs Logistic Regression
- [ ] Add confusion matrix and ROC-AUC curve to notebook outputs
- [ ] Deploy API on Render / Railway for live public demo
- [ ] Add a fraud analytics dashboard (Power BI or Streamlit) showing logged predictions over time

---

## 👨‍💻 Author

**Suresh Kanchamreddy** — Aspiring Data Analyst & ML Enthusiast

[![GitHub](https://img.shields.io/badge/GitHub-Suresh--Note-181717?style=flat-square&logo=github)](https://github.com/Suresh-Note)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0A66C2?style=flat-square&logo=linkedin)](https://linkedin.com/in/suresh-kanchamreddy)

> *"The best fraud detection system isn't the one with the highest accuracy — it's the one that explains its decisions clearly enough for a banker to act on them."*

---

## 📜 License

MIT License — open source, free to use and adapt. See [LICENSE](LICENSE) for details.
