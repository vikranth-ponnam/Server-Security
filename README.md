# ClaimWatch AI – Insurance Fraud Detection Platform
**GenAI Forge 2026 | SmartBridge × NASSCOM FutureSkills Prime**

An end-to-end ML web application that detects fraudulent insurance claims using
Random Forest, Decision Tree, and XGBoost with a Flask dashboard.

---

## Quick Start (VS Code Terminal)

### 1 – Open project in VS Code
```
File → Open Folder → select "claimwatch_ai"
```
Then open the integrated terminal: **Ctrl + `**

---

### 2 – Create & activate a virtual environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

---

### 3 – Install dependencies
```bash
pip install -r requirements.txt
```

---

### 4 – Generate dataset & train models  *(run ONCE)*
```bash
python generate_data.py
```
This will:
- Create `data/insurance_claims.csv` (5 000 synthetic records)
- Train Random Forest, Decision Tree, XGBoost
- Save the best model to `models/`

---

### 5 – Start the web application
```bash
python app.py
```
Then open your browser at: **http://127.0.0.1:5000**

---

## Pages
| URL | Description |
|-----|-------------|
| `/` | Home / landing page |
| `/predict` | Claim input form → fraud risk score |
| `/dashboard` | Model performance metrics |
| `/api/predict` | JSON REST API (POST) |

---

## REST API Example
```bash
curl -X POST http://127.0.0.1:5000/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "age": 45,
    "policy_tenure_years": 3,
    "claim_amount": 80000,
    "annual_premium": 2000,
    "num_claims_history": 8,
    "days_to_report": 45,
    "incident_severity": "Major",
    "insurance_type": "Auto",
    "incident_type": "Theft",
    "police_report_filed": 0,
    "witnesses": 0,
    "vehicle_age_years": 12,
    "deductible_amount": 500,
    "customer_region": "North"
  }'
```

---

## Project Structure
```
claimwatch_ai/
├── app.py                 # Flask application
├── generate_data.py       # Data generation + model training
├── requirements.txt       # Python dependencies
├── README.md
├── data/
│   └── insurance_claims.csv   (generated)
├── models/
│   ├── best_model.pkl         (generated)
│   ├── scaler.pkl             (generated)
│   ├── encoders.pkl           (generated)
│   ├── feature_cols.pkl       (generated)
│   └── results_summary.pkl    (generated)
└── templates/
    ├── base.html
    ├── index.html
    ├── predict.html
    ├── result.html
    └── dashboard.html
```

---

## Tech Stack
| Layer | Technology |
|-------|-----------|
| Language | Python 3.9+ |
| Web Framework | Flask 3.0 |
| ML Models | Random Forest, Decision Tree, XGBoost |
| Data Processing | Pandas, NumPy, Scikit-learn |
| Class Balancing | SMOTE (imbalanced-learn) |
| Frontend | Bootstrap 5, Chart.js |

---

## Useful VS Code Commands

| Task | Command |
|------|---------|
| Open terminal | Ctrl + ` |
| Run current file | Ctrl + F5 |
| Stop server | Ctrl + C |
| Format Python file | Shift + Alt + F |
| Search in project | Ctrl + Shift + F |
| Command Palette | Ctrl + Shift + P |

---

*Built for GenAI Forge 2026 – SmartBridge × NASSCOM FutureSkills Prime*
