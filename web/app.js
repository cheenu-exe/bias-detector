// State
let isStreaming = false;
let streamInterval = null;

// Navigation
document.querySelectorAll('.nav-links li').forEach(item => {
    item.addEventListener('click', () => {
        document.querySelectorAll('.nav-links li').forEach(l => l.classList.remove('active'));
        document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));

        item.classList.add('active');
        const tabId = item.getAttribute('data-tab');
        document.getElementById(tabId).classList.add('active');

        if (tabId === 'report') loadReport();
    });
});

// File Upload Handler
document.getElementById('fileUpload').addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    console.log("Uploading file...", file.name);

    try {
        const auditRes = await fetch('/api/audit', {
            method: 'POST',
            body: formData
        });

        if (!auditRes.ok) throw new Error(await auditRes.text());

        const results = await auditRes.json();
        displayAuditResults(results);
        alert("File uploaded and audited successfully!");

    } catch (err) {
        console.error(err);
        alert("Upload failed: " + err.message);
    }
});

// Audit Functions
async function generateAndAudit() {
    console.log("Generating data...");

    // 1. Get synthetic data
    const genRes = await fetch('/api/generate_data?n_samples=500');
    const data = await genRes.json();

    // 2. Send to audit endpoint (simulate file upload behavior by converting to File)
    const blob = new Blob([JSON.stringify(data)], { type: 'application/json' });
    const formData = new FormData();
    formData.append('file', blob, 'synthetic_data.json');

    console.log("Auditing...");

    try {
        const auditRes = await fetch('/api/audit', {
            method: 'POST',
            body: formData
        });

        const results = await auditRes.json();
        displayAuditResults(results);

        // Switch to audit tab if not there
        document.querySelector('[data-tab="audit"]').click();

    } catch (e) {
        alert("Audit failed: " + e.message);
    }
}

function displayAuditResults(results) {
    document.getElementById('auditResults').classList.remove('hidden');

    // Disparate Impact
    const di = results.disparate_impact;
    const diVal = document.getElementById('di-val');
    const diBar = document.getElementById('di-bar');

    diVal.innerText = di ? di.toFixed(2) : 'N/A';

    // Visual bar logic (cap at 100% for display)
    if (di) {
        let pct = di * 100;
        if (pct > 100) pct = 100; // Simplified visual
        diBar.style.width = pct + '%';

        if (di < 0.8) {
            diBar.style.backgroundColor = '#ef4444'; // Red
            diVal.classList.add('text-danger');
        } else {
            diBar.style.backgroundColor = '#10b981'; // Green
            diVal.classList.remove('text-danger');
            diVal.classList.add('text-success');
        }
    }

    // SPD
    const spd = results.statistical_parity_difference;
    document.getElementById('spd-val').innerText = spd ? spd.toFixed(3) : 'N/A';

    // Perturbation
    const perturb = results.perturbation_test;
    if (perturb) {
        document.getElementById('flip-val').innerText = (perturb.flip_rate * 100).toFixed(1) + '%';
    }
}

// Screening Functions
function toggleStream() {
    const btn = document.getElementById('btn-start-stream');

    if (isStreaming) {
        isStreaming = false;
        clearInterval(streamInterval);
        btn.innerHTML = '<i class="fa-solid fa-play"></i> Start Live Data Stream';
        btn.classList.add('primary');
        btn.classList.remove('secondary');
    } else {
        isStreaming = true;
        btn.innerHTML = '<i class="fa-solid fa-stop"></i> Stop Stream';
        btn.classList.remove('primary');
        btn.classList.add('secondary');

        // Start streaming simulation
        streamInterval = setInterval(runBatchScreen, 2000); // Every 2 seconds
    }
}

async function runBatchScreen() {
    // 1. Generate small batch of biased data (simulating drift/bias)
    // We fetch from generate but pretend it's new incoming usage data
    // Random bias level to make it interesting
    const bias = Math.random() > 0.7 ? 0.9 : 0.5; // Occasional drift
    const genRes = await fetch(`/api/generate_data?n_samples=20`);
    let batch = await genRes.json();

    // Inject artificial drift in feature 'experience' occasionally
    if (Math.random() > 0.6) {
        batch = batch.map(row => ({ ...row, experience: row.experience + 3 }));
    }

    // 2. Send to screen
    const screenRes = await fetch('/api/screen', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ data: batch })
    });

    const result = await screenRes.json();
    updateScreenLog(batch.length, result);
}

function updateScreenLog(count, result) {
    const logList = document.getElementById('stream-log');
    const driftStatus = document.getElementById('drift-status');
    const driftDetails = document.getElementById('drift-details');

    const driftDetected = Object.values(result.drift).some(d => d.drift_detected);

    // Log Item
    const item = document.createElement('li');
    item.className = 'log-item';
    const time = new Date().toLocaleTimeString();

    if (driftDetected) {
        item.classList.add('drift');
        item.innerHTML = `<span><i class="fa-solid fa-triangle-exclamation"></i> ${time}</span> <span>Batch (${count}): <strong>Drift Detected</strong></span>`;

        driftStatus.className = 'drift-indicator danger';
        driftStatus.innerHTML = '<i class="fa-solid fa-triangle-exclamation"></i> Drift Detected';
        driftDetails.innerText = Object.keys(result.drift).filter(k => result.drift[k].drift_detected).join(', ') + ' showing significant shift.';
        driftStatus.style.color = '#ef4444';

    } else {
        item.innerHTML = `<span><i class="fa-solid fa-check"></i> ${time}</span> <span>Batch (${count}): Safe</span>`;

        driftStatus.className = 'drift-indicator safe';
        driftStatus.innerHTML = '<i class="fa-solid fa-check-circle"></i> Stable';
        driftDetails.innerText = 'Distribution matches baseline.';
        driftStatus.style.color = '#10b981';
    }

    logList.prepend(item);
    if (logList.children.length > 20) logList.lastChild.remove();
}

// Report
async function loadReport() {
    const res = await fetch('/api/report');
    const data = await res.json();
    document.getElementById('json-report').innerText = JSON.stringify(data, null, 4);
}
