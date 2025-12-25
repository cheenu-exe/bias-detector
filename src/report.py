import json
import logging

try:
    import shap
    import lime
    import lime.lime_tabular
except ImportError:
    logging.warning("SHAP or LIME not found. Explainability features will be limited.")
    shap = None
    lime = None

class BiasReporter:
    def __init__(self):
        self.report_data = {}

    def add_audit_results(self, audit_results):
        """
        Adds historical audit results to the report.
        """
        self.report_data["historical_audit"] = audit_results

    def add_screening_results(self, screening_results):
        """
        Adds real-time screening results to the report.
        """
        self.report_data["screening_checks"] = screening_results

    def generate_scorecard(self, output_format="json"):
        """
        Generates the Bias Scorecard.
        """
        if output_format == "json":
            return json.dumps(self.report_data, indent=4)
        else:
            # Simple text summary
             return str(self.report_data)

    def explain_prediction(self, model, input_data, method="shap", train_data=None):
        """
        Generate an explanation for a specific prediction using SHAP or LIME.
        
        Args:
            model: The trained model object (must implement predict/predict_proba).
            input_data: The specific instance(s) to explain.
            method (str): 'shap' or 'lime'.
            train_data: Training data (required for SHAP/LIME initialization).
        """
        explanation = {}
        
        if method == "shap":
            if shap is None:
                return {"error": "SHAP library not installed"}
            
            # Using KernelExplainer as a generic fallback, or TreeExplainer if tree-based
            # For this demo, we assume KernelExplainer or LinearExplainer
            try:
                # This is a simplified wrapper. Real usage depends on model type.
                explainer = shap.KernelExplainer(model.predict, train_data)
                shap_values = explainer.shap_values(input_data)
                explanation["shap_values"] = shap_values.tolist() if hasattr(shap_values, 'tolist') else shap_values
            except Exception as e:
                explanation["error"] = str(e)
                
        elif method == "lime":
            if lime is None:
                return {"error": "LIME library not installed"}
                
            try:
                explainer = lime.lime_tabular.LimeTabularExplainer(
                    training_data=train_data.values, 
                    feature_names=train_data.columns.tolist(),
                    mode='classification'
                )
                
                # Explain first instance
                exp = explainer.explain_instance(input_data.values[0], model.predict_proba)
                explanation["lime_explanation"] = exp.as_list()
            except Exception as e:
                explanation["error"] = str(e)
                
        return explanation
