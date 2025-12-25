import copy

class ShadowTwinGenerator:
    def __init__(self):
        # Define sensitive ranges or categories to flip
        self.sensitive_attributes = ['gender', 'age']

    def generate_twins(self, input_data: dict):
        """
        Generates counterfactuals for the input data.
        Returns a list of dictionaries (twins).
        """
        twins = []
        original = input_data

        # Twin 1: Flip Gender (Assuming binary 0/1 for MVP)
        # If input has 'gender', create a twin with the opposite gender
        if 'gender' in original:
            gender_twin = copy.deepcopy(original)
            gender_twin['gender'] = 1 - original['gender'] # Flip 0->1, 1->0
            gender_twin['twin_type'] = 'gender_flip'
            twins.append(gender_twin)

        # Twin 2: Age Counterfactuals
        # If age > 50, try a younger age (e.g., 35)
        # If age < 50, try an older age (e.g., 55)
        if 'age' in original:
            age_twin = copy.deepcopy(original)
            if original['age'] > 50:
                age_twin['age'] = 35
                age_twin['twin_type'] = 'age_younger'
            else:
                age_twin['age'] = 55
                age_twin['twin_type'] = 'age_older'
            twins.append(age_twin)
            
        return twins
