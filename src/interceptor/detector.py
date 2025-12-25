class BiasDetector:
    def __init__(self, probability_threshold=0.1):
        self.probability_threshold = probability_threshold

    def check_bias(self, original_result: dict, twins_results: list):
        """
        Compares original result with twins results.
        Returns a report dictionary.
        """
        bias_detected = False
        reasons = []

        for twin_res in twins_results:
            twin_data = twin_res['twin_data']
            twin_prediction = twin_res['prediction']
            twin_type = twin_data.get('twin_type', 'unknown')

            # Check 1: Decision Flip (Hard Bias)
            if original_result['decision'] != twin_prediction['decision']:
                bias_detected = True
                reasons.append(f"Decision flipped when {twin_type} was tested. Original: {original_result['decision']}, Twin: {twin_prediction['decision']}")

            # Check 2: Probability deviation (Soft Bias)
            # e.g., if a woman has 45% chance and man has 80% chance, even if both are '0' (rejected), that's a big gap.
            prob_diff = abs(original_result['hiring_probability'] - twin_prediction['hiring_probability'])
            if prob_diff > self.probability_threshold:
                 # Only flag if not already flagged by decision flip to avoid redundancy, or flag as additional info
                 reasons.append(f"High probability divergence ({prob_diff:.2f}) for {twin_type}.")
                 bias_detected = True

        return {
            "bias_detected": bias_detected,
            "reasons": reasons,
            "twin_details": twins_results
        }
