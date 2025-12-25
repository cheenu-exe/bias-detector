from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from src.model.blackbox import hr_model
from src.interceptor.twins import ShadowTwinGenerator
from src.interceptor.detector import BiasDetector

app = FastAPI(title="Runtime Verification Layer", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For dev purposes, allow all. In prod, strict listing.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data Model
class CandidateProfile(BaseModel):
    age: int
    experience: int
    education: int # 1=BS, 2=MS, 3=PhD
    gender: int # 0=Male, 1=Female

# Components
twin_gen = ShadowTwinGenerator()
bias_detector = BiasDetector()

@app.get("/")
def read_root():
    return {"status": "Active", "message": "Runtime Verification Layer is running."}

@app.post("/predict")
def predict_and_verify(profile: CandidateProfile):
    data = profile.dict()
    
    # 1. Get the "Real" Model Decision
    try:
        original_result = hr_model.predict(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    # 2. Generate Shadow Twins (Runtime Interception)
    twins = twin_gen.generate_twins(data)
    
    # 3. Probe Model with Twins
    twins_results = []
    for twin in twins:
        res = hr_model.predict(twin)
        twins_results.append({
            "twin_data": twin,
            "prediction": res
        })
        
    # 4. Check for Bias
    bias_report = bias_detector.check_bias(original_result, twins_results)
    
    # 5. Return Augmented Response
    return {
        "model_decision": original_result,
        "verification_report": bias_report
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
