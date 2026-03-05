/**
 * AIM Studio - Frontend JavaScript
 * Handles all user interactions and API communication
 */

// API base URL
const API_BASE = 'http://localhost:5000/api';

// Store loaded model data
let loadedModelData = null;

/**
 * Initialize the application when page loads
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('AIM Studio initialized');
    
    // Check server status
    checkStatus();
    
    // Load available models
    loadAvailableModels();
});

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
 * Display status message
 */
function showStatus(elementId, message, type = 'info') {
    const element = document.getElementById(elementId);
    element.textContent = message;
    element.className = `status-message ${type}`;
    
    // Auto-hide after 5 seconds for success messages
    if (type === 'success') {
        setTimeout(() => {
            element.style.display = 'none';
        }, 5000);
    }
}

/**
 * Update the top status bar
 */
function updateStatusBar(text, info = '') {
    document.getElementById('statusText').textContent = text;
    document.getElementById('modelInfo').textContent = info;
}

/**
 * Check server and model status
 */
async function checkStatus() {
    try {
        const response = await fetch(`${API_BASE}/status`);
        const data = await response.json();
        
        if (data.model_loaded) {
            updateStatusBar(
                '✅ Model Loaded',
                `Order: ${data.order} | Vocab: ${data.vocabulary_size} words | Transitions: ${data.transitions_count}`
            );
        } else {
            updateStatusBar('⚠️ No model loaded', 'Train or load a model to get started');
        }
    } catch (error) {
        console.error('Status check failed:', error);
        updateStatusBar('❌ Server not connected', 'Make sure the backend is running');
    }
}

/**
 * Train a new model
 */
async function trainModel() {
    const text = document.getElementById('trainingText').value.trim();
    const order = parseInt(document.getElementById('modelOrder').value);
    
    // Validate input
    if (!text) {
        showStatus('trainStatus', 'Please enter training text', 'error');
        return;
    }
    
    if (text.split(/\s+/).length < 50) {
        showStatus('trainStatus', 'Please provide more training text (at least 50 words)', 'error');
        return;
    }
    
    showLoading();
    
    try {
        const response = await fetch(`${API_BASE}/train`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                text: text,
                order: order
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showStatus('trainStatus', 
                `✅ ${data.message}! Vocabulary: ${data.stats.vocabulary_size} words, Transitions: ${data.stats.transitions_count}`,
                'success'
            );
            
            // Update status bar
            checkStatus();
        } else {
            showStatus('trainStatus', `❌ ${data.error}`, 'error');
        }
    } catch (error) {
        console.error('Training failed:', error);
        showStatus('trainStatus', '❌ Failed to connect to server. Is it running?', 'error');
    } finally {
        hideLoading();
    }
}

/**
 * Generate text from the model
 */
async function generateText() {
    const prompt = document.getElementById('promptText').value.trim();
    const maxLength = parseInt(document.getElementById('maxLength').value);
    
    // Validate max length
    if (maxLength < 10 || maxLength > 500) {
        showStatus('generateStatus', 'Max length must be between 10 and 500', 'error');
        return;
    }
    
    showLoading();
    
    try {
        const response = await fetch(`${API_BASE}/generate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                prompt: prompt || null,
                max_length: maxLength,
                temperature: 1.0
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Display generated text
            document.getElementById('generatedText').textContent = data.text;
            
            showStatus('generateStatus', 
                `✅ Generated ${data.length} words successfully!`,
                'success'
            );
        } else {
            showStatus('generateStatus', `❌ ${data.error}`, 'error');
        }
    } catch (error) {
        console.error('Generation failed:', error);
        showStatus('generateStatus', '❌ Failed to connect to server', 'error');
    } finally {
        hideLoading();
    }
}

/**
 * Export the current model as .aim file
 */
async function exportModel() {
    const modelName = document.getElementById('modelName').value.trim();
    const author = document.getElementById('authorName').value.trim();
    const version = document.getElementById('modelVersion').value.trim();
    
    // Validate inputs
    if (!modelName) {
        showStatus('exportStatus', 'Please enter a model name', 'error');
        return;
    }
    
    showLoading();
    
    try {
        const response = await fetch(`${API_BASE}/export`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                model_name: modelName,
                author: author || 'Anonymous',
                version: version || '1.0'
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Download the .aim file
            downloadJSON(data.aim_data, data.filename);
            
            showStatus('exportStatus', 
                `✅ Model exported as ${data.filename}`,
                'success'
            );
            
            // Reload available models
            loadAvailableModels();
        } else {
            showStatus('exportStatus', `❌ ${data.error}`, 'error');
        }
    } catch (error) {
        console.error('Export failed:', error);
        showStatus('exportStatus', '❌ Failed to export model', 'error');
    } finally {
        hideLoading();
    }
}

/**
 * Handle file selection for loading models
 */
function handleFileSelect(event) {
    const file = event.target.files[0];
    
    if (file) {
        console.log('File selected:', file.name);
    }
}

/**
 * Load a .aim model file
 */
async function loadModel() {
    const fileInput = document.getElementById('modelFile');
    const file = fileInput.files[0];
    
    if (!file) {
        showStatus('loadStatus', 'Please select a .aim file', 'error');
        return;
    }
    
    showLoading();
    
    try {
        // Read the file as text
        const fileText = await file.text();
        const aimData = JSON.parse(fileText);
        
        // Send to backend
        const response = await fetch(`${API_BASE}/load_model`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                aim_data: aimData
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showStatus('loadStatus', 
                `✅ Loaded "${data.model_info.name}" by ${data.model_info.author}`,
                'success'
            );
            
            // Update status bar
            checkStatus();
            
            // Clear file input
            fileInput.value = '';
        } else {
            showStatus('loadStatus', `❌ ${data.error}`, 'error');
        }
    } catch (error) {
        console.error('Load failed:', error);
        showStatus('loadStatus', '❌ Failed to load model. Invalid .aim file?', 'error');
    } finally {
        hideLoading();
    }
}

/**
 * Load and display available models
 */
async function loadAvailableModels() {
    try {
        const response = await fetch(`${API_BASE}/models`);
        const data = await response.json();
        
        const modelsList = document.getElementById('modelsList');
        
        if (data.models && data.models.length > 0) {
            modelsList.innerHTML = '';
            
            data.models.forEach(model => {
                const modelItem = document.createElement('div');
                modelItem.className = 'model-item';
                modelItem.onclick = () => loadModelFromServer(model.filename);
                
                modelItem.innerHTML = `
                    <h4>${model.model_name}</h4>
                    <p><strong>Author:</strong> ${model.author} | <strong>Version:</strong> ${model.version}</p>
                    <p><strong>Algorithm:</strong> ${model.algorithm}</p>
                    <p class="text-muted"><small>Created: ${new Date(model.created_at).toLocaleString()}</small></p>
                `;
                
                modelsList.appendChild(modelItem);
            });
        } else {
            modelsList.innerHTML = '<p class="text-muted">No models found. Train and export a model to get started!</p>';
        }
    } catch (error) {
        console.error('Failed to load models:', error);
        document.getElementById('modelsList').innerHTML = 
            '<p class="text-muted">Could not connect to server</p>';
    }
}

/**
 * Load a model from the server's models directory
 */
async function loadModelFromServer(filename) {
    showLoading();
    
    try {
        // Download the model file
        const response = await fetch(`${API_BASE}/model/${filename}`);
        
        if (!response.ok) {
            throw new Error('Failed to download model');
        }
        
        const aimData = await response.json();
        
        // Load the model
        const loadResponse = await fetch(`${API_BASE}/load_model`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                aim_data: aimData
            })
        });
        
        const data = await loadResponse.json();
        
        if (loadResponse.ok) {
            showStatus('loadStatus', 
                `✅ Loaded "${data.model_info.name}" by ${data.model_info.author}`,
                'success'
            );
            
            // Update status bar
            checkStatus();
        } else {
            showStatus('loadStatus', `❌ ${data.error}`, 'error');
        }
    } catch (error) {
        console.error('Failed to load model:', error);
        showStatus('loadStatus', '❌ Failed to load model from server', 'error');
    } finally {
        hideLoading();
    }
}

/**
 * Download JSON data as a file
 */
function downloadJSON(data, filename) {
    const jsonStr = JSON.stringify(data, null, 2);
    const blob = new Blob([jsonStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

/**
 * Format file size for display
 */
function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}
