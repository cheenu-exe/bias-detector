import pandas as pd
import numpy as np
import logging
from src.utils import generate_synthetic_data
from src.audit import BiasAuditor
from src.screen import DataScreener
from src.report import BiasReporter

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

class MockModel:
    """
    Simulates a biased model for demonstration purposes.
    """
    def __init__(self):
        self.weights = {'experience': 0.05, 'education': 0.1, 'gender': 0.2}
        self.intercept = -0.5

    def fit(self, X, y):
        # Mock training - just keeping the hardcoded weights that mimic the data generation bias
        pass

    def predict(self, X):
        # Linear combination + threshold
        scores = (X['experience'] * self.weights['experience'] + 
                  X['education'] * self.weights['education'] + 
                  X['gender'] * self.weights['gender'] + 
                  self.intercept)
        # Add some noise
        scores += np.random.normal(0, 0.1, len(X))
        return (scores > 0.5).astype(int)

    def predict_proba(self, X):
        # Mock probabilities
        scores = (X['experience'] * self.weights['experience'] + 
                  X['education'] * self.weights['education'] + 
                  X['gender'] * self.weights['gender'] + 
                  self.intercept)
        # Sigmoid-ish
        probs = 1 / (1 + np.exp(-scores))
        return np.vstack([1-probs, probs]).T

def simple_train_test_split(df, test_size=0.3):
    """
    Simple split function to replace sklearn's.
    """
    mask = np.random.rand(len(df)) < (1 - test_size)
    train = df[mask]
    test = df[~mask]
    return train, test

def run_demo():
    print("=== Bias Detection Tool Demo ===")
    
    # 1. Data Generation
    print("\n[1] Generating Synthetic Data (with bias)...")
    df = generate_synthetic_data(n_samples=2000, bias_level=0.8)
    
    print(f"Data shape: {df.shape}")
    print("Class distribution:\n", df['hired'].value_counts())
    
    # Split Data
    train_df, test_df = simple_train_test_split(df, test_size=0.3)
    
    X_train = train_df[['experience', 'education', 'gender']]
    y_train = train_df['hired']
    X_test = test_df[['experience', 'education', 'gender']]
    y_test = test_df['hired']
    
    # 2. Model Training (Simulating the "Black Box")
    print("\n[2] Training a (Mock) Model...")
    model = MockModel()
    model.fit(X_train, y_train)
    print("Model trained (simulated).")
    
    # 3. Historical Bias Audit
    print("\n[3] Running Historical Bias Audit...")
    # Prepare a dataframe with predictions for auditing
    audit_df = X_test.copy()
    audit_df['hired_true'] = y_test
    # Need to align indexes for assignment if not aligned
    preds = model.predict(X_test)
    audit_df['hired_pred'] = preds
    
    auditor = BiasAuditor(
        data=audit_df,
        protected_attribute='gender',
        privileged_group=1,
        unprivileged_group=0,
        label_column='hired_pred',
        favorable_label=1
    )
    
    audit_results = auditor.run_complete_audit(true_label_column='hired_true')
    print("Audit Metrics:", audit_results)
    
    # Run Perturbation Testing
    print("Running Perturbation Testing...")
    perturb_results = auditor.run_perturbation_test(model_predict_fn=model.predict)
    audit_results['perturbation_test'] = perturb_results
    print(f"Perturbation Flip Rate: {perturb_results['flip_rate']:.2%}")

    # 4. Real-Time Screening
    print("\n[4] Simulating Real-Time Data Stream...")
    screener = DataScreener(reference_data=X_train, protected_attribute='gender')
    
    # Generate new batch with slight drift
    new_batch = generate_synthetic_data(n_samples=50, bias_level=0.5)
    new_batch['experience'] = new_batch['experience'] + 2.0 # Drift
    
    drift_results = screener.check_distributional_drift(new_batch)
    print("Drift Detected:", [k for k, v in drift_results.items() if v['drift_detected']])
    
    proxy_results = screener.check_for_proxies(new_batch)
    print("Potential Proxies detected (if any).") 
    # Proxies check might be empty if we don't include correlated vars, but functionality is there.
    
    screen_results = {
        "drift": drift_results,
        "proxies": proxy_results
    }
    
    # 5. Reporting
    print("\n[5] Generating Bias Scorecard...")
    reporter = BiasReporter()
    reporter.add_audit_results(audit_results)
    reporter.add_screening_results(screen_results)
    
    # Attempt explanation (will use fallback or error since SHAP missing)
    print("Generating explanation for a sample prediction (Mocking SHAP)...")
    sample_input = X_test.iloc[0:1] # Take one sample
    explanation = reporter.explain_prediction(model, sample_input, method='shap', train_data=X_train)
    
    scorecard = reporter.generate_scorecard()
    print("\n--- FINAL BIAS SCORECARD ---")
    print(scorecard)
    
    # Save scorecard
    with open("bias_scorecard.json", "w") as f:
        f.write(scorecard)
    print("\nScorecard saved to bias_scorecard.json")

if __name__ == "__main__":
    run_demo()
