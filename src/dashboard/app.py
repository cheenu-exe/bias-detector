import streamlit as st
import sys
import os

# Add project root to path to allow imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.model.blackbox import hr_model
from src.interceptor.twins import ShadowTwinGenerator
from src.interceptor.detector import BiasDetector

# Setup
st.set_page_config(page_title="Runtime Verification Layer", layout="wide")
twin_gen = ShadowTwinGenerator()
bias_detector = BiasDetector()

st.title("🛡️ Runtime Verification Layer")
st.markdown("### Intercepting HR Decisions in Real-Time")

col1, col2 = st.columns([1, 2])

with col1:
    st.header("Candidate Profile")
    with st.form("candidate_form"):
        age = st.slider("Age", 18, 70, 30)
        experience = st.slider("Years of Experience", 0, 40, 5)
        education = st.selectbox("Education Level", [1, 2, 3], format_func=lambda x: {1: "Bachelor's", 2: "Master's", 3: "PhD"}[x])
        gender_input = st.selectbox("Gender", ["Male", "Female"])
        gender = 0 if gender_input == "Male" else 1
        
        submitted = st.form_submit_button("Submit Application")

if submitted:
    input_data = {
        "age": age,
        "experience": experience,
        "education": education,
        "gender": gender
    }
    
    # --- The Interceptor Logic (Simulating the API) ---
    original_result = hr_model.predict(input_data)
    
    twins = twin_gen.generate_twins(input_data)
    twins_results = []
    for twin in twins:
        res = hr_model.predict(twin)
        twins_results.append({
            "twin_data": twin,
            "prediction": res
        })
        
    bias_report = bias_detector.check_bias(original_result, twins_results)
    # --------------------------------------------------

    with col2:
        st.header("Decision & Audit")
        
        # Display Decision
        decision_map = {1: "HIRED", 0: "REJECTED"}
        decision_color = "green" if original_result['decision'] == 1 else "red"
        st.markdown(f"#### Model Decision: :{decision_color}[{decision_map[original_result['decision']]}]")
        st.text(f"Confidence Score: {original_result['hiring_probability']:.2f}")
        
        st.divider()
        
        # Display Runtime Verification
        st.subheader("Runtime Interceptor Stream")
        
        if bias_report['bias_detected']:
            st.error("⚠️ POTENTIAL BIAS DETECTED")
            for reason in bias_report['reasons']:
                st.write(f"- {reason}")
        else:
            st.success("✅ No Bias Detected in Runtime Check")
            
        with st.expander("View Shadow Twins Analysis"):
            st.write("The system automatically generated counterfactuals (Shadow Twins) to probe the model.")
            
            for item in bias_report['twin_details']:
                t_data = item['twin_data']
                t_pred = item['prediction']
                t_type = t_data.get('twin_type', 'Twin')
                
                decision_str = "Hired" if t_pred['decision'] == 1 else "Rejected"
                
                # Highlight what changed
                diff_desc = ""
                if t_type == 'gender_flip':
                    diff_desc = f"Gender changed to {'Female' if t_data['gender']==1 else 'Male'}"
                elif 'age' in t_type:
                    diff_desc = f"Age changed to {t_data['age']}"
                
                st.markdown(f"**{t_type.upper()}**: {diff_desc} -> **{decision_str}** ({t_pred['hiring_probability']:.2f})")

st.markdown("---")
st.info("ℹ️ this tool is a demo of the interceptor layer. It operates parallel to the core model API.")
