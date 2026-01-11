/**
 * Main JavaScript for Anomaly Detection API
 * Handles form submissions, file uploads, and result display
 */

// ============================================================================
// Utility Functions
// ============================================================================

function showElement(element) {
    if (element) {
        element.classList.add('show');
        element.classList.remove('hidden');
    }
}

function hideElement(element) {
    if (element) {
        element.classList.remove('show');
        element.classList.add('hidden');
    }
}

function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} show`;
    alertDiv.textContent = message;

    const container = document.querySelector('.form-container') || document.querySelector('.container');
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            alertDiv.remove();
        }, 5000);
    }
}

function formatModelName(modelName) {
    const names = {
        'isolation_forest': 'Isolation Forest',
        'ocsvm': 'One-Class SVM',
        'elliptic_envelope': 'Elliptic Envelope',
        'lof': 'Local Outlier Factor',
        'autoencoder': 'Autoencoder',
        'decision_tree': 'Decision Tree',
        'knn': 'K-Nearest Neighbors'
    };
    return names[modelName] || modelName.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());;
}

function formatScore(score) {
    if (score === null || score === undefined || isNaN(score)) {
        return 'N/A';
    }
    return parseFloat(score).toFixed(4);
}

function formatBytes(bytes) {
    if (bytes === 1024) return bytes + ' B';
    if (bytes < 1024*1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024*1024)).toFixed(1) + ' MB';
}

// ============================================================================
// Network Prediction
// ============================================================================

const TRAFFIC_PRESETS = {
    "normal_web_browsing": {
        "dur": 0.5, "proto": "tcp", "service": "http", "state": "FIN",
        "spkts": 12, "dpkts": 10, "sbytes": 800, "dbytes": 15000, "rate": 40.0
    },
    "file_transfer_ftp": {
        "dur": 2.5, "proto": "tcp", "service": "ftp", "state": "FIN",
        "spkts": 30, "dpkts": 25, "sbytes": 2000, "dbytes": 50000, "rate": 20.0
    },
    "dns_query": {
        "dur": 0.001, "proto": "udp", "service": "dns", "state": "CON",
        "spkts": 2, "dpkts": 2, "sbytes": 146, "dbytes": 178, "rate": 2000.0
    },
    "suspicious_scan": {
        "dur": 0.01, "proto": "tcp", "service": "-", "state": "INT",
        "spkts": 5, "dpkts": 0, "sbytes": 200, "dbytes": 0, "rate": 500.0
    }
};

// Initialize network form enhancements
function initNetworkForm() {
    const form = document.getElementById('networkForm');
    const presetSelect = document.getElementById('presetSelect');
    const loadPresetBtn = document.getElementById('loadPresetBtn');
    const toggleAdvanced = document.getElementById('toggleAdvanced');
    const resetBtn = document.getElementById('resetBtn');

    if (!form) return;

    // Load preset on button click
    if (loadPresetBtn && presetSelect) {
        loadPresetBtn.addEventListener('click', function() {
            const selectedPreset = presetSelect.value;
            if (selectedPreset && TRAFFIC_PRESETS[selectedPreset]) {
                loadPresetValues(selectedPreset);
                showAlert(`✅ Loaded "${getPresetDisplayName(selectedPreset)}" example`, 'success');
            } else {
                showAlert('Please select a traffic type first', 'warning');
            }
        });
    }

    // Toggle advanced fields
    if (toggleAdvanced) {
        toggleAdvanced.addEventListener('click', function () {
            const advancedFields = document.getElementById('advancedFields');
            const toggleText = document.getElementById('advancedToggleText');

            if (advancedFields.classList.contains('hidden')) {
                advancedFields.classList.remove('hidden');
                toggleText.textContent = '⚙️ Hide Advanced Options';
            } else {
                advancedFields.classList.add('hidden');
                toggleText.textContent = '⚙️ Show Advanced Options';
            }
        });
    }

    // Reset form
    if (resetBtn) {
        resetBtn.addEventListener('click', function() {
            form.reset();
            if (presetSelect) presetSelect.value = '';
            showAlert('Form reset', 'info');
        });
    }
    

    // Form submission
    form.addEventListener('submit', async function (e) {
        e.preventDefault();

        const formData = {
            dur: parseFloat(document.getElementById('dur').value) || 0,
            proto: document.getElementById('proto').value,
            service: document.getElementById('service').value,
            state: document.getElementById('state').value,
            spkts: parseInt(document.getElementById('spkts').value) || 0,
            dpkts: parseInt(document.getElementById('dpkts').value) || 0,
            sbytes: parseInt(document.getElementById('sbytes').value) || 0,
            dbytes: parseInt(document.getElementById('dbytes').value) || 0,
            rate: parseFloat(document.getElementById('rate').value) || 0
        };

        // Add preset indicator if selected
        if (presetSelect && presetSelect.value) {
            formData.preset = presetSelect.value;
        }
        
        await predictNetwork(formData);
    });
}

function loadPresetValues(presetName) {
    const preset = TRAFFIC_PRESETS[presetName];
    if (!preset) return;

    // Fill in form fields
    const fields = ['dur', 'proto', 'service', 'state', 'spkts', 'dpkts', 'sbytes', 'dbytes', 'rate'];
    fields.forEach(field => {
        const element = document.getElementById(field);
        if (element && preset[field] !== undefined) {
            element.value = preset[field];
            // Visual feedback
            element.classList.add('preset-filled');
            setTimeout(() => element.classList.remove('preset-filled'), 600);
        }
    });
}
function getPresetDisplayName(presetName) {
    const names = {
        "normal_web_browsing": "Normal Web Browsing",
        "file_transfer_ftp": "File Transfer (FTP)",
        "dns_query": "DNS Query",
        "suspicious_scan": "Suspicious Port Scan"
    };
    return names[presetName] || presetName;
}

async function predictNetwork(formData) {
    const loadingEl = document.getElementById('loading');
    const resultsEl = document.getElementById('results');
    
    try {
        showElement(loadingEl);
        hideElement(resultsEl);
        
        const response = await fetch('/api/predict/network', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            window.lastNetworkResult = result.data; // Store for download
            displayNetworkResults(result.data);
        } else {
            showAlert(result.error || 'Prediction failed', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showAlert('Network error: ' + error.message, 'error');
    } finally {
        hideElement(loadingEl);
    }
}

// Enhanced result display with better UX
function displayNetworkResults(data) {
    const resultsEl = document.getElementById('results');

    // Ensemble Result
    const ensemble = data.ensemble;
    const isNormal = ensemble.prediction === 'Normal';

    // Determine color based on prediction
    const resultColor = isNormal ? '#27ae60' : '#e74c3c';
    const resultIcon = isNormal ? '✅' : '⚠️';
    const resultText = isNormal ? 'Normal Traffic' : 'Potential Threat Detected';

    // Build HTML
    let html = `
        <div class="result-card ensemble-result" style="border-left: 5px solid ${resultColor};">
            <h3 style="color: ${resultColor};">${resultIcon} ${resultText}</h3>
            <div class="confidence-display">
                <div class="confidence-label">Confidence Level</div>
                <div class="confidence-bar-container">
                    <div class="confidence-bar" style="width: ${ensemble.confidence}%; background: ${resultColor};"></div>
                </div>
                <div class="confidence-value">${ensemble.confidence}%</div>
            </div>
            <div class="voting-summary">
                <p><strong>Model Agreement:</strong> ${ensemble.votes.Normal} models predict Normal, 
                   ${ensemble.votes.Attack || ensemble.confidence || 0} predict Attack</p>

                <p class="explanation-text">
                    ${getNetworkExplanation(isNormal, ensemble.confidence)}
                </p>
            </div>
        </div>
        
        <div class="models-breakdown">
            <h4>📊 Individual Model Results</h4>
            <div class="model-cards">
    `;

    // Individual model results
    if (data.models) {
        for (const [modelName, modelData] of Object.entries(data.models)) {
            const modelPrediction = modelData.prediction;
            const modelConfidence = modelData.confidence || 0;
            const modelIsNormal = modelPrediction === 'Normal';
            const modelColor = modelIsNormal ? '#27ae60' : '#e74c3c';

            html += `
                <div class="model-card">
                    <div class="model-header">
                        <span class="model-name">${formatModelName(modelName)}</span>
                        <span class="model-badge" style="background: ${modelColor};">${modelPrediction}</span>
                    </div>
                    <div class="model-confidence">
                        <small>Confidence: ${modelConfidence}%</small>
                        <div class="mini-confidence-bar">
                            <div style="width: ${modelConfidence}%; background: ${modelColor};"></div>
                        </div>
                    </div>
                    ${modelData.score ? `<div class="model-score">Score: ${formatScore(modelData.score)}</small>` : ''}
                </div>
            `;
        }
    }

    html += `
            </div>
        </div>
        
        <div class="action-buttons">
            <button onclick="downloadResults()" class="btn-secondary">💾 Download JSON</button>
            <button onclick="window.print()" class="btn-secondary">🖨️ Print Report</button>
        </div>
    `;

    resultsEl.innerHTML = html;
    showElement(resultsEl);
    // Smooth scroll to results
    resultsEl.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function getNetworkExplanation(isNormal, confidence) {
    if (isNormal) {
        if (confidence >= 80) {
            return "✓ This traffic pattern matches normal network behavior with high confidence. All security indicators are within expected ranges.";
        } else {
            return "✓ Traffic appears normal, though some models show slight deviations. This is likely benign behavior.";
        }
    } else {
        if (confidence >= 80) {
            return "⚠ This traffic shows strong anomalous characteristics that may indicate malicious activity. Immediate investigation recommended.";
        } else {
            return "⚠ Some suspicious patterns detected. Further monitoring and analysis advised to determine if this is a real threat.";
        }
    }
}

// Download results as JSON
// function downloadResults() {
//     const resultsEl = document.getElementById('results');
//     if (!resultsEl || !window.lastNetworkResult) {
//         showAlert('No results to download', 'warning');
//         return;
//     }

//     const dataStr = JSON.stringify(window.lastNetworkResult, null, 2);
//     const blob = new Blob([dataStr], { type: 'application/json' });
//     const url = URL.createObjectURL(blob);
//     const a = document.createElement('a');
//     a.href = url;
//     a.download = `network-analysis-${Date.now()}.json`;
//     document.body.appendChild(a);
//     a.click();
//     document.body.removeChild(a);
//     URL.revokeObjectURL(url);
// }

// // Store last result for download
// async function predictNetwork(formData) {
//     const loadingEl = document.getElementById('loading');
//     const resultsEl = document.getElementById('results');

//     try {
//         showElement(loadingEl);
//         hideElement(resultsEl);

//         const response = await fetch('/api/predict/network', {
//             method: 'POST',
//             headers: { 'Content-Type': 'application/json' },
//             body: JSON.stringify(formData)
//         });

//         const result = await response.json();

//         if (result.success) {
//             window.lastNetworkResult = result.data; // Store for download
//             displayNetworkResults(result.data);
//         } else {
//             showAlert(result.error || 'Prediction failed', 'error');
//         }
//     } catch (error) {
//         console.error('Error:', error);
//         showAlert('Network error: ' + error.message, 'error');
//     } finally {
//         hideElement(loadingEl);
//     }
// }




// ============================================================================
// Image Prediction (MVTec & X-ray)
// ============================================================================

// ============================================================================
// MVTEC Form Handling
// ============================================================================

function initMVTecForm() {
    const form = document.getElementById('mvtecForm');
    const fileInput = document.getElementById('imageFile');
    const dropZone = document.getElementById('dropZone');
    const preview = document.getElementById('imagePreview');
    const previewImg = document.getElementById('previewImg');
    const removeBtn = document.getElementById('removeImage');
    const showSamplesBtn = document.getElementById('showSamplesBtn');
    const modal = document.getElementById('sampleImagesModal');

    if (!form) return;

    // Drag & drop handling
    if (dropZone) {

        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, preventDefaults, false);
        });
        
        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }


        dropZone.addEventListener('dragover', () => {
            dropZone.classList.add('drag-over');
        });

        dropZone.addEventListener('dragleave', () => {
            dropZone.classList.remove('drag-over');
        });

        dropZone.addEventListener('drop', (e) => {
            dropZone.classList.remove('drag-over');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                fileInput.files = files;
                showImagePreview(files[0], 'mvtec');
                console.log("Drag and drop file:", files[0]);
            }
        });
    }

    // File selection handling
    if (fileInput) {
        fileInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                showImagePreview(file, 'mvtec');
                console.log("Selected file:", file);
            }
        });
    }

    // Remove image
    if (removeBtn) {
        removeBtn.addEventListener('click', () => {
            fileInput.value = '';
            if (preview) preview.classList.add('hidden');
            const filename = document.getElementById('fileName');
            if (filename) filename.textContent = '';
        });
    }

    // Sample images modal
    if (showSamplesBtn && modal) {
        showSamplesBtn.addEventListener('click', () => {
            modal.classList.remove('hidden');
        });

        const closeBtn = modal.querySelector('.close-modal');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                modal.classList.add('hidden');
            });
        }
        // Close on outside click
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.classList.add('hidden');
            }
        });
    }

    // Form submission
    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const file = fileInput.files[0];
        if (!file) {
            showAlert('Please select an image first', 'warning');
            return;
        }

        // Validate file size (5MB)
        if (file.size > 5 * 1024 * 1024) {
            showAlert('File too large. Maximum size is 5MB', 'error');
            return;
        }

        const formData = new FormData();
        formData.append('file', file);

        await predictMVTec(formData);
    });
}

function showImagePreview(file, type) {
    const previewId = type === 'xray' ? 'xrayPreview' : 'imagePreview';
    const imgId = type === 'xray' ? 'xrayPreviewImg' : 'previewImg';
    const fileNameId = type === 'xray' ? 'xrayFileName' : 'fileName';

    const preview = document.getElementById(previewId);
    const previewImg = document.getElementById(imgId);
    const fileName = document.getElementById(fileNameId);

    if (file && file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = (e) => {
            if (previewImg) previewImg.src = e.target.result;
            if (preview) preview.classList.remove('hidden');
            if (fileName) fileName.textContent = `Selected: ${file.name} (${formatBytes(file.size)})`;
        };
        reader.readAsDataURL(file);
    } else {
        showAlert('Please select a valid image file', 'error');
    }
}

async function predictMVTec(formData) {
    const loadingEl = document.getElementById('loading');
    const resultsEl = document.getElementById('results');

    try {
        showElement(loadingEl);
        hideElement(resultsEl);

        const response = await fetch('/api/predict/mvtec', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (result.success) {
            window.lastMVTecResult = result.data; // Store for download
            displayMVTecResults(result.data);
        } else {
            showAlert(result.error || 'Prediction failed', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showAlert('Network error: ' + error.message, 'error');
    } finally {
        hideElement(loadingEl);
    }
}

function displayMVTecResults(data) {
    const resultsEl = document.getElementById('results');
    const ensemble = data.ensemble;
    const imageInfo = data.image_info || {};

    const isNormal = ensemble.prediction === 'Normal';
    const resultColor = isNormal ? '#27ae60' : '#e74c3c';
    const resultIcon = isNormal ? '✅' : '⚠️';

    let html = `
        <div class="result-card ensemble-result" style="border-left: 5px solid ${resultColor};">

            ${imageInfo.category_icon ? `<div class="product-category">${imageInfo.category_icon} ${imageInfo.category.toUpperCase()}</div>` : ''}

            <h3 style="color: ${resultColor};">${resultIcon} Quality Inspection: ${ensemble.prediction}</h3>

            ${imageInfo.category_description ? `<p class="category-description">${imageInfo.category_description}</p>` : ''}
            
            <div class="confidence-display">
                <div class="confidence-label">Quality Inspection Confidence</div>
                <div class="confidence-bar-container">
                    <div class="confidence-bar" style="width: ${ensemble.confidence}%; background: ${resultColor};"></div>
                </div>
                <div class="confidence-value">${ensemble.confidence}%</div>
            </div>
            
            <div class="voting-summary">
                <p><strong>Model Agreement:</strong> ${ensemble.votes.Normal} models say Normal, 
                   ${ensemble.votes.Anomaly} detect Anomaly (out of ${ensemble.total_models} total)</p>
                <p class="explanation-text">
                    ${getMVTecExplanation(isNormal, ensemble.confidence)}
                </p>
            </div>
        </div>
        
        <div class="models-breakdown">
            <h4>🤖 Individual Model Results</h4>
            <div class="model-cards">
    `;

    // Individual models
    if (data.models) {
        for (const [modelName, modelData] of Object.entries(data.models)) {
            const modelColor = modelData.prediction === 'Normal' ? '#27ae60' : '#e74c3c';

            html += `
                <div class="model-card">
                    <div class="model-header">
                        <span class="model-name">${formatModelName(modelName)}</span>
                        <span class="model-badge" style="background: ${modelColor};">${modelData.prediction}</span>
                    </div>
                    <div class="model-confidence">
                        ${modelData.confidence ? `
                            <small>Confidence: ${modelData.confidence}%</small>
                            <div class="mini-confidence-bar">
                                <div style="width: ${modelData.confidence}%; background: ${modelColor};"></div>
                            </div>
                        ` : ''}
                        ${modelData.score ? `<small class="model-score">Anomaly Score: ${formatScore(modelData.score)}</small>` : ''}
                    </div>
                </div>
            `;
        }
    }

    html += `
            </div>
        </div>
        
        <div class="action-buttons">
            <button onclick="downloadResults('mvtec')" class="btn-secondary">💾 Download Report</button>
        </div>
    `;
    
    resultsEl.innerHTML = html;
    showElement(resultsEl);
    resultsEl.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function getMVTecExplanation(isNormal, confidence) {
    if (isNormal) {
        return "✓ This product passes quality inspection. No manufacturing defects or anomalies detected by our AI models.";
    } else {
        if (confidence >= 75) {
            return "⚠ Potential defect detected with high confidence. Manual inspection strongly recommended before shipping.";
        } else {
            return "⚠ Possible quality issue detected. Additional verification recommended to confirm defect status.";
        }
    }
}

// ============================================================================
// X-RAY Form Handling
// ============================================================================

function initXrayForm() {
    const form = document.getElementById('xrayForm');
    const fileInput = document.getElementById('xrayFile');
    const dropZone = document.getElementById('xrayDropZone');
    const preview = document.getElementById('xrayPreview');
    const previewImg = document.getElementById('xrayPreviewImg');
    const removeBtn = document.getElementById('removeXray');

    if (!form) return;

    // Similar drag & drop as MVTec
    if (dropZone) {
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
            }, false);
        });
        
        dropZone.addEventListener('dragover', () => {
            dropZone.classList.add('drag-over');
        });
        
        dropZone.addEventListener('dragleave', () => {
            dropZone.classList.remove('drag-over');
        });
        
        dropZone.addEventListener('drop', (e) => {
            dropZone.classList.remove('drag-over');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                fileInput.files = files;
                showImagePreview(files[0], 'xray');
            }
        });
    }

    if (fileInput) {
        fileInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                showImagePreview(file, 'xray');
                console.log("Selected file:", file);
            }
        });
    }

    if (removeBtn) {
        removeBtn.addEventListener('click', () => {
            fileInput.value = '';
            if (preview) preview.classList.add('hidden');
            const fileName = document.getElementById('xrayFileName');
            if (fileName) fileName.textContent = '';
        });
    }

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const file = fileInput.files[0];
        if (!file) {
            showAlert('Please select an X-ray image first', 'warning');
            return;
        }

        // Validate file size (10MB)
        if (file.size > 10 * 1024 * 1024) {
            showAlert('File too large. Maximum size is 10MB', 'error');
            return;
        }

        const formData = new FormData();
        formData.append('file', file);

        const analysisType = document.querySelector('input[name="analysisType"]:checked');
        if (analysisType) {
            formData.append('analysis_type', analysisType.value);
        }

        await predictXray(formData);
    });
}

async function predictXray(formData) {
    const loadingEl = document.getElementById('loading');
    const resultsEl = document.getElementById('results');

    try {
        showElement(loadingEl);
        hideElement(resultsEl);

        const response = await fetch('/api/predict/xray', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (result.success) {
            window.lastXrayResult = result.data; // Store for download
            displayXrayResults(result.data);
        } else {
            showAlert(result.error || 'Prediction failed', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showAlert('Network error: ' + error.message, 'error');
    } finally {
        hideElement(loadingEl);
    }
}

function displayXrayResults(data) {
    const resultsEl = document.getElementById('results');
    const ensemble = data.ensemble;
    const unsupervised = data.unsupervised_models || {};
    const supervised = data.supervised_models || {};

    const isNormal = ensemble.prediction === 'Normal';
    const resultColor = isNormal ? '#27ae60' : '#e74c3c';
    const resultIcon = isNormal ? '✅' : '⚠️';

    let html = `
        <div class="medical-warning">
            ⚕️ <strong>Medical Disclaimer:</strong> ${data.medical_disclaimer || 'This is for research purposes only. Always consult qualified healthcare professionals.'}
        </div>
        
        <div class="result-card ensemble-result" style="border-left: 5px solid ${resultColor};">
            <h3 style="color: ${resultColor};">${resultIcon} Analysis Result: ${ensemble.prediction}</h3>
            
            <div class="confidence-display">
                <div class="confidence-label">Overall Confidence</div>
                <div class="confidence-bar-container">
                    <div class="confidence-bar" style="width: ${ensemble.confidence}%; background: ${resultColor};"></div>
                </div>
                <div class="confidence-value">${ensemble.confidence}%</div>
            </div>
            
            <div class="voting-summary">
                <p><strong>Consensus:</strong> ${ensemble.votes.Normal} models indicate Normal, 

                   ${ensemble.votes.Anomaly} detect Anomaly (${ensemble.total_models} models total)</p>

                ${ensemble.interpretation ? `<p class="explanation-text">${ensemble.interpretation}</p>` : ''}
            </div>
        </div>
    `;

    // Unsupervised models
    if (Object.keys(unsupervised).length > 0) {
        html += `
            <div class="models-breakdown">
                <h4>🔬 Unsupervised Anomaly Detection</h4>
                <p class="section-description">These models detect unusual patterns without knowing specific diseases</p>
                <div class="model-cards">
        `;

    for (const [modelName, modelData] of Object.entries(unsupervised)) {
        const modelColor = modelData.prediction === 'Normal' ? '#27ae60' : '#e74c3c';

        html += `
                <div class="model-card">
                    <div class="model-header">
                        <span class="model-name">${formatModelName(modelName)}</span>
                        <span class="model-badge" style="background: ${modelColor};">${modelData.prediction}</span>
                    </div>
                    <div class="model-confidence">
                        ${modelData.method ? `<small class="model-method">${modelData.method}</small>` : ''}
                        ${modelData.reconstruction_error !== undefined ? 
                            `<small>Reconstruction Error: ${formatScore(modelData.reconstruction_error)}</small>` : ''}
                        ${modelData.confidence ? `
                            <small>Confidence: ${modelData.confidence}%</small>
                            <div class="mini-confidence-bar">
                                <div style="width: ${modelData.confidence}%; background: ${modelColor};"></div>
                            </div>
                        ` : ''}
                    </div>
                </div>
            `;
        }

        html += `</div></div>`;

    }

    // Supervised models
    if (Object.keys(supervised).length > 0) {
        html += `
            <div class="models-breakdown">
                <h4>🏥 Supervised Disease Classification</h4>
                <p class="section-description">These models identify specific thoracic conditions</p>
                <div class="model-cards">
        `;

        for (const [modelName, modelData] of Object.entries(supervised)) {
            const diseaseInfo = modelData.diseaseInfo || {};
            const color = diseaseInfo.color || '#95a5a6';

            html += `
                <div class="model-card disease-card">
                    <div class="model-header">
                        <span class="model-name">${formatModelName(modelName)}</span>
                        <span class="model-badge" style="background: ${color};">
                            ${diseaseInfo.icon || ''} ${modelData.prediction}
                        <span>
                    </div>
                    ${diseaseInfo.common_name ? `<p class="disease-common-name">${diseaseInfo.common_name}</p>` : ''}
                    ${diseaseInfo.description ? `<p class="disease-description">${diseaseInfo.description}</p>` : ''}
                    ${modelData.confidence ? `
                        <div class="model-confidence">
                            <small>Confidence: ${modelData.confidence.toFixed(1)}%</small>
                            <div class="mini-confidence-bar">
                                <div style="width: ${modelData.confidence}%; background: ${color};"></div>
                            </div>
                        </div>
                    ` : ''}
                    ${diseaseInfo.recommendation ? `
                        <div class="disease-recommendation">
                            <strong>Recommendation:</strong> ${diseaseInfo.recommendation}
                        </div>
                    ` : ''}
                    ${modelData.probability ? `<small>Confidence: ${Math.max(...modelData.probability).toFixed(2)}%</small>` : ''}
                </div>
            `;
        }

        html += `</div></div>`;
    }

    html += `
        <div class="action-buttons">
            <button onclick="downloadResults('xray')" class="btn-secondary">💾 Download Report</button>
            <button onclick="window.print()" class="btn-secondary">🖨️ Print Report</button>
        </div>
    `;

    resultsEl.innerHTML = html;
    showElement(resultsEl);
    resultsEl.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// ============================================================================
// DOWNLOAD RESULTS
// ============================================================================

function downloadResults(type = 'network') {
    let data = null;
    let filename = '';

    if (type === 'network' && window.lastNetworkResult) {
        data = window.lastNetworkResult;
        filename = `network-analysis-${Date.now()}.json`;
    } else if (type === 'mvtec' && window.lastMVTecResult) {
        data = window.lastMVTecResult;
        filename = `mvtec-inspection-${Date.now()}.json`;
    } else if (type === 'xray' && window.lastXrayResult) {
        data = window.lastXrayResult;
        filename = `xray-analysis-${Date.now()}.json`;
    } else {
        showAlert('No results to download', 'warning');
        return;
    }

    const dataStr = JSON.stringify(data, null, 2);
    const blob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    showAlert('Report downloaded successfully', 'success');
}

// ============================================================================
// Initialize all forms on page load
// ============================================================================

document.addEventListener('DOMContentLoaded', function () {
    console.log('🚀 Anomaly Detection API - JavaScript Loaded');

    //Initialize based on which form is present
    initNetworkForm();
    initMVTecForm();
    initXrayForm();

    // Add smooth scrolling to all links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth'});
            }
        });
    });
});

// ============================================================================
// KEYBOARD SHORTCUTS
// ============================================================================

document.addEventListener('keydown', function(e) {
    // Ctrl+Shift+L to toggle advanced options
    if (e.ctrlKey && e.metaKey && e.key === 'Enter') {
        const forms = ['networkForm', 'mvtecForm', 'xrayForm'];
        for (const formId of forms) {
            const form = document.getElementById(formId);
            if (form && !form.classList.contains('hidden')) {
                form.dispatchEvent(new Event('submit'));
                break;
            }
        }
    }
});

console.log('✅ Anomaly Detection API - JavaScript Initialized');