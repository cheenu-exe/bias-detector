from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import pandas as pd
import io
import json
import logging

from src.utils import generate_synthetic_data
from src.audit import BiasAuditor
from src.screen import DataScreener
from src.report import BiasReporter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api")

app = FastAPI(title="Bias Detection Dashboard")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global configuration / State
# In a real app, this would be per-session or database-backed.
class SystemState:
    def __init__(self):
        self.reporter = BiasReporter()
        self.ref_data = generate_synthetic_data(n_samples=2000, bias_level=0.5)
        logger.info("System State Initialized with Reference Data")

state = SystemState()

class ScreenInput(BaseModel):
    data: List[Dict[str, Any]]

@app.get("/api/state")
def get_system_state():
    return {"status": "Active", "reference_data_size": len(state.ref_data)}

@app.get("/api/generate_data")
def get_sample_data(n_samples: int = 200):
    """Generates synthetic biased data for the user to play with."""
    df = generate_synthetic_data(n_samples=n_samples, bias_level=0.8)
    return json.loads(df.to_json(orient="records"))

@app.post("/api/audit")
async def run_audit(file: UploadFile = File(...)):
    """Runs the Historical Bias Audit on uploaded file."""
    try:
        content = await file.read()
        try:
            df = pd.read_json(io.BytesIO(content))
        except ValueError:
            df = pd.read_csv(io.BytesIO(content))
    except Exception as e:
        logger.error(f"File upload error: {e}")
        raise HTTPException(status_code=400, detail="Invalid file format. Upload CSV or JSON.")
            
    # Mock Prediction Augmentation
    # If the user uploads raw data without predictions, we simulate a model's output
    if 'hired_pred' not in df.columns:
        # Check if we have the columns for our heuristic
        if 'experience' in df.columns and 'gender' in df.columns:
             # Heuristic: Biased logic (Male & High Experience = Hired)
            df['hired_pred'] = ((df['experience'] > 4) & (df['gender'] == 1)).astype(int)
        else:
            # Fallback: Random predictions if columns don't match our demo schema
            import numpy as np
            logger.warning("Missing 'experience' or 'gender' columns. Generating random predictions.")
            df['hired_pred'] = np.random.randint(0, 2, df.shape[0])
    
    auditor = BiasAuditor(
        data=df,
        protected_attribute='gender',
        privileged_group=1,
        unprivileged_group=0,
        label_column='hired_pred',
        favorable_label=1
    )
    
    # Run audit
    # Check if ground truth exists
    true_col = 'hired' if 'hired' in df.columns else None
    results = auditor.run_complete_audit(true_label_column=true_col)
    
    # Run perturbation test (using a mock function that mimics the logic above)
    def mock_predict(sub_df):
        return ((sub_df['experience'] > 4) & (sub_df['gender'] == 1)).astype(int)
        
    perturb_results = auditor.run_perturbation_test(mock_predict)
    results['perturbation_test'] = perturb_results
    
    # Update global reporter
    state.reporter.add_audit_results(results)
    
    return results

@app.post("/api/screen")
def screen_data(input_data: ScreenInput):
    """Runs Real-Time Screening on a batch of data."""
    df = pd.DataFrame(input_data.data)
    
    if df.empty:
        return {"error": "No data provided"}

    screener = DataScreener(reference_data=state.ref_data, protected_attribute='gender')
    
    # Check Drift
    drift_results = screener.check_distributional_drift(df, threshold=0.05)
    
    # Check Proxies
    # Needs accumulated data to be meaningful, but we run it on the batch
    proxy_results = screener.check_for_proxies(pd.concat([state.ref_data, df], ignore_index=True))
    
    screen_results = {
        "drift": drift_results,
        "proxies": proxy_results,
        "batch_risk": "High" if any(d['drift_detected'] for d in drift_results.values()) else "Low"
    }
    
    state.reporter.add_screening_results(screen_results)
    return screen_results

@app.get("/api/report")
def get_report():
    """Returns the current accumulated Bias Scorecard."""
    return json.loads(state.reporter.generate_scorecard())

# Mount Frontend
app.mount("/", StaticFiles(directory="web", html=True), name="static")
