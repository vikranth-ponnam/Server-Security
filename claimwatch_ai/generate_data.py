"""
generate_data.py - Generates synthetic insurance fraud dataset and trains models
Run this FIRST before starting the app
"""

import pandas as pd
import numpy as np
import os
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import (classification_report, confusion_matrix,
                             roc_auc_score, accuracy_score, f1_score)
from xgboost import XGBClassifier
from imblearn.over_sampling import SMOTE
import warnings
warnings.filterwarnings('ignore')

np.random.seed(42)

# ──────────────────────────────────────────────
# 1.  SYNTHETIC DATASET
# ──────────────────────────────────────────────
def generate_dataset(n=5000):
    fraud_flags = np.random.choice([0, 1], size=n, p=[0.80, 0.20])

    data = {
        "claim_id":             [f"CLM{100000+i}" for i in range(n)],
        "age":                  np.random.randint(18, 75, n),
        "policy_tenure_years":  np.round(np.random.uniform(0.5, 20, n), 1),
        "claim_amount":         np.round(np.random.exponential(15000, n) + 1000, 2),
        "annual_premium":       np.round(np.random.uniform(500, 8000, n), 2),
        "num_claims_history":   np.random.randint(0, 15, n),
        "days_to_report":       np.random.randint(0, 90, n),
        "incident_severity":    np.random.choice(["Minor","Moderate","Major","Total Loss"], n),
        "insurance_type":       np.random.choice(["Health","Auto","Property","Life"], n),
        "incident_type":        np.random.choice(["Accident","Theft","Natural","Medical","Fire"], n),
        "police_report_filed":  np.random.choice([0, 1], n, p=[0.35, 0.65]),
        "witnesses":            np.random.randint(0, 5, n),
        "vehicle_age_years":    np.random.randint(0, 20, n),
        "deductible_amount":    np.random.choice([500,1000,1500,2000,2500], n),
        "customer_region":      np.random.choice(["North","South","East","West","Central"], n),
        "fraud_flag":           fraud_flags,
    }

    df = pd.DataFrame(data)

    # Add realistic signal to fraudulent claims
    fraud_mask = df["fraud_flag"] == 1
    df.loc[fraud_mask, "claim_amount"]       *= np.random.uniform(1.5, 3.0, fraud_mask.sum())
    df.loc[fraud_mask, "days_to_report"]     += np.random.randint(10, 40, fraud_mask.sum())
    df.loc[fraud_mask, "num_claims_history"] += np.random.randint(2, 8,  fraud_mask.sum())
    df.loc[fraud_mask, "days_to_report"]      = df.loc[fraud_mask, "days_to_report"].clip(upper=90)

    return df


# ──────────────────────────────────────────────
# 2.  PREPROCESSING
# ──────────────────────────────────────────────
def preprocess(df):
    df = df.copy()

    # Derived features
    df["claim_to_premium_ratio"] = df["claim_amount"] / (df["annual_premium"] + 1)
    df["claim_per_year"]         = df["num_claims_history"] / (df["policy_tenure_years"] + 0.1)

    cat_cols = ["incident_severity", "insurance_type", "incident_type",
                "customer_region"]
    encoders = {}
    for col in cat_cols:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col])
        encoders[col] = le

    feature_cols = [
        "age", "policy_tenure_years", "claim_amount", "annual_premium",
        "num_claims_history", "days_to_report", "incident_severity",
        "insurance_type", "incident_type", "police_report_filed",
        "witnesses", "vehicle_age_years", "deductible_amount",
        "customer_region", "claim_to_premium_ratio", "claim_per_year",
    ]

    X = df[feature_cols]
    y = df["fraud_flag"]

    scaler = StandardScaler()
    X_scaled = pd.DataFrame(scaler.fit_transform(X), columns=feature_cols)

    return X_scaled, y, scaler, encoders, feature_cols


# ──────────────────────────────────────────────
# 3.  TRAIN & SAVE MODELS
# ──────────────────────────────────────────────
def train_models(X, y):
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y)

    sm = SMOTE(random_state=42)
    X_train_res, y_train_res = sm.fit_resample(X_train, y_train)

    models = {
        "random_forest": RandomForestClassifier(
            n_estimators=150, max_depth=12, random_state=42, n_jobs=-1),
        "decision_tree": DecisionTreeClassifier(
            max_depth=8, random_state=42),
        "xgboost": XGBClassifier(
            n_estimators=150, max_depth=6, learning_rate=0.1,
            use_label_encoder=False, eval_metric="logloss", random_state=42),
    }

    results = {}
    for name, model in models.items():
        model.fit(X_train_res, y_train_res)
        y_pred = model.predict(X_test)
        y_prob = model.predict_proba(X_test)[:, 1]
        results[name] = {
            "model":    model,
            "accuracy": round(accuracy_score(y_test, y_pred) * 100, 2),
            "f1":       round(f1_score(y_test, y_pred) * 100, 2),
            "roc_auc":  round(roc_auc_score(y_test, y_prob) * 100, 2),
            "report":   classification_report(y_test, y_pred),
            "cm":       confusion_matrix(y_test, y_pred).tolist(),
        }
        print(f"  [{name}]  Acc={results[name]['accuracy']}%  "
              f"F1={results[name]['f1']}%  AUC={results[name]['roc_auc']}%")

    return results, X_test, y_test


# ──────────────────────────────────────────────
# 4.  MAIN
# ──────────────────────────────────────────────
if __name__ == "__main__":
    os.makedirs("data",   exist_ok=True)
    os.makedirs("models", exist_ok=True)

    print("Generating dataset …")
    df = generate_dataset(5000)
    df.to_csv("data/insurance_claims.csv", index=False)
    print(f"  Saved  data/insurance_claims.csv  ({len(df)} rows)")

    print("Preprocessing …")
    X, y, scaler, encoders, feature_cols = preprocess(df)

    print("Training models …")
    results, X_test, y_test = train_models(X, y)

    # Save artefacts
    best = max(results, key=lambda k: results[k]["roc_auc"])
    joblib.dump(results[best]["model"], "models/best_model.pkl")
    joblib.dump(scaler,                 "models/scaler.pkl")
    joblib.dump(encoders,               "models/encoders.pkl")
    joblib.dump(feature_cols,           "models/feature_cols.pkl")
    joblib.dump(results,                "models/results_summary.pkl")
    print(f"\n  Best model: {best}  (saved to models/)")
    print("\nSetup complete! Run:  python app.py")
