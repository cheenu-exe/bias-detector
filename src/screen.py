import pandas as pd
import numpy as np
from scipy import stats

class DataScreener:
    def __init__(self, reference_data, protected_attribute):
        """
        Initialize the screener with reference (training) data.
        
        Args:
            reference_data (pd.DataFrame): The "fair" or original training data.
            protected_attribute (str): The column name of the protected attribute.
        """
        self.ref_data = reference_data
        self.protected_attribute = protected_attribute
        
    def check_distributional_drift(self, new_batch, features=None, threshold=0.05):
        """
        Check for distributional drift between reference data and new batch using KS-Test.
        
        Args:
            new_batch (pd.DataFrame): Incoming data stream.
            features (list): List of features to check. If None, checks all numerical columns.
            threshold (float): P-value threshold. If p < threshold, distributions are different.
            
        Returns:
            dict: Dictionary of features with drift detected.
        """
        drift_report = {}
        if features is None:
            features = self.ref_data.select_dtypes(include=[np.number]).columns.tolist()
            
        for feature in features:
            if feature not in new_batch.columns:
                continue
                
            # KS Test
            stat, p_value = stats.ks_2samp(self.ref_data[feature], new_batch[feature])
            
            is_drift = p_value < threshold
            drift_report[feature] = {
                "drift_detected": bool(is_drift),
                "p_value": float(p_value),
                "statistic": float(stat)
            }
            
        return drift_report

    def check_for_proxies(self, new_batch, threshold=0.7):
        """
        Detect potential proxies by checking correlation of features with the protected attribute.
        
        Args:
            new_batch (pd.DataFrame): Dataset to analyze (can be combined ref + new).
            threshold (float): Correlation coefficient threshold to flag as proxy.
            
        Returns:
            dict: Features flagged as proxies.
        """
        # We need the protected attribute in the data to check correlations.
        # If it's not in new_batch (e.g., hidden in deployment), this check works on 
        # the assumption we have it or are auditing a labeled batch.
        
        if self.protected_attribute not in new_batch.columns:
            return {"error": "Protected attribute not found in batch for proxy detection."}
            
        correlations = new_batch.corr()
        
        if self.protected_attribute not in correlations:
            # Might be non-numeric, skipping for basic implementation
            return {}
            
        proxies = {}
        target_corr = correlations[self.protected_attribute]
        
        for feature, corr_value in target_corr.items():
            if feature == self.protected_attribute:
                continue
                
            if abs(corr_value) >= threshold:
                proxies[feature] = {
                    "correlation": float(corr_value),
                    "risk": "High"
                }
                
        return proxies

    def screen_input(self, input_row):
        """
        Screen a single input row for high-risk combinations.
        Hardcoded heuristic for demo purposes.
        """
        flags = []
        # Example heuristic: If 'zip_code' is present and matches a high-risk list
        # In a real tool, this would be more sophisticated or use a model.
        
        # Placeholder logic
        return flags
