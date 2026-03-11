"""
app.py – ClaimWatch AI  Flask application
"""

from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
import joblib
import os
import json

app = Flask(__name__)

# ──────────────────────────────────────────────
# Load saved artefacts (created by generate_data.py)
# ──────────────────────────────────────────────
MODEL = SCALER = ENCODERS = FEATURE_COLS = RESULTS = None

def load_artefacts():
    global MODEL, SCALER, ENCODERS, FEATURE_COLS, RESULTS
    try:
        MODEL        = joblib.load("models/best_model.pkl")
        SCALER       = joblib.load("models/scaler.pkl")
        ENCODERS     = joblib.load("models/encoders.pkl")
        FEATURE_COLS = joblib.load("models/feature_cols.pkl")
        RESULTS      = joblib.load("models/results_summary.pkl")
        print("  Artefacts loaded successfully.")
    except FileNotFoundError:
        print("  WARNING: models not found – run  python generate_data.py  first.")

load_artefacts()

# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────
SEV_MAP  = {"Minor": 0, "Moderate": 1, "Major": 2, "Total Loss": 3}
INS_MAP  = {"Auto": 0, "Health": 1, "Life": 2, "Property": 3}
INC_MAP  = {"Accident": 0, "Fire": 1, "Medical": 2, "Natural": 3, "Theft": 4}
REG_MAP  = {"Central": 0, "East": 1, "North": 2, "South": 3, "West": 4}

def risk_label(prob):
    if prob >= 0.70: return "High Risk",   "danger"
    if prob >= 0.40: return "Medium Risk", "warning"
    return "Low Risk", "success"

def build_features(form):
    age               = float(form["age"])
    tenure            = float(form["policy_tenure_years"])
    claim_amt         = float(form["claim_amount"])
    premium           = float(form["annual_premium"])
    num_claims        = float(form["num_claims_history"])
    days_report       = float(form["days_to_report"])
    sev               = SEV_MAP[form["incident_severity"]]
    ins_type          = INS_MAP[form["insurance_type"]]
    inc_type          = INC_MAP[form["incident_type"]]
    police            = int(form["police_report_filed"])
    witnesses         = float(form["witnesses"])
    veh_age           = float(form["vehicle_age_years"])
    deductible        = float(form["deductible_amount"])
    region            = REG_MAP[form["customer_region"]]

    claim_to_premium  = claim_amt / (premium + 1)
    claim_per_year    = num_claims / (tenure + 0.1)

    raw = pd.DataFrame([[
        age, tenure, claim_amt, premium, num_claims, days_report,
        sev, ins_type, inc_type, police, witnesses, veh_age,
        deductible, region, claim_to_premium, claim_per_year,
    ]], columns=FEATURE_COLS)

    return SCALER.transform(raw)

# ──────────────────────────────────────────────
# Routes
# ──────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/predict", methods=["GET", "POST"])
def predict():
    if request.method == "GET":
        return render_template("predict.html")

    try:
        feats = build_features(request.form)
        prob  = float(MODEL.predict_proba(feats)[0][1])
        label, color = risk_label(prob)

        # Feature importances (if available)
        importance_data = []
        if hasattr(MODEL, "feature_importances_"):
            imp = MODEL.feature_importances_
            pairs = sorted(zip(FEATURE_COLS, imp), key=lambda x: x[1], reverse=True)[:8]
            importance_data = [{"feature": f, "importance": round(float(v)*100, 2)} for f, v in pairs]

        return render_template(
            "result.html",
            prob=round(prob * 100, 2),
            label=label,
            color=color,
            form_data=request.form,
            importance_data=json.dumps(importance_data),
        )
    except Exception as e:
        return render_template("predict.html", error=str(e))

@app.route("/dashboard")
def dashboard():
    if RESULTS is None:
        return render_template("dashboard.html", metrics=None)
    metrics = {
        name: {
            "accuracy": v["accuracy"],
            "f1":       v["f1"],
            "roc_auc":  v["roc_auc"],
            "cm":       v["cm"],
        }
        for name, v in RESULTS.items()
    }
    return render_template("dashboard.html", metrics=json.dumps(metrics))

@app.route("/api/predict", methods=["POST"])
def api_predict():
    """JSON API endpoint"""
    try:
        data  = request.get_json()
        feats = build_features(data)
        prob  = float(MODEL.predict_proba(feats)[0][1])
        label, _ = risk_label(prob)
        return jsonify({"fraud_probability": round(prob, 4),
                        "risk_label": label,
                        "is_fraud": prob >= 0.5})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(debug=True, port=5000)
