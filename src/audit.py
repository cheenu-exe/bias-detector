import pandas as pd
import numpy as np

# In a real scenario, we might import aif360 here, but for this implementation
# we will write the metric calculations from scratch to ensure they work 
# without complex dependencies, while mimicking the logic.

class BiasAuditor:
    def __init__(self, data, protected_attribute, privileged_group, unprivileged_group, label_column, favorable_label):
        """
        Initialize the auditor.
        
        Args:
            data (pd.DataFrame): The dataset containing features and labels.
            protected_attribute (str): Name of the column representing the protected class.
            privileged_group (any): Value indicating the privileged group.
            unprivileged_group (any): Value indicating the unprivileged group.
            label_column (str): Name of the column representing the ground truth or prediction.
            favorable_label (any): Value indicating a positive/favorable outcome.
        """
        self.df = data
        self.protected_attribute = protected_attribute
        self.privileged_group = privileged_group
        self.unprivileged_group = unprivileged_group
        self.label_column = label_column
        self.favorable_label = favorable_label

    def calculate_disparate_impact(self):
        """
        Calculate Disparate Impact (DI).
        DI = P(Y=1 | D=unprivileged) / P(Y=1 | D=privileged)
        """
        priv_df = self.df[self.df[self.protected_attribute] == self.privileged_group]
        unpriv_df = self.df[self.df[self.protected_attribute] == self.unprivileged_group]
        
        if len(priv_df) == 0 or len(unpriv_df) == 0:
            return None

        priv_pos_rate = len(priv_df[priv_df[self.label_column] == self.favorable_label]) / len(priv_df)
        unpriv_pos_rate = len(unpriv_df[unpriv_df[self.label_column] == self.favorable_label]) / len(unpriv_df)
        
        if priv_pos_rate == 0:
            return 0.0 # Avoid division by zero, though logically strange implication
            
        di = unpriv_pos_rate / priv_pos_rate
        return di

    def calculate_statistical_parity_difference(self):
        """
        Calculate Statistical Parity Difference (SPD).
        SPD = P(Y=1 | D=unprivileged) - P(Y=1 | D=privileged)
        """
        priv_df = self.df[self.df[self.protected_attribute] == self.privileged_group]
        unpriv_df = self.df[self.df[self.protected_attribute] == self.unprivileged_group]
        
        if len(priv_df) == 0 or len(unpriv_df) == 0:
            return None

        priv_pos_rate = len(priv_df[priv_df[self.label_column] == self.favorable_label]) / len(priv_df)
        unpriv_pos_rate = len(unpriv_df[unpriv_df[self.label_column] == self.favorable_label]) / len(unpriv_df)
        
        spd = unpriv_pos_rate - priv_pos_rate
        return spd

    def calculate_equal_opportunity_difference(self, true_label_column):
        """
        Calculate Equal Opportunity Difference (EOD).
        Difference in True Positive Rates (TPR).
        EOD = TPR_unprivileged - TPR_privileged
        
        Requires ground truth labels to identify true positives.
        
        Args:
            true_label_column (str): Name of the column with ground truth labels.
        """
        # Filter for actual positive cases (Y_true = 1)
        # We need to assess recall/TPR for these groups.
        
        actual_positives = self.df[self.df[true_label_column] == self.favorable_label]
        
        priv_df = actual_positives[actual_positives[self.protected_attribute] == self.privileged_group]
        unpriv_df = actual_positives[actual_positives[self.protected_attribute] == self.unprivileged_group]
        
        if len(priv_df) == 0 or len(unpriv_df) == 0:
            return None # Cannot calculate TPR if there are no actual positives in a group

        # TPR = TP / (TP + FN) = (Predicted=1 & True=1) / (True=1)
        # Since we filtered `actual_positives`, len(priv_df) is (TP+FN).
        # We just need to count how many of these were PREDICTED as positive.
        
        priv_tpr = len(priv_df[priv_df[self.label_column] == self.favorable_label]) / len(priv_df)
        unpriv_tpr = len(unpriv_df[unpriv_df[self.label_column] == self.favorable_label]) / len(unpriv_df)
        
        eod = unpriv_tpr - priv_tpr
        return eod

    def run_complete_audit(self, true_label_column=None):
        """
        Runs all configured metrics and returns a dictionary.
        """
        results = {
            "disparate_impact": self.calculate_disparate_impact(),
            "statistical_parity_difference": self.calculate_statistical_parity_difference()
        }
        
        if true_label_column:
            results["equal_opportunity_difference"] = self.calculate_equal_opportunity_difference(true_label_column)
            
        return results

    def run_perturbation_test(self, model_predict_fn, sensitive_value=None):
        """
        Runs perturbation testing by flipping the protected attribute and checking for label changes.
        
        Args:
            model_predict_fn (callable): A function that takes a DataFrame and returns predictions.
            sensitive_value (any): The value to flip to/from. If None, uses unprivileged_group.
        
        Returns:
            dict: Summary of flip rate and indices of flipped samples.
        """
        if sensitive_value is None:
            sensitive_value = self.unprivileged_group
            
        # Create perturbed data
        # We assume binary protected attribute for simplicity in this demo
        df_perturbed = self.df.copy()
        
        # Simple flip logic: if it matches optimal/sensitive, flip it.
        # This assumes the column is binary 0/1 or similar.
        # For more complex cases, we'd need explicit mapping.
        
        # For this implementation, we assume we are testing: "If I change Unprivileged -> Privileged, does outcome change?"
        # So we only look at rows currently in Unprivileged group.
        
        target_rows = self.df[self.df[self.protected_attribute] == self.unprivileged_group].index
        
        if len(target_rows) == 0:
            return {"flip_rate": 0.0, "flipped_indices": []}
            
        # Set them to privileged
        df_perturbed.loc[target_rows, self.protected_attribute] = self.privileged_group
        
        # Get original predictions (if not already in df, but we usually audit trained models)
        # Using the passed predict_fn to ensure we test the model's current behavior
        original_preds = model_predict_fn(self.df.loc[target_rows])
        new_preds = model_predict_fn(df_perturbed.loc[target_rows])
        
        # Check differences
        diff = (original_preds != new_preds)
        flip_count = np.sum(diff)
        flip_rate = flip_count / len(target_rows)
        
        return {
            "flip_rate": flip_rate,
            "flipped_indices": target_rows[diff].tolist(),
            "analyzed_count": len(target_rows)
        }

