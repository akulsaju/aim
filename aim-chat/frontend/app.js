/**
 * AIM Chat - Frontend Application
 * Handles chat UI and API communication
 */

const API_BASE = 'http://localhost:5000/api';

let currentModel = null;
let isModelLoaded = false;

/**
 * Initialize the application
 */
document.addEventListener('DOMContentLoaded', function() {
    checkServerStatus();
    loadAvailableModels();
    
    // Auto-resize textarea
    const textarea = document.getElementById('messageInput');
    textarea.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = Math.min(this.scrollHeight, 150) + 'px';
    });
});

/**
 * Check server status
 */
async function checkServerStatus() {
    try {
        const response = await fetch(`${API_BASE}/status`);
        const data = await response.json();
        
        // Update status indicator
        document.getElementById('statusIndicator').classList.add('online');
        document.getElementById('statusText').textContent = 'Online';
        
        // Update model info if loaded
        if (data.model_loaded && data.model_info) {
            updateModelInfo(data.model_info);
            isModelLoaded = true;
            showChatArea();
        }
    } catch (error) {
        document.getElementById('statusIndicator').classList.remove('online');
        document.getElementById('statusText').textContent = 'Offline';
        showToast('Server is offline. Please start the backend.', 3000);
    }
}

/**
 * Load available models from the server
 */
async function loadAvailableModels() {
    try {
        const response = await fetch(`${API_BASE}/models`);
        const data = await response.json();
        
        const modelsList = document.getElementById('modelsList');
        
        if (data.models && data.models.length > 0) {
            modelsList.innerHTML = data.models.map(model => `
                <div class="model-item" onclick="loadModel('${model.filename}')">
                    <div class="model-item-name">🤖 ${model.name}</div>
                    <div class="model-item-desc">${model.description}</div>
                    <div class="model-item-meta">
                        v${model.version} • ${model.knowledge_count} knowledge items
                    </div>
                </div>
            `).join('');
        } else {
            modelsList.innerHTML = '<p class="no-model-text">No models found</p>';
        }
    } catch (error) {
        document.getElementById('modelsList').innerHTML = '<p class="no-model-text">Could not load models</p>';
    }
}

/**
 * Load a specific model
 */
async function loadModel(filename) {
    showLoading();
    
    try {
        const response = await fetch(`${API_BASE}/load_model_by_name`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ filename })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            currentModel = data.model_info;
            isModelLoaded = true;
            updateModelInfo(data.model_info);
            showChatArea();
            clearMessages();
            showToast(`Model "${data.model_info.name}" loaded successfully!`, 2000);
        } else {
            showToast(`Error: ${data.error}`, 3000);
        }
    } catch (error) {
        showToast('Failed to load model', 3000);
    } finally {
        hideLoading();
    }
}

/**
 * Update model info display
 */
function updateModelInfo(modelInfo) {
    const modelInfoDiv = document.getElementById('modelInfo');
    modelInfoDiv.innerHTML = `
        <div class="model-info-loaded">
            <div class="info-row">
                <span class="info-label">Name:</span>
                <span class="info-value">${modelInfo.name}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Version:</span>
                <span class="info-value">${modelInfo.version}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Knowledge:</span>
                <span class="info-value">${modelInfo.knowledge_count} items</span>
            </div>
        </div>
    `;
}

/**
 * Show chat area and hide welcome screen
 */
function showChatArea() {
    document.getElementById('welcomeScreen').style.display = 'none';
    document.getElementById('chatArea').style.display = 'flex';
}

/**
 * Send a message
 */
async function sendMessage() {
    const input = document.getElementById('messageInput');
    const message = input.value.trim();
    
    if (!message) return;
    
    if (!isModelLoaded) {
        showToast('Please load a model first!', 2000);
        return;
    }
    
    // Clear input
    input.value = '';
    input.style.height = 'auto';
    
    // Add user message to chat
    addMessage('user', message);
    
    // Show loading
    showLoading();
    
    try {
        const response = await fetch(`${API_BASE}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Add AI response to chat
            addMessage('ai', data.response);
        } else {
            addMessage('ai', `Error: ${data.error}`);
        }
    } catch (error) {
        addMessage('ai', 'Sorry, I encountered an error. Please try again.');
    } finally {
        hideLoading();
    }
}

/**
 * Add a message to the chat
 */
function addMessage(role, content) {
    const messagesContainer = document.getElementById('messagesContainer');
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    
    const avatar = role === 'user' ? '👤' : '🤖';
    
    messageDiv.innerHTML = `
        <div class="message-avatar">${avatar}</div>
        <div class="message-content">${escapeHtml(content)}</div>
    `;
    
    messagesContainer.appendChild(messageDiv);
    
    // Smooth scroll to bottom
    setTimeout(() => {
        messagesContainer.scrollTo({
            top: messagesContainer.scrollHeight,
            behavior: 'smooth'
        });
    }, 100);
}

/**
 * Clear all messages
 */
function clearMessages() {
    document.getElementById('messagesContainer').innerHTML = '';
}

/**
 * Clear chat history
 */
async function clearChat() {
    if (!isModelLoaded) return;
    
    try {
        await fetch(`${API_BASE}/clear`, { method: 'POST' });
        clearMessages();
        showToast('Chat cleared', 1500);
    } catch (error) {
        showToast('Failed to clear chat', 2000);
    }
}

/**
 * Handle Enter key press in textarea
 */
function handleKeyPress(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
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
 * Show toast notification
 */
function showToast(message, duration = 2000) {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.classList.add('show');
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, duration);
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Show modal dialog
 */
function showModal(modalId) {
    document.getElementById(modalId).classList.add('active');
}

/**
 * Close modal dialog
 */
function closeModal(modalId) {
    document.getElementById(modalId).classList.remove('active');
}

/**
 * Show add knowledge modal
 */
function showAddDataModal() {
    if (!isModelLoaded) {
        showToast('Please load or create a model first!', 2500);
        return;
    }
    showModal('addDataModal');
}

/**
 * Show create model modal
 */
function showCreateModelModal() {
    showModal('createModelModal');
}

/**
 * Add new knowledge to current model
 */
async function addKnowledge() {
    const textarea = document.getElementById('newKnowledge');
    const text = textarea.value.trim();
    
    if (!text) {
        showToast('Please enter knowledge sentences!', 2000);
        return;
    }
    
    // Split by newlines first
    const lines = text.split('\n')
        .map(s => s.trim())
        .filter(s => s.length > 0);
    
    // Further split each line into sentences
    const sentences = [];
    for (const line of lines) {
        // Split on period, exclamation, or question mark followed by space or end
        const lineSentences = line.split(/([.!?])\s+/)
            .reduce((acc, part, i, arr) => {
                if (i % 2 === 0 && part) {
                    const punct = arr[i + 1] || '';
                    acc.push((part + punct).trim());
                }
                return acc;
            }, [])
            .filter(s => s.length > 10); // Only keep substantial sentences
        
        sentences.push(...lineSentences);
    }
    
    if (sentences.length === 0) {
        showToast('No valid sentences found!', 2000);
        return;
    }
    
    showLoading();
    
    try {
        const response = await fetch(`${API_BASE}/add_knowledge`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ knowledge: sentences })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showToast(`✅ Added ${sentences.length} knowledge sentences!`, 2500);
            textarea.value = '';
            closeModal('addDataModal');
            
            // Update model info
            if (currentModel) {
                currentModel.knowledge_count = data.total_knowledge;
                updateModelInfo(currentModel);
            }
        } else {
            showToast(`Error: ${data.error}`, 3000);
        }
    } catch (error) {
        showToast('Failed to add knowledge', 2500);
    } finally {
        hideLoading();
    }
}

/**
 * Create a new model
 */
async function createModel() {
    const name = document.getElementById('newModelName').value.trim();
    const version = document.getElementById('newModelVersion').value.trim() || '1.0';
    const description = document.getElementById('newModelDesc').value.trim();
    const knowledgeText = document.getElementById('newModelKnowledge').value.trim();
    
    if (!name) {
        showToast('Model name is required!', 2000);
        return;
    }
    
    if (!knowledgeText) {
        showToast('Knowledge sentences are required!', 2000);
        return;
    }
    
    // Split knowledge into sentences
    const knowledge = knowledgeText.split('\n')
        .map(s => s.trim())
        .filter(s => s.length > 0);
    
    if (knowledge.length < 3) {
        showToast('Please add at least 3 knowledge sentences!', 2500);
        return;
    }
    
    showLoading();
    
    try {
        const response = await fetch(`${API_BASE}/create_model`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name,
                version,
                description: description || `Custom knowledge model: ${name}`,
                knowledge
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            currentModel = data.model_info;
            isModelLoaded = true;
            updateModelInfo(data.model_info);
            showChatArea();
            clearMessages();
            
            showToast(`✅ Model "${name}" created and loaded!`, 2500);
            
            // Clear form
            document.getElementById('newModelName').value = '';
            document.getElementById('newModelVersion').value = '1.0';
            document.getElementById('newModelDesc').value = '';
            document.getElementById('newModelKnowledge').value = '';
            
            closeModal('createModelModal');
        } else {
            showToast(`Error: ${data.error}`, 3000);
        }
    } catch (error) {
        showToast('Failed to create model', 2500);
    } finally {
        hideLoading();
    }
}

/**
 * Create and save model to file
 */
async function createAndSaveModel() {
    const name = document.getElementById('newModelName').value.trim();
    const version = document.getElementById('newModelVersion').value.trim() || '1.0';
    const description = document.getElementById('newModelDesc').value.trim();
    const knowledgeText = document.getElementById('newModelKnowledge').value.trim();
    
    if (!name) {
        showToast('Model name is required!', 2000);
        return;
    }
    
    if (!knowledgeText) {
        showToast('Knowledge sentences are required!', 2000);
        return;
    }
    
    const knowledge = knowledgeText.split('\n')
        .map(s => s.trim())
        .filter(s => s.length > 0);
    
    if (knowledge.length < 3) {
        showToast('Please add at least 3 knowledge sentences!', 2500);
        return;
    }
    
    showLoading();
    
    try {
        // First create the model
        const createResponse = await fetch(`${API_BASE}/create_model`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name,
                version,
                description: description || `Custom knowledge model: ${name}`,
                knowledge
            })
        });
        
        const createData = await createResponse.json();
        
        if (!createResponse.ok) {
            showToast(`Error: ${createData.error}`, 3000);
            hideLoading();
            return;
        }
        
        // Then save it
        const saveResponse = await fetch(`${API_BASE}/save_model`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        
        const saveData = await saveResponse.json();
        
        if (saveResponse.ok) {
            currentModel = createData.model_info;
            isModelLoaded = true;
            updateModelInfo(createData.model_info);
            showChatArea();
            clearMessages();
            
            showToast(`✅ Model saved as ${saveData.filename}!`, 3000);
            
            // Clear form and reload models list
            document.getElementById('newModelName').value = '';
            document.getElementById('newModelVersion').value = '1.0';
            document.getElementById('newModelDesc').value = '';
            document.getElementById('newModelKnowledge').value = '';
            
            closeModal('createModelModal');
            loadAvailableModels();
        } else {
            showToast(`Created but failed to save: ${saveData.error}`, 3000);
        }
    } catch (error) {
        showToast('Failed to create and save model', 2500);
    } finally {
        hideLoading();
    }
}

// Refresh status every 10 seconds
setInterval(checkServerStatus, 10000);
