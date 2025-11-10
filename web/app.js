const API_BASE = window.location.hostname === 'localhost' 
    ? 'http://localhost:8000' 
    : window.location.origin;

function app() {
    return {
        isAuthenticated: false,
        token: null,
        username: '',
        currentTab: 'dashboard',
        loginForm: { username: '', password: '' },
        loginError: '',
        stats: {},
        apiKeys: [],
        models: [],
        showAddKeyModal: false,
        newKey: {
            name: '',
            expiration_type: 'never',
            duration_days: 30,
            expires_at: '',
            daily_limit: 0
        },
        testForm: {
            apiKeyId: '',
            file: null
        },
        testResult: null,

        async init() {
            // Check if token exists in localStorage
            const savedToken = localStorage.getItem('admin_token');
            const savedUsername = localStorage.getItem('admin_username');
            if (savedToken) {
                this.token = savedToken;
                this.username = savedUsername;
                this.isAuthenticated = true;
                await this.loadDashboard();
            }
        },

        async login() {
            try {
                const response = await fetch(`${API_BASE}/admin/auth/login`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(this.loginForm)
                });

                if (!response.ok) {
                    this.loginError = 'Invalid credentials';
                    return;
                }

                const data = await response.json();
                this.token = data.access_token;
                this.username = this.loginForm.username;
                localStorage.setItem('admin_token', this.token);
                localStorage.setItem('admin_username', this.username);
                this.isAuthenticated = true;
                this.loginError = '';
                await this.loadDashboard();
            } catch (error) {
                this.loginError = 'Login failed: ' + error.message;
            }
        },

        logout() {
            this.isAuthenticated = false;
            this.token = null;
            this.username = '';
            localStorage.removeItem('admin_token');
            localStorage.removeItem('admin_username');
            this.loginForm = { username: '', password: '' };
        },

        async loadDashboard() {
            await this.loadStats();
            await this.loadApiKeys();
            await this.loadModels();
        },

        async loadStats() {
            try {
                const response = await fetch(`${API_BASE}/admin/stats/dashboard`, {
                    headers: { 'Authorization': `Bearer ${this.token}` }
                });
                if (response.ok) {
                    this.stats = await response.json();
                }
            } catch (error) {
                console.error('Failed to load stats:', error);
            }
        },

        async loadApiKeys() {
            try {
                const response = await fetch(`${API_BASE}/admin/keys`, {
                    headers: { 'Authorization': `Bearer ${this.token}` }
                });
                if (response.ok) {
                    this.apiKeys = await response.json();
                }
            } catch (error) {
                console.error('Failed to load API keys:', error);
            }
        },

        async loadModels() {
            try {
                const response = await fetch(`${API_BASE}/admin/models`, {
                    headers: { 'Authorization': `Bearer ${this.token}` }
                });
                if (response.ok) {
                    this.models = await response.json();
                }
            } catch (error) {
                console.error('Failed to load models:', error);
            }
        },

        async createApiKey() {
            try {
                const payload = {
                    name: this.newKey.name,
                    expiration_type: this.newKey.expiration_type,
                    daily_limit: parseInt(this.newKey.daily_limit) || null
                };

                if (this.newKey.expiration_type === 'duration') {
                    payload.duration_days = parseInt(this.newKey.duration_days);
                } else if (this.newKey.expiration_type === 'date') {
                    payload.expires_at = new Date(this.newKey.expires_at).toISOString();
                }

                const response = await fetch(`${API_BASE}/admin/keys`, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${this.token}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(payload)
                });

                if (response.ok) {
                    this.showAddKeyModal = false;
                    this.newKey = { name: '', expiration_type: 'never', duration_days: 30, expires_at: '', daily_limit: 0 };
                    await this.loadApiKeys();
                    alert('API key created successfully!');
                } else {
                    const error = await response.json();
                    alert('Failed to create API key: ' + error.detail);
                }
            } catch (error) {
                alert('Failed to create API key: ' + error.message);
            }
        },

        async copyKey(keyId) {
            try {
                const response = await fetch(`${API_BASE}/admin/keys/${keyId}`, {
                    headers: { 'Authorization': `Bearer ${this.token}` }
                });
                if (response.ok) {
                    const key = await response.json();
                    await navigator.clipboard.writeText(key.key_value);
                    alert('API key copied to clipboard!');
                }
            } catch (error) {
                alert('Failed to copy key');
            }
        },

        async toggleKey(keyId) {
            try {
                const response = await fetch(`${API_BASE}/admin/keys/${keyId}/toggle`, {
                    method: 'PATCH',
                    headers: { 'Authorization': `Bearer ${this.token}` }
                });
                if (response.ok) {
                    await this.loadApiKeys();
                }
            } catch (error) {
                alert('Failed to toggle key');
            }
        },

        async renewKey(keyId) {
            const days = prompt('Enter number of days to extend:');
            if (!days) return;

            try {
                const response = await fetch(`${API_BASE}/admin/keys/${keyId}/renew`, {
                    method: 'PATCH',
                    headers: {
                        'Authorization': `Bearer ${this.token}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        expiration_type: 'duration',
                        duration_days: parseInt(days)
                    })
                });
                if (response.ok) {
                    await this.loadApiKeys();
                    alert('API key renewed successfully!');
                }
            } catch (error) {
                alert('Failed to renew key');
            }
        },

        async deleteKey(keyId) {
            if (!confirm('Are you sure you want to delete this API key?')) return;

            try {
                const response = await fetch(`${API_BASE}/admin/keys/${keyId}`, {
                    method: 'DELETE',
                    headers: { 'Authorization': `Bearer ${this.token}` }
                });
                if (response.ok) {
                    await this.loadApiKeys();
                    alert('API key deleted successfully!');
                }
            } catch (error) {
                alert('Failed to delete key');
            }
        },

        async uploadModel(event) {
            const file = event.target.files[0];
            if (!file) return;

            const formData = new FormData();
            formData.append('file', file);

            try {
                const response = await fetch(`${API_BASE}/admin/models/upload`, {
                    method: 'POST',
                    headers: { 'Authorization': `Bearer ${this.token}` },
                    body: formData
                });

                if (response.ok) {
                    await this.loadModels();
                    alert('Model uploaded successfully!');
                } else {
                    alert('Failed to upload model');
                }
            } catch (error) {
                alert('Failed to upload model: ' + error.message);
            }
        },

        async activateModel(modelId) {
            try {
                const response = await fetch(`${API_BASE}/admin/models/${modelId}/activate`, {
                    method: 'PATCH',
                    headers: { 'Authorization': `Bearer ${this.token}` }
                });
                if (response.ok) {
                    await this.loadModels();
                    await this.loadStats();
                    alert('Model activated successfully!');
                }
            } catch (error) {
                alert('Failed to activate model');
            }
        },

        async deleteModel(modelId) {
            if (!confirm('Are you sure you want to delete this model?')) return;

            try {
                const response = await fetch(`${API_BASE}/admin/models/${modelId}`, {
                    method: 'DELETE',
                    headers: { 'Authorization': `Bearer ${this.token}` }
                });
                if (response.ok) {
                    await this.loadModels();
                    alert('Model deleted successfully!');
                }
            } catch (error) {
                alert('Failed to delete model');
            }
        },

        async testDetection() {
            if (!this.testForm.apiKeyId || !this.testForm.file) {
                alert('Please select API key and image file');
                return;
            }

            // Get the API key value
            const key = await fetch(`${API_BASE}/admin/keys/${this.testForm.apiKeyId}`, {
                headers: { 'Authorization': `Bearer ${this.token}` }
            }).then(r => r.json());

            const formData = new FormData();
            formData.append('file', this.testForm.file);

            try {
                const response = await fetch(`${API_BASE}/api/v1/detect?include_visual=true`, {
                    method: 'POST',
                    headers: { 'X-API-Key': key.key_value },
                    body: formData
                });

                if (response.ok) {
                    this.testResult = await response.json();
                } else {
                    alert('Detection failed');
                }
            } catch (error) {
                alert('Detection failed: ' + error.message);
            }
        }
    }
}
