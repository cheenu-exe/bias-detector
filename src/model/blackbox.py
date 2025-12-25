import random

class MockHRModel:
    def __init__(self):
        pass

    def predict(self, data: dict):
        """
        Accepts a dictionary of attributes.
        Returns {'hiring_probability': float, 'decision': int}
        """
        # data: {'age': int, 'experience': int, 'education': int, 'gender': int}
        
        age = data.get('age', 30)
        experience = data.get('experience', 5)
        education = data.get('education', 1)
        gender = data.get('gender', 0) # 0=Male, 1=Female
        
        # Base score calculation
        # Education: BS=1 (10pts), MS=2 (20pts), PhD=3 (30pts)
        score = education * 10
        
        # Experience: 2pts per year
        score += experience * 2
        
        # --- BIAS SIMULATION ---
        # 1. Age Bias: Penalize if age > 50
        if age > 50:
            score -= 20
            
        # 2. Gender Bias: Penalize if Female (1)
        if gender == 1:
            score -= 10
        # -----------------------
        
        # Normalize score to probability roughly between 0 and 1
        # Max reasonable score: 30 (PhD) + 80 (40yr exp) = 110.
        # Min score: 10.
        # Add some randomness
        noise = random.uniform(-5, 5)
        final_score = score + noise
        
        # Sigmoid-ish scaling
        probability = min(max(final_score / 80.0, 0.0), 1.0)
        
        # Decision Threshold
        decision = 1 if probability > 0.5 else 0
        
        return {
            "hiring_probability": float(probability),
            "decision": int(decision)
        }

# Global instance
hr_model = MockHRModel()
