/**
 * Willow Desktop v6.0.0 - Frontend Application Logic
 */

// Tauri API imports
const { invoke } = window.__TAURI__.tauri;

// Application State
const AppState = {
    isConnected: false,
    capabilities: {},
    models: [],
    settings: {
        defaultModel: '',
        defaultMaxTokens: 1000,
        defaultTopK: 3,
        theme: 'dark'
    }
};

// DOM Elements
const Elements = {
    // Status
    statusDot: document.getElementById('statusDot'),
    statusText: document.getElementById('statusText'),
    capabilitiesList: document.getElementById('capabilitiesList'),
    
    // Navigation
    navItems: document.querySelectorAll('.nav-item'),
    tabContents: document.querySelectorAll('.tab-content'),
    
    // Chat
    chatForm: document.getElementById('chatForm'),
    chatInput: document.getElementById('chatInput'),
    chatMessages: document.getElementById('chatMessages'),
    sendButton: document.getElementById('sendButton'),
    modelSelect: document.getElementById('modelSelect'),
    maxTokensInput: document.getElementById('maxTokensInput'),
    
    // RAG
    ragForm: document.getElementById('ragForm'),
    ragQuery: document.getElementById('ragQuery'),
    ragDocuments: document.getElementById('ragDocuments'),
    ragTopK: document.getElementById('ragTopK'),
    ragResults: document.getElementById('ragResults'),
    
    // Settings
    defaultModel: document.getElementById('defaultModel'),
    defaultMaxTokens: document.getElementById('defaultMaxTokens'),
    defaultTopK: document.getElementById('defaultTopK'),
    themeSelect: document.getElementById('themeSelect'),
    saveSettingsButton: document.getElementById('saveSettingsButton'),
    
    // Status Tab
    backendStatusValue: document.getElementById('backendStatusValue'),
    versionValue: document.getElementById('versionValue'),
    featuresGrid: document.getElementById('featuresGrid'),
    modelsList: document.getElementById('modelsList'),
    performanceStats: document.getElementById('performanceStats'),
    refreshStatusButton: document.getElementById('refreshStatusButton'),
    
    // Loading
    loadingOverlay: document.getElementById('loadingOverlay')
};

// Utility Functions
const Utils = {
    formatTime: (date = new Date()) => {
        return date.toLocaleTimeString();
    },
    
    showLoading: () => {
        Elements.loadingOverlay.classList.add('active');
    },
    
    hideLoading: () => {
        Elements.loadingOverlay.classList.remove('active');
    },
    
    updateStatus: (status, text) => {
        Elements.statusDot.className = `status-dot ${status}`;
        Elements.statusText.textContent = text;
    },
    
    showError: (message) => {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'message system';
        errorDiv.innerHTML = `
            <div class="message-content">❌ <strong>Error:</strong> ${message}</div>
            <div class="message-time">${Utils.formatTime()}</div>
        `;
        Elements.chatMessages.appendChild(errorDiv);
        Elements.chatMessages.scrollTop = Elements.chatMessages.scrollHeight;
    },
    
    saveSettings: () => {
        const settings = {
            defaultModel: Elements.defaultModel.value,
            defaultMaxTokens: parseInt(Elements.defaultMaxTokens.value),
            defaultTopK: parseInt(Elements.defaultTopK.value),
            theme: Elements.themeSelect.value
        };
        localStorage.setItem('willowSettings', JSON.stringify(settings));
        AppState.settings = settings;
        
        // Apply theme
        document.documentElement.setAttribute('data-theme', settings.theme);
        
        return settings;
    },
    
    loadSettings: () => {
        const saved = localStorage.getItem('willowSettings');
        if (saved) {
            const settings = JSON.parse(saved);
            AppState.settings = { ...AppState.settings, ...settings };
            
            // Update UI
            Elements.defaultModel.value = settings.defaultModel || '';
            Elements.defaultMaxTokens.value = settings.defaultMaxTokens || 1000;
            Elements.defaultTopK.value = settings.defaultTopK || 3;
            Elements.themeSelect.value = settings.theme || 'dark';
            
            // Apply theme
            document.documentElement.setAttribute('data-theme', settings.theme || 'dark');
        }
    }
};

// Backend Communication
const Backend = {
    async queryLLM(prompt, model = null, maxTokens = null) {
        try {
            const query = {
                prompt: prompt,
                model: model,
                max_tokens: maxTokens
            };
            
            const response = await invoke('query_willow_llm', { query });
            return response;
        } catch (error) {
            console.error('LLM Query Error:', error);
            return {
                success: false,
                error: `Failed to communicate with backend: ${error}`
            };
        }
    },
    
    async queryRAG(query, documents = null, topK = null) {
        try {
            const ragQuery = {
                query: query,
                documents: documents,
                top_k: topK
            };
            
            const response = await invoke('query_willow_rag', { query: ragQuery });
            return response;
        } catch (error) {
            console.error('RAG Query Error:', error);
            return {
                success: false,
                error: `Failed to communicate with backend: ${error}`
            };
        }
    },
    
    async getStatus() {
        try {
            const response = await invoke('get_willow_status');
            return response;
        } catch (error) {
            console.error('Status Query Error:', error);
            return {
                success: false,
                error: `Failed to get backend status: ${error}`
            };
        }
    }
};

// Chat Functions
const Chat = {
    addMessage(content, type = 'user', sender = null) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        
        const senderText = sender ? `<strong>${sender}:</strong> ` : '';
        messageDiv.innerHTML = `
            <div class="message-content">${senderText}${content}</div>
            <div class="message-time">${Utils.formatTime()}</div>
        `;
        
        Elements.chatMessages.appendChild(messageDiv);
        Elements.chatMessages.scrollTop = Elements.chatMessages.scrollHeight;
    },
    
    async sendMessage(prompt) {
        // Add user message
        Chat.addMessage(prompt, 'user');
        
        // Show loading
        Utils.showLoading();
        
        // Get model and max tokens from UI
        const model = Elements.modelSelect.value || AppState.settings.defaultModel || null;
        const maxTokens = parseInt(Elements.maxTokensInput.value) || AppState.settings.defaultMaxTokens;
        
        try {
            // Query backend
            const response = await Backend.queryLLM(prompt, model, maxTokens);
            
            if (response.success) {
                Chat.addMessage(response.data, 'assistant', 'Willow');
            } else {
                Chat.addMessage(`Error: ${response.error}`, 'system');
            }
        } catch (error) {
            Chat.addMessage(`Failed to send message: ${error}`, 'system');
        } finally {
            Utils.hideLoading();
        }
    }
};

// RAG Functions
const RAG = {
    async search(query, documents = null, topK = null) {
        Utils.showLoading();
        
        try {
            // Parse documents if provided
            let docsArray = null;
            if (documents && documents.trim()) {
                docsArray = documents.split('\n').filter(doc => doc.trim()).map(doc => doc.trim());
            }
            
            const ragTopK = topK || AppState.settings.defaultTopK;
            
            // Query backend
            const response = await Backend.queryRAG(query, docsArray, ragTopK);
            
            if (response.success) {
                RAG.displayResult(response.data);
            } else {
                RAG.displayError(response.error);
            }
        } catch (error) {
            RAG.displayError(`Failed to perform RAG search: ${error}`);
        } finally {
            Utils.hideLoading();
        }
    },
    
    displayResult(result) {
        Elements.ragResults.innerHTML = `
            <div class="rag-result">
                <div class="rag-result-header">📚 RAG Search Result</div>
                <div class="rag-result-content">${result}</div>
            </div>
        `;
    },
    
    displayError(error) {
        Elements.ragResults.innerHTML = `
            <div class="rag-result">
                <div class="rag-result-header">❌ Error</div>
                <div class="rag-result-content">${error}</div>
            </div>
        `;
    }
};

// Status Functions
const Status = {
    async refresh() {
        Utils.showLoading();
        
        try {
            const response = await Backend.getStatus();
            
            if (response.success) {
                Status.updateUI(response.data);
                Utils.updateStatus('connected', 'Connected');
                AppState.isConnected = true;
            } else {
                Utils.updateStatus('error', 'Connection failed');
                Status.displayError(response.error);
                AppState.isConnected = false;
            }
        } catch (error) {
            Utils.updateStatus('error', 'Backend unavailable');
            Status.displayError(`Failed to get status: ${error}`);
            AppState.isConnected = false;
        } finally {
            Utils.hideLoading();
        }
    },
    
    updateUI(data) {
        // Update backend status
        Elements.backendStatusValue.textContent = '✅ Connected';
        Elements.versionValue.textContent = data.version || 'Unknown';
        
        // Update capabilities
        AppState.capabilities = data.capabilities || {};
        Status.updateCapabilities();
        
        // Update models
        AppState.models = data.models || [];
        Status.updateModels();
        
        // Update performance stats
        Status.updatePerformanceStats(data.performance_stats || {});
        
        // Update features grid
        Status.updateFeaturesGrid(data.capabilities || {});
    },
    
    updateCapabilities() {
        const capsList = Elements.capabilitiesList;
        capsList.innerHTML = '';
        
        Object.entries(AppState.capabilities).forEach(([key, available]) => {
            const item = document.createElement('div');
            item.className = 'capability-item';
            
            const status = available ? '✅' : '❌';
            const name = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
            
            item.innerHTML = `
                <span class="capability-status">${status}</span>
                <span>${name}</span>
            `;
            
            capsList.appendChild(item);
        });
    },
    
    updateModels() {
        // Update model selects
        [Elements.modelSelect, Elements.defaultModel].forEach(select => {
            const currentValue = select.value;
            select.innerHTML = '<option value="">Auto-select model</option>';
            
            AppState.models.forEach(model => {
                const option = document.createElement('option');
                option.value = model;
                option.textContent = model;
                select.appendChild(option);
            });
            
            // Restore selection if still valid
            if (AppState.models.includes(currentValue)) {
                select.value = currentValue;
            }
        });
        
        // Update models list in status tab
        Elements.modelsList.innerHTML = '';
        AppState.models.forEach(model => {
            const item = document.createElement('div');
            item.className = 'model-item';
            item.textContent = model;
            Elements.modelsList.appendChild(item);
        });
    },
    
    updatePerformanceStats(stats) {
        Elements.performanceStats.innerHTML = '';
        
        Object.entries(stats).forEach(([key, value]) => {
            const item = document.createElement('div');
            item.className = 'performance-item';
            
            const displayKey = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
            item.textContent = `${displayKey}: ${value}`;
            
            Elements.performanceStats.appendChild(item);
        });
    },
    
    updateFeaturesGrid(capabilities) {
        Elements.featuresGrid.innerHTML = '';
        
        Object.entries(capabilities).forEach(([key, available]) => {
            const item = document.createElement('div');
            item.className = 'feature-item';
            
            const status = available ? '✅' : '❌';
            const name = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
            
            item.innerHTML = `
                <span class="feature-status">${status}</span>
                <span>${name}</span>
            `;
            
            Elements.featuresGrid.appendChild(item);
        });
    },
    
    displayError(error) {
        Elements.backendStatusValue.textContent = '❌ Error';
        Elements.featuresGrid.innerHTML = `<div class="error-message">Error: ${error}</div>`;
    }
};

// Navigation Functions
const Navigation = {
    init() {
        Elements.navItems.forEach(item => {
            item.addEventListener('click', () => {
                const tab = item.dataset.tab;
                Navigation.switchTab(tab);
            });
        });
    },
    
    switchTab(tabName) {
        // Update nav items
        Elements.navItems.forEach(item => {
            if (item.dataset.tab === tabName) {
                item.classList.add('active');
            } else {
                item.classList.remove('active');
            }
        });
        
        // Update tab contents
        Elements.tabContents.forEach(content => {
            if (content.id === `${tabName}Content`) {
                content.classList.add('active');
            } else {
                content.classList.remove('active');
            }
        });
    }
};

// Event Listeners
function setupEventListeners() {
    // Navigation
    Navigation.init();
    
    // Chat form
    Elements.chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const message = Elements.chatInput.value.trim();
        if (message) {
            Elements.chatInput.value = '';
            await Chat.sendMessage(message);
        }
    });
    
    // Chat input - Enter to send (Shift+Enter for new line)
    Elements.chatInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            Elements.chatForm.dispatchEvent(new Event('submit'));
        }
    });
    
    // RAG form
    Elements.ragForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const query = Elements.ragQuery.value.trim();
        if (query) {
            const documents = Elements.ragDocuments.value.trim();
            const topK = parseInt(Elements.ragTopK.value) || 3;
            await RAG.search(query, documents, topK);
        }
    });
    
    // Settings
    Elements.saveSettingsButton.addEventListener('click', () => {
        Utils.saveSettings();
        // Show confirmation
        Elements.saveSettingsButton.textContent = 'Saved! 💾';
        setTimeout(() => {
            Elements.saveSettingsButton.textContent = 'Save Settings 💾';
        }, 2000);
    });
    
    // Status refresh
    Elements.refreshStatusButton.addEventListener('click', Status.refresh);
}

// Initialization
async function initialize() {
    console.log('🌲 Initializing Willow Desktop v6.0.0');
    
    // Load settings
    Utils.loadSettings();
    
    // Setup event listeners
    setupEventListeners();
    
    // Set welcome time
    const welcomeTimeEl = document.getElementById('welcomeTime');
    if (welcomeTimeEl) {
        welcomeTimeEl.textContent = Utils.formatTime();
    }
    
    // Initial status check
    await Status.refresh();
    
    console.log('✅ Willow Desktop initialized');
}

// Start the application when DOM is loaded
document.addEventListener('DOMContentLoaded', initialize);

// Handle window focus for reconnection
window.addEventListener('focus', () => {
    if (!AppState.isConnected) {
        Status.refresh();
    }
});

// Export for debugging
window.WillowApp = {
    AppState,
    Backend,
    Chat,
    RAG,
    Status,
    Utils
};