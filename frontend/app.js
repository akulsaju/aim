/**
 * AIM Studio v3 - Modern Frontend Application
 * Advanced text generation with Markov chains and model management
 */

const API_BASE = 'http://localhost:5000/api';
const API_V3_BASE = 'http://localhost:5000/api/v3';

let currentModel = null;
let generatedText = '';

/**
 * Initialize the application
 */
document.addEventListener('DOMContentLoaded', function() {
    initializeTabs();
    initializeEventListeners();
    checkServerStatus();
    loadAvailableModels();
    setupTemperatureDisplay();
});

/**
 * Initialize tab switching
 */
function initializeTabs() {
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            switchTab(item.dataset.tab);
        });
    });
}

/**
 * Switch to a tab
 */
function switchTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Deactivate all nav items
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });
    
    // Show selected tab
    document.getElementById(tabName).classList.add('active');
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
    
    // Load API info if info tab
    if (tabName === 'info') {
        loadAPIInfo();
    }
}

/**
 * Initialize event listeners
 */
function initializeEventListeners() {
    // Temperature range display
    const tempInput = document.getElementById('temperature');
    if (tempInput) {
        tempInput.addEventListener('input', (e) => {
            document.getElementById('tempValue').textContent = e.target.value;
        });
    }
    
    // File input display
    const fileInput = document.getElementById('modelFile');
    if (fileInput) {
        fileInput.addEventListener('change', (e) => {
            const fileName = e.target.files[0]?.name || 'Choose a file...';
            document.getElementById('fileName').textContent = fileName;
        });
    }
}

/**
 * Toggle engine-specific options
 */
function toggleEngineOptions() {
    const engineType = document.getElementById('engineType').value;
    document.getElementById('llmOptions').style.display = engineType === 'llm' ? 'block' : 'none';
    const markovOpts = document.getElementById('markovOptions');
    if (markovOpts) {
        markovOpts.style.display = engineType === 'markov' ? 'block' : 'none';
    }
}

/**
 * Toggle engine-specific options
 */
function toggleEngineOptions() {
    const engineType = document.getElementById('engineType').value;
    document.getElementById('llmOptions').style.display = engineType === 'llm' ? 'block' : 'none';
    document.getElementById('markovOptions').style.display = engineType === 'markov' ? 'block' : 'none';
}

/**
 * Setup temperature display
 */
function setupTemperatureDisplay() {
    const temp = document.getElementById('temperature');
    if (temp) {
        document.getElementById('tempValue').textContent = temp.value;
    }
}

/**
 * Check server connection and model status
 */
async function checkServerStatus() {
    try {
        const response = await fetch(`${API_BASE}/status`);
        const data = await response.json();
        
        const statusBadge = document.getElementById('statusBadge');
        statusBadge.classList.add('online');
        statusBadge.textContent = 'Online';
        
        // Update model card
        if (data.model_loaded) {
            currentModel = data;
            document.querySelector('.model-status').textContent = '✅ Model Ready';
            document.getElementById('modelOrder').textContent = data.order;
            document.getElementById('modelVocab').textContent = `${data.vocabulary_size}`;
            document.getElementById('modelDetails').style.display = 'block';
        } else {
            document.querySelector('.model-status').textContent = '⚠️ No Model';
            document.getElementById('modelDetails').style.display = 'none';
        }
    } catch (error) {
        const statusBadge = document.getElementById('statusBadge');
        statusBadge.textContent = 'Offline';
        showToast('Server not responding', 'error');
    }
}

/**
 * Train a new model
 */
async function trainModel() {
    const text = document.getElementById('trainingText').value.trim();
    const engineType = document.getElementById('engineType').value;
    const apiKey = document.getElementById('apiKey')?.value || null;
    const order = engineType === 'markov' ? parseInt(document.getElementById('modelOrder').value) : 2;
    
    if (!text) {
        showMessage('trainStatus', '❌ Please enter training text', 'error');
        return;
    }
    
    const wordCount = text.split(/\s+/).length;
    if (wordCount < 10) {
        showMessage('trainStatus', `❌ Need more text (${wordCount}/10 words minimum)`, 'error');
        return;
    }
    
    showLoading();
    
    try {
        const payload = { 
            text, 
            engine: engineType,
            order 
        };
        
        if (engineType === 'llm' && apiKey) {
            payload.api_key = apiKey;
        }
        
        const response = await fetch(`${API_BASE}/v3/train`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            const engineName = engineType === 'llm' ? '🤖 LLM' : engineType === 'markov' ? '📊 Markov' : '📈 N-gram';
            showMessage('trainStatus', 
                `✅ ${engineName} model configured successfully!`,
                'success'
            );
            checkServerStatus();
        } else {
            showMessage('trainStatus', `❌ ${data.error}`, 'error');
        }
    } catch (error) {
        // Fallback to old API
        try {
            const response = await fetch(`${API_BASE}/train`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text, order })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                showMessage('trainStatus', 
                    `✅ Model trained! ${data.stats.vocabulary_size} words`,
                    'success'
                );
                checkServerStatus();
            } else {
                showMessage('trainStatus', `❌ ${data.error}`, 'error');
            }
        } catch (err) {
            showMessage('trainStatus', '❌ Connection failed', 'error');
        }
    } finally {
        hideLoading();
    }
}

/**
 * Generate text
 */
async function generateText() {
    const prompt = document.getElementById('promptText').value.trim() || null;
    const maxLength = parseInt(document.getElementById('maxLength').value);
    const temperature = parseFloat(document.getElementById('temperature').value);
    
    if (!currentModel) {
        showMessage('generateStatus', '❌ No model trained yet', 'error');
        return;
    }
    
    if (maxLength < 10 || maxLength > 500) {
        showMessage('generateStatus', '❌ Words must be 10-500', 'error');
        return;
    }
    
    showLoading();
    
    try {
        const response = await fetch(`${API_BASE}/generate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt, max_length: maxLength, temperature })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            generatedText = data.text;
            document.getElementById('generatedText').textContent = data.text;
            document.getElementById('copyBtn').style.display = 'inline-flex';
            
            showMessage('generateStatus', 
                `✅ Generated ${data.length} words in ${data.time}ms`,
                'success'
            );
        } else {
            showMessage('generateStatus', `❌ ${data.error}`, 'error');
        }
    } catch (error) {
        showMessage('generateStatus', '❌ Generation failed', 'error');
    } finally {
        hideLoading();
    }
}

/**
 * Copy generated text
 */
function copyGenerated() {
    if (generatedText) {
        navigator.clipboard.writeText(generatedText).then(() => {
            showToast('✅ Copied to clipboard!', 'success');
        });
    }
}

/**
 * Export model
 */
async function exportModel() {
    const name = document.getElementById('modelName').value.trim();
    const author = document.getElementById('authorName').value.trim();
    const description = document.getElementById('modelDescription').value.trim();
    const version = document.getElementById('modelVersion').value.trim() || '1.0';
    
    if (!name) {
        showMessage('exportStatus', '❌ Enter a model name', 'error');
        return;
    }
    
    if (!currentModel) {
        showMessage('exportStatus', '❌ No model to export', 'error');
        return;
    }
    
    showLoading();
    
    try {
        const response = await fetch(`${API_BASE}/export`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                model_name: name,
                author: author || 'Anonymous',
                version,
                description
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            downloadJSON(data.aim_data, `${name}-v${version}.aim`);
            showMessage('exportStatus', `✅ Exported as ${data.filename}`, 'success');
            loadAvailableModels();
        } else {
            showMessage('exportStatus', `❌ ${data.error}`, 'error');
        }
    } catch (error) {
        showMessage('exportStatus', '❌ Export failed', 'error');
    } finally {
        hideLoading();
    }
}

/**
 * Load model from file
 */
async function loadModel() {
    const fileInput = document.getElementById('modelFile');
    const file = fileInput.files[0];
    
    if (!file) {
        showMessage('loadStatus', '❌ Select a .aim file', 'error');
        return;
    }
    
    showLoading();
    
    try {
        const fileText = await file.text();
        const aimData = JSON.parse(fileText);
        
        const response = await fetch(`${API_BASE}/load_model`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ aim_data: aimData })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage('loadStatus', 
                `✅ Loaded "${data.model_info.name}" by ${data.model_info.author}`,
                'success'
            );
            checkServerStatus();
            fileInput.value = '';
            document.getElementById('fileName').textContent = 'Choose a file...';
        } else {
            showMessage('loadStatus', `❌ ${data.error}`, 'error');
        }
    } catch (error) {
        showMessage('loadStatus', '❌ Invalid .aim file', 'error');
    } finally {
        hideLoading();
    }
}

/**
 * Load available models
 */
async function loadAvailableModels() {
    try {
        const response = await fetch(`${API_BASE}/models`);
        const data = await response.json();
        const modelsList = document.getElementById('modelsList');
        
        if (data.models && data.models.length > 0) {
            modelsList.innerHTML = data.models.map(model => `
                <div class="model-item" onclick="loadModelFromServer('${model.filename}')">
                    <div class="model-item-name">📦 ${model.model_name}</div>
                    <div class="model-item-info"><strong>Author:</strong> ${model.author}</div>
                    <div class="model-item-info"><strong>Version:</strong> ${model.version}</div>
                    <div class="model-item-info" style="font-size: 0.8rem; margin-top: 0.5rem;">
                        ${new Date(model.created_at).toLocaleDateString()}
                    </div>
                </div>
            `).join('');
        } else {
            modelsList.innerHTML = '<p class="text-muted">No models found. Train and export to create one!</p>';
        }
    } catch (error) {
        document.getElementById('modelsList').innerHTML = '<p class="text-muted">Could not load models</p>';
    }
}

/**
 * Load model from server
 */
async function loadModelFromServer(filename) {
    showLoading();
    
    try {
        const response = await fetch(`${API_BASE}/model/${filename}`);
        
        if (!response.ok) throw new Error('Download failed');
        
        const aimData = await response.json();
        const loadResponse = await fetch(`${API_BASE}/load_model`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ aim_data: aimData })
        });
        
        const data = await loadResponse.json();
        
        if (loadResponse.ok) {
            showToast(`✅ Loaded "${data.model_info.name}"`, 'success');
            checkServerStatus();
        } else {
            showToast(`❌ ${data.error}`, 'error');
        }
    } catch (error) {
        showToast('❌ Failed to load model', 'error');
    } finally {
        hideLoading();
    }
}

/**
 * Load and display API info
 */
async function loadAPIInfo() {
    const infoDiv = document.getElementById('apiInfo');
    
    try {
        const [engines, v3Engine] = await Promise.all([
            fetch(`${API_BASE}/v3/engines`).then(r => r.json()).catch(() => null),
            fetch(`${API_V3_BASE}/engines`).then(r => r.json()).catch(() => null)
        ]);
        
        let html = `
            <div style="margin: 1rem 0;">
                <h3 style="margin-bottom: 1rem; color: #6366f1;">Available Engines</h3>
                <div style="display: grid; gap: 1rem;">
        `;
        
        const engineList = v3Engine?.engines || engines?.engines || [];
        if (engineList.length > 0) {
            engineList.forEach(engine => {
                html += `
                    <div style="border: 1px solid #e2e8f0; border-radius: 0.5rem; padding: 1rem; background: #f8fafc;">
                        <h4 style="color: #1e293b;">${engine.name}</h4>
                        <p style="color: #64748b; margin: 0.5rem 0;">${engine.description}</p>
                        <small style="color: #94a3b8;">Type: ${engine.type}</small>
                    </div>
                `;
            });
        }
        
        html += `
                </div>
                <div style="margin-top: 2rem; padding: 1rem; background: #f0f9ff; border-left: 4px solid #3b82f6; border-radius: 0.5rem;">
                    <h4 style="color: #0c2d6b; margin: 0;">System Information</h4>
                    <p style="color: #0c2d6b; margin: 0.5rem 0; font-size: 0.9rem;">
                        <strong>Version:</strong> AIM v3.0.0<br>
                        <strong>Server:</strong> Flask + Markov Chains<br>
                        <strong>API Base:</strong> ${API_BASE}
                    </p>
                </div>
            </div>
        `;
        
        infoDiv.innerHTML = html;
    } catch (error) {
        infoDiv.innerHTML = '<p class="text-muted">Could not load API information</p>';
    }
}

/**
 * Show status message
 */
function showMessage(elementId, message, type = 'info') {
    const element = document.getElementById(elementId);
    element.textContent = message;
    element.className = `status-message show ${type}`;
    
    if (type === 'success') {
        setTimeout(() => {
            element.classList.remove('show');
        }, 4000);
    }
}

/**
 * Show toast notification
 */
function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    container.appendChild(toast);
    
    setTimeout(() => toast.remove(), 3000);
}

/**
 * Show loading overlay
 */
function showLoading() {
    document.getElementById('loadingOverlay').classList.add('active');
}

/**
 * Hide loading overlay
 */
function hideLoading() {
    document.getElementById('loadingOverlay').classList.remove('active');
}

/**
 * Download JSON
 */
function downloadJSON(data, filename) {
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// Refresh status every 5 seconds
setInterval(checkServerStatus, 5000);
