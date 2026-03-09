// Authentication Service
class AuthService {
    constructor() {
        this.currentUser = null;
        this.apiService = null;
    }

    // Set API service
    setApiService(apiService) {
        this.apiService = apiService;
    }

    // Register new user
    async register(userData) {
        if (!this.apiService) {
            throw new Error('API service not initialized');
        }

        try {
            console.log('📝 Attempting registration...');
            const response = await this.apiService.register(userData);
            console.log('🔍 Debug - Registration response:', response);
            
            if (response && (response.access_token || response.token || response.id)) {
                const token = response.access_token || response.token;
                console.log('✅ Registration successful, token received:', token ? token.substring(0, 20) + '...' : 'undefined');
                if (token) {
                    this.apiService.setToken(token);
                    
                    // Load current user data
                    await this.loadCurrentUser();
                    console.log('✅ User data loaded successfully');
                }
                return response;
            } else {
                console.error('❌ Registration failed - no token in response:', response);
                throw new Error('Registration failed - Invalid response from server');
            }
            
        } catch (error) {
            console.error('❌ Registration error:', error);
            throw error;
        }
    }

    // Login user
    async login(credentials) {
        if (!this.apiService) {
            throw new Error('API service not initialized');
        }
        try {
            console.log('🔑 Attempting login with:', credentials.email);
            
            const response = await this.apiService.login(credentials);
            console.log('🔍 Debug - API response:', response);
            
            if (response && (response.access_token || response.token)) {
                const token = response.access_token || response.token;
                console.log('✅ Login successful, token received:', token ? token.substring(0, 20) + '...' : 'undefined');
                if (token) {
                    this.apiService.setToken(token);
                    
                    // Load current user data
                    await this.loadCurrentUser();
                    console.log('✅ User data loaded successfully');
                }
                return response;
            } else {
                console.error('❌ Login failed - no token in response:', response);
                throw new Error('Login failed - Invalid response from server');
            }
            
        } catch (error) {
            console.error('❌ Login error:', error);
            throw error;
        }
    }

    // Load current user
    async loadCurrentUser() {
        if (!this.apiService) {
            throw new Error('API service not initialized');
        }
        try {
            const user = await this.apiService.getCurrentUser();
            this.currentUser = user;
            return user;
        } catch (error) {
            console.error('Failed to load current user:', error);
            this.logout();
            return null;
        }
    }

    // Logout user
    logout() {
        if (this.apiService) {
            this.apiService.clearToken();
        }
        this.currentUser = null;
        window.location.href = 'login.html';
    }

    // Check if user is authenticated
    isAuthenticated() {
        return this.apiService && !!this.apiService.token;
    }

    // Get current user
    getCurrentUser() {
        return this.currentUser;
    }

    // Show error message
    showError(message) {
        const errorAlert = document.getElementById('errorAlert');
        const errorMessage = document.getElementById('errorMessage');
        if (errorAlert && errorMessage) {
            errorMessage.textContent = message;
            errorAlert.classList.remove('hidden');
            
            // Hide after 5 seconds
            setTimeout(() => {
                errorAlert.classList.add('hidden');
            }, 5000);
        } else {
            console.error('Error display elements not found');
            alert(message); // Fallback
        }
    }

    // Clear error message
    clearError() {
        const errorAlert = document.getElementById('errorAlert');
        if (errorAlert) {
            errorAlert.classList.add('hidden');
        }
    }

    // Validate email
    validateEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }

    // Validate password
    validatePassword(password) {
        return password && password.length >= 6;
    }

    // Handle form submission
    async handleAuthSubmit(event, isLogin = true) {
        event.preventDefault();
        this.clearError();

        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const fullName = document.getElementById('fullName')?.value;

        // Validation
        if (!this.validateEmail(email)) {
            this.showError('Please enter a valid email address');
            return;
        }

        if (!this.validatePassword(password)) {
            this.showError('Password must be at least 6 characters long');
            return;
        }

        if (!isLogin && !fullName) {
            this.showError('Please enter your full name');
            return;
        }

        const submitButton = document.querySelector('button[type="submit"]');
        const originalText = submitButton.textContent;
        
        try {
            // Show loading state
            submitButton.disabled = true;
            submitButton.textContent = 'Processing...';

            const userData = { email, password };
            if (!isLogin) {
                userData.name = fullName;
            }

            if (isLogin) {
                await this.login(userData);
            } else {
                await this.register(userData);
            }

            // Redirect to main app
            window.location.href = 'index.html';

        } catch (error) {
            this.showError(error.message || 'Authentication failed');
        } finally {
            // Reset button state
            submitButton.disabled = false;
            submitButton.textContent = originalText;
        }
    }

    // Initialize auth on page load
    async init() {
        if (this.isAuthenticated()) {
            await this.loadCurrentUser();
        }
    }
}

// Export singleton instance
const authService = new AuthService();

// Export to global scope
window.authService = authService;
