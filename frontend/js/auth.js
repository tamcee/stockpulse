/**
 * Authentication UI Module
 * Handles login/register modals and auth state management.
 */
const Auth = {
    init() {
        this.modal = document.getElementById('authModal');
        this.modalTitle = document.getElementById('authModalTitle');
        this.modalBody = document.getElementById('authModalBody');
        this.closeBtn = document.getElementById('authModalClose');
        this.topbarActions = document.getElementById('topbarActions');

        this.closeBtn.addEventListener('click', () => this.hideModal());
        this.modal.addEventListener('click', (e) => {
            if (e.target === this.modal) this.hideModal();
        });

        this.updateUI();
    },

    isLoggedIn() {
        return !!localStorage.getItem('auth_token');
    },

    getUser() {
        const user = localStorage.getItem('auth_user');
        return user ? JSON.parse(user) : null;
    },

    getToken() {
        return localStorage.getItem('auth_token');
    },

    updateUI() {
        if (this.isLoggedIn()) {
            const user = this.getUser();
            const initial = user ? user.username.charAt(0).toUpperCase() : '?';
            this.topbarActions.innerHTML = `
                <div class="user-info">
                    <div class="user-avatar">${initial}</div>
                    <span class="user-name">${user ? user.username : 'User'}</span>
                </div>
                <button class="btn btn-ghost btn-sm" id="logoutBtn">Logout</button>
            `;
            document.getElementById('logoutBtn').addEventListener('click', () => this.logout());
        } else {
            this.topbarActions.innerHTML = `
                <button class="btn btn-secondary btn-sm" id="loginBtn">Sign In</button>
                <button class="btn btn-primary btn-sm" id="registerBtn">Sign Up</button>
            `;
            document.getElementById('loginBtn').addEventListener('click', () => this.showLogin());
            document.getElementById('registerBtn').addEventListener('click', () => this.showRegister());
        }
    },

    showLogin() {
        this.modalTitle.textContent = 'Sign In';
        this.modalBody.innerHTML = `
            <form id="loginForm">
                <div class="form-group">
                    <label class="form-label">Email</label>
                    <input type="email" class="form-input" id="loginEmail" placeholder="your@email.com" required>
                </div>
                <div class="form-group">
                    <label class="form-label">Password</label>
                    <input type="password" class="form-input" id="loginPassword" placeholder="••••••••" required>
                </div>
                <div class="form-error" id="loginError" style="display:none;"></div>
                <button type="submit" class="btn btn-primary" style="width:100%; margin-top:8px;">Sign In</button>
                <p class="form-switch">Don't have an account? <a href="#" id="switchToRegister">Sign Up</a></p>
            </form>
        `;
        document.getElementById('loginForm').addEventListener('submit', (e) => this.handleLogin(e));
        document.getElementById('switchToRegister').addEventListener('click', (e) => { e.preventDefault(); this.showRegister(); });
        this.showModal();
    },

    showRegister() {
        this.modalTitle.textContent = 'Create Account';
        this.modalBody.innerHTML = `
            <form id="registerForm">
                <div class="form-group">
                    <label class="form-label">Username</label>
                    <input type="text" class="form-input" id="regUsername" placeholder="Choose a username" required minlength="3">
                </div>
                <div class="form-group">
                    <label class="form-label">Email</label>
                    <input type="email" class="form-input" id="regEmail" placeholder="your@email.com" required>
                </div>
                <div class="form-group">
                    <label class="form-label">Password</label>
                    <input type="password" class="form-input" id="regPassword" placeholder="Min. 6 characters" required minlength="6">
                </div>
                <div class="form-error" id="registerError" style="display:none;"></div>
                <button type="submit" class="btn btn-primary" style="width:100%; margin-top:8px;">Create Account</button>
                <p class="form-switch">Already have an account? <a href="#" id="switchToLogin">Sign In</a></p>
            </form>
        `;
        document.getElementById('registerForm').addEventListener('submit', (e) => this.handleRegister(e));
        document.getElementById('switchToLogin').addEventListener('click', (e) => { e.preventDefault(); this.showLogin(); });
        this.showModal();
    },

    async handleLogin(e) {
        e.preventDefault();
        const email = document.getElementById('loginEmail').value;
        const password = document.getElementById('loginPassword').value;
        const errorEl = document.getElementById('loginError');

        try {
            const data = await API.login(email, password);
            localStorage.setItem('auth_token', data.token);
            localStorage.setItem('auth_user', JSON.stringify(data.user));
            this.hideModal();
            this.updateUI();
            App.showToast('Welcome back, ' + data.user.username + '!', 'success');
        } catch (err) {
            errorEl.textContent = err.message;
            errorEl.style.display = 'block';
        }
    },

    async handleRegister(e) {
        e.preventDefault();
        const username = document.getElementById('regUsername').value;
        const email = document.getElementById('regEmail').value;
        const password = document.getElementById('regPassword').value;
        const errorEl = document.getElementById('registerError');

        try {
            const data = await API.register(username, email, password);
            localStorage.setItem('auth_token', data.token);
            localStorage.setItem('auth_user', JSON.stringify(data.user));
            this.hideModal();
            this.updateUI();
            App.showToast('Account created! Welcome, ' + data.user.username + '!', 'success');
        } catch (err) {
            errorEl.textContent = err.message;
            errorEl.style.display = 'block';
        }
    },

    logout() {
        localStorage.removeItem('auth_token');
        localStorage.removeItem('auth_user');
        this.updateUI();
        App.showToast('Signed out successfully.', 'info');
        // Reload watchlist view if currently on it
        if (App.currentView === 'watchlist') {
            App.navigateTo('dashboard');
        }
    },

    showModal() {
        this.modal.classList.add('visible');
    },

    hideModal() {
        this.modal.classList.remove('visible');
    },
};
