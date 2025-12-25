document.addEventListener('DOMContentLoaded', () => {
    // State
    const formData = {
        age: 30,
        experience: 5,
        education: 1,
        gender: 0
    };

    // Elements
    const ageInput = document.getElementById('age');
    const ageDisplay = document.getElementById('ageDisplay');
    const expInput = document.getElementById('experience');
    const expDisplay = document.getElementById('expDisplay');
    const eduInput = document.getElementById('education');
    const genderInput = document.getElementById('gender');
    const form = document.getElementById('candidateForm');
    const submitBtn = document.getElementById('submitBtn');

    // UI Sections
    const initialState = document.getElementById('initialState');
    const loadingState = document.getElementById('loadingState');
    const errorState = document.getElementById('errorState');
    const resultState = document.getElementById('resultState');

    // Bind Inputs
    ageInput.addEventListener('input', (e) => {
        formData.age = parseInt(e.target.value);
        ageDisplay.textContent = formData.age;
    });

    expInput.addEventListener('input', (e) => {
        formData.experience = parseInt(e.target.value);
        expDisplay.textContent = formData.experience;
    });

    eduInput.addEventListener('change', (e) => {
        formData.education = parseInt(e.target.value);
    });

    genderInput.addEventListener('change', (e) => {
        formData.gender = parseInt(e.target.value);
    });

    // Submit Handler
    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        // Show Loading
        initialState.style.display = 'none';
        resultState.style.display = 'none';
        errorState.style.display = 'none';
        loadingState.style.display = 'flex';
        submitBtn.disabled = true;
        submitBtn.textContent = 'Intercepting...';

        try {
            const response = await fetch('http://localhost:8000/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData),
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const data = await response.json();

            // Simulate Delay
            setTimeout(() => {
                loadingState.style.display = 'none';
                renderResult(data);
                submitBtn.disabled = false;
                submitBtn.textContent = 'Process Application';
            }, 800);

        } catch (err) {
            loadingState.style.display = 'none';
            errorState.style.display = 'block';
            document.getElementById('errorMsg').textContent = "Failed to connect to verification layer. Ensure backend is running on port 8000.";
            submitBtn.disabled = false;
            submitBtn.textContent = 'Process Application';
        }
    });

    function renderResult(data) {
        resultState.style.display = 'flex';

        const original = data.model_decision;
        const report = data.verification_report;

        // Render Decision
        const decisionCard = document.getElementById('decisionCard');
        const decisionText = document.getElementById('decisionText');
        const confidenceScore = document.getElementById('confidenceScore');

        const isHired = original.decision === 1;
        const color = isHired ? 'var(--success)' : 'var(--danger)';
        const text = isHired ? 'HIRED' : 'REJECTED';

        decisionCard.style.borderLeft = `4px solid ${color}`;
        decisionText.textContent = text;
        decisionText.style.color = color;
        confidenceScore.textContent = (original.hiring_probability * 100).toFixed(1) + '%';

        // Render Bias
        const auditIcon = document.getElementById('auditIcon');
        const auditStatusBox = document.getElementById('auditStatusBox');

        if (report.bias_detected) {
            // Icon: Alert
            auditIcon.innerHTML = `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#ef4444" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>`;

            // Box
            auditStatusBox.style.background = 'rgba(239, 68, 68, 0.1)';
            auditStatusBox.style.border = '1px solid rgba(239, 68, 68, 0.2)';

            let html = `<strong style="color: var(--danger);">BIAS DETECTED</strong><ul style="margin: 0.5rem 0; padding-left: 1.5rem;">`;
            report.reasons.forEach(r => html += `<li>${r}</li>`);
            html += `</ul>`;
            auditStatusBox.innerHTML = html;
        } else {
            // Icon: Check
            auditIcon.innerHTML = `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>`;

            // Box
            auditStatusBox.style.background = 'rgba(16, 185, 129, 0.1)';
            auditStatusBox.style.border = '1px solid rgba(16, 185, 129, 0.2)';
            auditStatusBox.innerHTML = `<strong style="color: var(--success);">AUDIT PASSED</strong><p style="margin: 0.5rem 0;">No significant deviations detected across sensitive attribute permutations.</p>`;
        }

        // Render Twins
        const twinsGrid = document.getElementById('shadowTwinsGrid');
        twinsGrid.innerHTML = '';

        report.twin_details.forEach(twin => {
            const tData = twin.twin_data;
            const tPred = twin.prediction;
            const tHired = tPred.decision === 1;
            const tColor = tHired ? 'var(--success)' : 'var(--danger)';
            const tText = tHired ? 'HIRED' : 'REJECTED';

            let diffDesc = '';
            if (tData.twin_type === 'gender_flip') {
                diffDesc = `Gender: ${tData.gender === 1 ? 'Female' : 'Male'}`;
            } else {
                diffDesc = `Age: ${tData.age}`;
            }

            const card = document.createElement('div');
            card.style.background = 'rgba(255,255,255,0.05)';
            card.style.padding = '1rem';
            card.style.borderRadius = '8px';

            card.innerHTML = `
                <div style="font-size: 0.75rem; text-transform: uppercase; color: var(--text-muted); margin-bottom: 0.5rem;">
                    ${tData.twin_type}
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-weight: bold; color: ${tColor};">
                        ${tText}
                    </span>
                    <span style="font-size: 0.875rem;">
                        ${(tPred.hiring_probability * 100).toFixed(0)}%
                    </span>
                </div>
                <div style="font-size: 0.8rem; margin-top: 0.5rem; color: var(--text-muted);">
                    ${diffDesc}
                </div>
            `;
            twinsGrid.appendChild(card);
        });
    }
});
