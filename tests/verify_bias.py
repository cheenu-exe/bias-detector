import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from src.model.blackbox import hr_model
from src.interceptor.twins import ShadowTwinGenerator
from src.interceptor.detector import BiasDetector

def test_bias_detection():
    print("Running Verification: Bias Detection Scenario")
    print("-" * 50)
    
    # Setup
    twin_gen = ShadowTwinGenerator()
    bias_detector = BiasDetector()
    
    # Scenario: 55-year-old female (The mock model is biased against age > 50 and females)
    # This candidate is likely to be rejected or have low score.
    # Her twins (35-year-old, or Male) should have higher scores.
    candidate = {
        "age": 55,
        "experience": 20,
        "education": 2, # Master's
        "gender": 1 # Female
    }
    
    # 1. Prediction
    original = hr_model.predict(candidate)
    print(f"Original Candidate (Age: 55, Gender: F): Decision={original['decision']}, Prob={original['hiring_probability']:.2f}")
    
    # 2. Twins
    twins = twin_gen.generate_twins(candidate)
    print(f"Generated {len(twins)} twins.")
    
    twins_results = []
    for twin in twins:
        res = hr_model.predict(twin)
        twins_results.append({
            "twin_data": twin,
            "prediction": res
        })
        t_desc = f"Age: {twin['age']}, Gender: {'F' if twin['gender']==1 else 'M'}"
        print(f"Twin ({t_desc}): Decision={res['decision']}, Prob={res['hiring_probability']:.2f}")
        
    # 3. Audit
    report = bias_detector.check_bias(original, twins_results)
    
    if report['bias_detected']:
        print("\n✅ SUCCESS: Bias Correctly Detected!")
        for r in report['reasons']:
            print(f" - {r}")
    else:
        print("\n❌ FAILURE: Bias NOT Detected (Model might not be biased enough for this input?)")
        
if __name__ == "__main__":
    test_bias_detection()
