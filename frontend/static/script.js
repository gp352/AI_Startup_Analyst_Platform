let uploadedFiles = [];
let apiUrl = '';
let isConnected = false;

// API Configuration
async function testConnection() {
    const urlInput = document.getElementById('apiUrlInput');
    const statusEl = document.getElementById('connectionStatus');
    const messageEl = document.getElementById('connectionMessage');
    
    apiUrl = urlInput.value.trim().replace(/\/+$/, ''); // Remove trailing slashes
    
    if (!apiUrl) {
        showMessage(messageEl, 'Please enter an API URL', 'error');
        return;
    }

    try {
        statusEl.textContent = 'Testing...';
        statusEl.className = 'status-indicator';
        
        const response = await fetch(`${apiUrl}/health`);

        if (response.ok) {
            isConnected = true;
            statusEl.textContent = 'Connected';
            statusEl.className = 'status-indicator status-connected';
            showMessage(messageEl, `✅ Connected successfully! Service is healthy.`, 'success');
            updateAnalyzeButton();
        } else {
            throw new Error(`HTTP ${response.status}`);
        }
    } catch (error) {
        isConnected = false;
        statusEl.textContent = 'Disconnected';
        statusEl.className = 'status-indicator status-disconnected';
        showMessage(messageEl, `❌ Connection failed: ${error.message}`, 'error');
    }
}

function showMessage(element, message, type) {
    element.innerHTML = `<div class="${type}-message">${message}</div>`;
    setTimeout(() => {
        element.innerHTML = '';
    }, 5000);
}

// File upload functionality
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const fileList = document.getElementById('fileList');
const analyzeBtn = document.getElementById('analyzeBtn');

uploadArea.addEventListener('click', () => fileInput.click());
uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('drag-over');
});
uploadArea.addEventListener('dragleave', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('drag-over');
});
uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('drag-over');
    const files = Array.from(e.dataTransfer.files);
    addFiles(files);
});
fileInput.addEventListener('change', (e) => {
    const files = Array.from(e.target.files);
    addFiles(files);
});

function addFiles(files) {
    files.forEach(file => {
        if (!uploadedFiles.find(f => f.name === file.name)) {
            uploadedFiles.push(file);
        }
    });
    updateFileList();
    updateAnalyzeButton();
}

function removeFile(fileName) {
    uploadedFiles = uploadedFiles.filter(file => file.name !== fileName);
    updateFileList();
    updateAnalyzeButton();
}

function updateFileList() {
    fileList.innerHTML = '';
    uploadedFiles.forEach(file => {
        const fileItem = document.createElement('div');
        fileItem.className = 'file-item';
        fileItem.innerHTML = `
            <div>
                <div class="file-name">${file.name}</div>
                <div class="file-size">${(file.size / 1024).toFixed(1)} KB</div>
            </div>
            <button class="remove-file" onclick="removeFile('${file.name}')">Remove</button>
        `;
        fileList.appendChild(fileItem);
    });
}

function updateAnalyzeButton() {
    analyzeBtn.disabled = uploadedFiles.length === 0 || !isConnected;
}

// Analysis functionality
analyzeBtn.addEventListener('click', performAnalysis);

async function performAnalysis() {
    if (!isConnected) {
        alert('Please connect to the API first');
        return;
    }

    const progressEl = document.getElementById('progressUpdates');
    
    document.getElementById('loading').style.display = 'block';
    document.getElementById('analysisResults').style.display = 'none';
    document.getElementById('results').style.display = 'none';
    
    progressEl.innerHTML = '';

    try {
        updateProgress(progressEl, '🔄 Uploading documents...');
        
        const formData = new FormData();
        uploadedFiles.forEach(file => formData.append('file', file));

        const sector = document.getElementById('sectorSelect').value;
        const stage = document.getElementById('stageSelect').value;
        if (sector) formData.append('sector', sector);
        if (stage) formData.append('stage', stage);

        updateProgress(progressEl, '🤖 Processing with Google Cloud AI...');
        
        const response = await fetch(`${apiUrl}/api/analyze`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(`Analysis failed: ${errorData.error || response.statusText}`);
        }

        const analysisResult = await response.json();
        updateProgress(progressEl, '✅ Analysis complete! Displaying results...');
        
        setTimeout(() => {
            displayResults(analysisResult);
            document.getElementById('loading').style.display = 'none';
            document.getElementById('results').style.display = 'block';
        }, 1000);

    } catch (error) {
        console.error('Analysis error:', error);
        document.getElementById('loading').style.display = 'none';
        document.getElementById('analysisResults').style.display = 'block';
        document.getElementById('analysisResults').innerHTML = `
            <div class="error-message">
                <strong>Analysis Failed</strong><br>${error.message}
            </div>
        `;
    }
}

function updateProgress(progressEl, message) {
    const progressItem = document.createElement('div');
    progressItem.style.cssText = 'padding: 5px 0; color: #4a5568; font-size: 0.9em;';
    progressItem.innerHTML = message;
    progressEl.appendChild(progressItem);
    progressEl.scrollTop = progressEl.scrollHeight;
}

function displayResults(result) {
    const resultsContainer = document.getElementById('results');
    
    if (result.error) {
        resultsContainer.innerHTML = `<div class="error-message"><strong>API Error:</strong> ${result.error}</div>`;
        return;
    }
    
    const analysis = result.document_analysis?.startup_analysis || {};
    const investment = result.investment_score || {};
    const risks = result.risk_assessment || {};
    const benchmarks = result.benchmarks || {};

    const overallScore = investment.overall_score || 0;
    const companyName = analysis.company_name || 'Analyzed Startup';

    resultsContainer.innerHTML = `
        <div class="metric-card">
            <div class="metric-title">AI Investment Score</div>
            <div class="metric-value ${getScoreClass(overallScore)}">${overallScore}/100</div>
            <div class="metric-description">
                <strong>${companyName}</strong> • ${result.sector} • ${result.funding_stage}
            </div>
        </div>
        
        <div class="metric-card">
            <div class="metric-title">🚨 AI Risk Assessment</div>
            <div><strong>Overall Risk:</strong> <span class="risk-${(risks.risk_level || 'medium').toLowerCase()}">${risks.risk_level} (${risks.overall_risk_score}/10)</span></div>
            ${(risks.risk_factors || []).map(r => `<div><strong>${r.type}:</strong> ${r.concerns.join(', ')}</div>`).join('')}
        </div>

        <div class="recommendation-box">
            <div class="recommendation-title">🎯 AI Investment Recommendation</div>
            <div style="font-size: 1.4em; margin-bottom: 10px;">
                <strong>${investment.recommendation?.action}</strong>
                <span style="font-size: 0.8em; opacity: 0.8;">(${investment.recommendation?.confidence} Confidence)</span>
            </div>
            <div>${investment.recommendation?.reasoning}</div>
        </div>
    `;
}

function getScoreClass(score) {
    if (score >= 80) return 'score-excellent';
    if (score >= 65) return 'score-good';
    if (score >= 50) return 'score-average';
    return 'score-poor';
}

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    const apiUrlInput = document.getElementById('apiUrlInput');
    if (apiUrlInput.value.trim()) {
        setTimeout(testConnection, 500);
    }
});