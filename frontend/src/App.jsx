import React, { useState } from 'react';

// Simple SVG Icons to avoid dependency issues
const AlertIcon = () => (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ color: '#ef4444' }}>
        <circle cx="12" cy="12" r="10"></circle>
        <line x1="12" y1="8" x2="12" y2="12"></line>
        <line x1="12" y1="16" x2="12.01" y2="16"></line>
    </svg>
);

const CheckIcon = () => (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ color: '#10b981' }}>
        <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
        <polyline points="22 4 12 14.01 9 11.01"></polyline>
    </svg>
);

function App() {
    const [formData, setFormData] = useState({
        age: 30,
        experience: 5,
        education: 1,
        gender: 0
    });

    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);
        setResult(null);

        try {
            // Assuming backend is at localhost:8000
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

            // Simulate a small delay for "Analysis" visual effect
            setTimeout(() => {
                setResult(data);
                setLoading(false);
            }, 800);

        } catch (err) {
            setError("Failed to connect to verification layer. Ensure backend is running on port 8000.");
            setLoading(false);
        }
    };

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: parseInt(e.target.value)
        });
    };

    return (
        <div className="container">
            <header style={{ textAlign: 'center', marginBottom: '3rem' }}>
                <h1 style={{ fontSize: '2.5rem', marginBottom: '0.5rem', background: 'linear-gradient(45deg, #3b82f6, #8b5cf6)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
                    Runtime Verification Layer
                </h1>
                <p style={{ color: 'var(--text-muted)' }}>Real-time AI Bias Auditing & Interception</p>
            </header>

            <div style={{ display: 'grid', gridTemplateColumns: 'minmax(300px, 1fr) 2fr', gap: '2rem', width: '100%', maxWidth: '1200px' }}>

                {/* Input Column */}
                <div className="glass-card">
                    <h2 style={{ marginTop: 0 }}>Candidate Profile</h2>
                    <form onSubmit={handleSubmit}>
                        <label>Age</label>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                            <input
                                type="range"
                                name="age"
                                min="18"
                                max="70"
                                value={formData.age}
                                onChange={handleChange}
                            />
                            <span>{formData.age}</span>
                        </div>

                        <label>Experience (Years)</label>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                            <input
                                type="range"
                                name="experience"
                                min="0"
                                max="40"
                                value={formData.experience}
                                onChange={handleChange}
                            />
                            <span>{formData.experience}</span>
                        </div>

                        <label>Education</label>
                        <select name="education" value={formData.education} onChange={handleChange}>
                            <option value={1}>Bachelor's</option>
                            <option value={2}>Master's</option>
                            <option value={3}>PhD</option>
                        </select>

                        <label>Gender</label>
                        <select name="gender" value={formData.gender} onChange={handleChange}>
                            <option value={0}>Male</option>
                            <option value={1}>Female</option>
                        </select>

                        <button type="submit" disabled={loading} style={{ width: '100%', marginTop: '1rem' }}>
                            {loading ? "Intercepting..." : "Process Application"}
                        </button>
                    </form>
                </div>

                {/* Results Column */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>

                    {error && (
                        <div className="glass-card" style={{ borderLeft: '4px solid var(--danger)' }}>
                            <strong style={{ color: 'var(--danger)' }}>Error:</strong> {error}
                        </div>
                    )}

                    {!result && !loading && !error && (
                        <div className="glass-card" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', minHeight: '300px', opacity: 0.5 }}>
                            <p>Awaiting Input Stream...</p>
                        </div>
                    )}

                    {loading && (
                        <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', minHeight: '300px' }}>
                            <div style={{ width: '40px', height: '40px', border: '4px solid var(--primary)', borderTopColor: 'transparent', borderRadius: '50%', animation: 'spin 1s linear infinite' }}></div>
                            <p style={{ marginTop: '1rem' }}>Generating Shadow Twins...</p>
                            <style>{`@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }`}</style>
                        </div>
                    )}

                    {result && (
                        <>
                            {/* Main Decision Card */}
                            <div className="glass-card" style={{
                                borderLeft: `4px solid ${result.model_decision.decision === 1 ? 'var(--success)' : 'var(--danger)'}`,
                                display: 'flex', justifyContent: 'space-between', alignItems: 'center'
                            }}>
                                <div>
                                    <h3 style={{ margin: 0, fontSize: '0.875rem', textTransform: 'uppercase', letterSpacing: '1px', color: 'var(--text-muted)' }}>Model Decision</h3>
                                    <div style={{ fontSize: '2rem', fontWeight: 'bold', color: result.model_decision.decision === 1 ? 'var(--success)' : 'var(--danger)' }}>
                                        {result.model_decision.decision === 1 ? 'HIRED' : 'REJECTED'}
                                    </div>
                                </div>
                                <div style={{ textAlign: 'right' }}>
                                    <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>Confidence</div>
                                    <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>{(result.model_decision.hiring_probability * 100).toFixed(1)}%</div>
                                </div>
                            </div>

                            {/* Audit Card */}
                            <div className="glass-card" style={{ position: 'relative', overflow: 'hidden' }}>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1.5rem' }}>
                                    {result.verification_report.bias_detected ? <AlertIcon /> : <CheckIcon />}
                                    <h3 style={{ margin: 0 }}>Runtime Audit Report</h3>
                                </div>

                                {result.verification_report.bias_detected ? (
                                    <div style={{ background: 'rgba(239, 68, 68, 0.1)', padding: '1rem', borderRadius: '8px', border: '1px solid rgba(239, 68, 68, 0.2)', marginBottom: '1.5rem' }}>
                                        <strong style={{ color: 'var(--danger)' }}>BIAS DETECTED</strong>
                                        <ul style={{ margin: '0.5rem 0', paddingLeft: '1.5rem' }}>
                                            {result.verification_report.reasons.map((r, i) => (
                                                <li key={i}>{r}</li>
                                            ))}
                                        </ul>
                                    </div>
                                ) : (
                                    <div style={{ background: 'rgba(16, 185, 129, 0.1)', padding: '1rem', borderRadius: '8px', border: '1px solid rgba(16, 185, 129, 0.2)', marginBottom: '1.5rem' }}>
                                        <strong style={{ color: 'var(--success)' }}>AUDIT PASSED</strong>
                                        <p style={{ margin: '0.5rem 0' }}>No significant deviations detected across sensitive attribute permutations.</p>
                                    </div>
                                )}

                                <h4>Shadow Twin Analysis</h4>
                                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
                                    {result.verification_report.twin_details.map((twin, idx) => (
                                        <div key={idx} style={{ background: 'rgba(255,255,255,0.05)', padding: '1rem', borderRadius: '8px' }}>
                                            <div style={{ fontSize: '0.75rem', textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>
                                                {twin.twin_data.twin_type}
                                            </div>
                                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                                <span style={{ fontWeight: 'bold', color: twin.prediction.decision === 1 ? 'var(--success)' : 'var(--danger)' }}>
                                                    {twin.prediction.decision === 1 ? 'HIRED' : 'REJECTED'}
                                                </span>
                                                <span style={{ fontSize: '0.875rem' }}>
                                                    {(twin.prediction.hiring_probability * 100).toFixed(0)}%
                                                </span>
                                            </div>
                                            <div style={{ fontSize: '0.8rem', marginTop: '0.5rem', color: 'var(--text-muted)' }}>
                                                {twin.twin_data.twin_type === 'gender_flip' ?
                                                    `Gender: ${twin.twin_data.gender === 1 ? 'Female' : 'Male'}` :
                                                    `Age: ${twin.twin_data.age}`
                                                }
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </>
                    )}

                </div>
            </div>
        </div>
    );
}

export default App;
