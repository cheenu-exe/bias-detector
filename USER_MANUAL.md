# BiasGuard - User Manual

Welcome to **BiasGuard**, your expert AI Auditor for detecting and mitigating algorithmic bias. This tool helps you analyze datasets and model outputs to ensure fairness across protected attributes (like gender, race, age).

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.8+
- Modern Web Browser (Chrome, Firefox, Safari)

### 2. Installation
The tool comes pre-installed in your environment. If you need to restart it:

```bash
# Open a terminal in the project folder
cd "bias detector tool"

# Activate the virtual environment
source venv/bin/activate

# Install dependencies (if not done)
pip install -r requirements.txt

# Start the Dashboard
uvicorn src.api:app --reload
```
You will see a message saying `Application startup complete`.

### 3. Accessing the Tool
Open your browser and navigate to:
👉 **http://localhost:8000**

---

## 🛠 Features & Usage

### 1. Historical Bias Audit
Use this module to analyze existing datasets or past model predictions.

- **Upload Data**: Click **"Upload File"** to upload a CSV or JSON file containing your dataset.
    - *Required columns*: A protected attribute (e.g., `gender`, `race`), features (e.g., `experience`, `education`), and a prediction/label column.
- **Generate Synthetic Data**: Click **"Generate Synthetic Data"** to create a sample dataset with known bias for testing purposes.
- **Visualizing Results**:
    - **Disparate Impact (DI)**: Measures the ratio of positive outcomes between groups.
        - *Safe Zone*: 0.8 to 1.25.
        - *Red Bar*: Indicates adverse impact (bias detected).
    - **Statistical Parity Difference**: Difference in acceptance rates. Ideally 0.
    - **Perturbation Flip Rate**: Shows how often changing ONLY the protected attribute flips the model's decision. High flip rate = High Bias.

### 2. Real-Time Screening
Simulate a live production environment where data is screened before reaching the model.

- **Start Live Stream**: Click this button to simulate incoming data traffic.
- **Drift Detection**: The logs will show "Safe" or "Drift Detected".
    - *Drift* means the incoming data looks significantly different from the training data, which could lead to unreliable or biased predictions.
    - *Alerts*: High-risk batches are flagged with a red warning triangle.

### 3. Bias Scorecard
- Click the **Scorecard** tab to view the full JSON report.
- This report aggregates findings from both the historical audit and real-time screening.
- You can copy this JSON for compliance reporting or integration with other tools.

---

## ❓ FAQ

**Q: I uploaded a file but nothing happened?**
A: Ensure your file is a valid CSV/JSON. If the tool can't parse it, it might fail silently in the UI log. Check the browser console (F12) for detailed errors.

**Q: What does a Disparate Impact of 0.0 mean?**
A: This is severe! It means the unprivileged group received ZERO positive outcomes compared to the privileged group.

**Q: How do I stop the server?**
A: Go to your terminal and press `Ctrl+C`.

---

**Support**: Contact the AI Ethics Team for deep-dive analysis of any alerts found by BiasGuard.
