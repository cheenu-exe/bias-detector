import pandas as pd
import numpy as np

def generate_synthetic_data(n_samples=1000, bias_level=0.8):
    """
    Generates a synthetic dataset with controlled bias.
    
    Args:
        n_samples (int): Number of samples.
        bias_level (float): Degree of bias (0.0 to 1.0) against unprivileged group.
                            Higher value means more bias.
    
    Returns:
        pd.DataFrame: DataFrame with features, protected attribute, and target.
    """
    np.random.seed(42)
    
    # Features
    experience = np.random.normal(5, 2, n_samples)
    education = np.random.choice([0, 1, 2], n_samples, p=[0.3, 0.5, 0.2]) # HS, Bachelor, Master
    
    # Protected Attribute (e.g., Gender: 1=Privileged, 0=Unprivileged)
    gender = np.random.choice([0, 1], n_samples, p=[0.5, 0.5])
    
    # Target (e.g., Hired: 1=Yes, 0=No)
    # Base probability based on qualifications
    prob = 0.3 + 0.05 * experience + 0.1 * education
    
    # Inject Bias: Lower probability for unprivileged group
    # bias_level reduces the probability of positive outcome for group 0
    bias_factor = np.where(gender == 0, 1 - bias_level * 0.5, 1.0) 
    
    prob = prob * bias_factor
    prob = np.clip(prob, 0, 1)
    
    hired = np.random.binomial(1, prob)
    
    df = pd.DataFrame({
        'experience': experience,
        'education': education,
        'gender': gender,
        'hired': hired
    })
    
    return df

def perturbation_test_data(df, protected_attribute, sensitive_value):
    """
    Creates a perturbed version of the dataset where the protected attribute is flipped.
    """
    df_perturbed = df.copy()
    # Flip the protected attribute
    df_perturbed[protected_attribute] = df_perturbed[protected_attribute].apply(
        lambda x: sensitive_value if x != sensitive_value else (1 - sensitive_value) # Assuming binary 0/1
    )
    return df_perturbed
