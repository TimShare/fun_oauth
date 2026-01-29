// API Base URL
const API_BASE = '';

// Текущий токен
let authToken = localStorage.getItem('authToken');

// Инициализация приложения
document.addEventListener('DOMContentLoaded', () => {
    initApp();
});

function initApp() {
    updateNav();
    
    // Проверяем URL параметры (для OAuth callback)
    let token = null;
    
    // Пытаемся получить из query параметров
    const urlParams = new URLSearchParams(window.location.search);
    token = urlParams.get('token');
    
    // Если не нашли в search, проверяем hash
    if (!token && window.location.hash) {
        const hashParams = new URLSearchParams(window.location.hash.substring(1));
        token = hashParams.get('token');
    }
    
    if (token) {
        authToken = token;
        localStorage.setItem('authToken', token);
        window.history.replaceState({}, document.title, '/');
        showPage('profile');
        return;
    }

    // Показываем соответствующую страницу
    if (authToken) {
        showPage('profile');
    } else {
        showPage('home');
    }
}

function updateNav() {
    const nav = document.getElementById('nav');
    
    if (authToken) {
        nav.innerHTML = `
            <button onclick="showPage('profile')">Профиль</button>
            <button onclick="logout()">Выйти</button>
        `;
    } else {
        nav.innerHTML = `
            <button onclick="showPage('home')">Главная</button>
            <button onclick="showPage('login')">Вход</button>
            <button onclick="showPage('register')">Регистрация</button>
        `;
    }
}

function showPage(page) {
    const app = document.getElementById('app');
    
    switch(page) {
        case 'home':
            app.innerHTML = getHomePage();
            break;
        case 'login':
            app.innerHTML = getLoginPage();
            break;
        case 'register':
            app.innerHTML = getRegisterPage();
            break;
        case 'profile':
            loadProfile();
            break;
    }
}

function getHomePage() {
    return `
        <div class="home-welcome">
            <h2>Добро пожаловать!</h2>
            <p>Современное приложение с чистой архитектурой и множественными способами авторизации</p>
            
            <div class="features">
                <div class="feature">
                    <h3>🔐 Google OAuth</h3>
                    <p>Быстрый вход через Google аккаунт</p>
                </div>
                <div class="feature">
                    <h3>📧 Email + Пароль</h3>
                    <p>Классическая регистрация с email</p>
                </div>
                <div class="feature">
                    <h3>🛡️ JWT Токены</h3>
                    <p>Безопасная аутентификация</p>
                </div>
            </div>
            
            <button onclick="showPage('register')" style="margin-top: 30px;">
                Начать
            </button>
        </div>
    `;
}

function getLoginPage() {
    return `
        <h2 style="margin-bottom: 25px; text-align: center;">Вход</h2>
        <div id="message"></div>
        
        <form onsubmit="handleLogin(event)">
            <div class="form-group">
                <label>Email</label>
                <input type="email" id="email" required>
            </div>
            <div class="form-group">
                <label>Пароль</label>
                <input type="password" id="password" required>
            </div>
            <button type="submit">Войти</button>
        </form>
        
        <div class="divider"><span>или</span></div>
        
        <button class="google" onclick="loginWithGoogle()">
            Войти через Google
        </button>
        
        <button class="secondary" onclick="showPage('register')">
            Нет аккаунта? Зарегистрироваться
        </button>
    `;
}

function getRegisterPage() {
    return `
        <h2 style="margin-bottom: 25px; text-align: center;">Регистрация</h2>
        <div id="message"></div>
        
        <form onsubmit="handleRegister(event)">
            <div class="form-group">
                <label>Email</label>
                <input type="email" id="email" required>
            </div>
            <div class="form-group">
                <label>Имя (необязательно)</label>
                <input type="text" id="fullName">
            </div>
            <div class="form-group">
                <label>Пароль</label>
                <input type="password" id="password" required minlength="6">
            </div>
            <button type="submit">Зарегистрироваться</button>
        </form>
        
        <div class="divider"><span>или</span></div>
        
        <button class="google" onclick="loginWithGoogle()">
            Регистрация через Google
        </button>
        
        <button class="secondary" onclick="showPage('login')">
            Уже есть аккаунт? Войти
        </button>
    `;
}

async function handleLogin(event) {
    event.preventDefault();
    
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    
    try {
        const response = await fetch(`${API_BASE}/auth/login`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ email, password })
        });
        
        if (!response.ok) {
            const error = await response.json();
            showMessage(error.detail || 'Ошибка входа', 'error');
            return;
        }
        
        const data = await response.json();
        authToken = data.access_token;
        localStorage.setItem('authToken', authToken);
        
        updateNav();
        showPage('profile');
        
    } catch (error) {
        showMessage('Ошибка подключения к серверу', 'error');
    }
}

async function handleRegister(event) {
    event.preventDefault();
    
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const fullName = document.getElementById('fullName').value;
    
    try {
        const response = await fetch(`${API_BASE}/auth/register`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ 
                email, 
                password,
                full_name: fullName || null
            })
        });
        
        if (!response.ok) {
            const error = await response.json();
            showMessage(error.detail || 'Ошибка регистрации', 'error');
            return;
        }
        
        const data = await response.json();
        authToken = data.access_token;
        localStorage.setItem('authToken', authToken);
        
        updateNav();
        showPage('profile');
        
    } catch (error) {
        showMessage('Ошибка подключения к серверу', 'error');
    }
}

async function loadProfile() {
    const app = document.getElementById('app');
    app.innerHTML = '<div class="loading">Загрузка профиля</div>';
    
    try {
        const response = await fetch(`${API_BASE}/auth/me`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        if (!response.ok) {
            throw new Error('Не удалось загрузить профиль');
        }
        
        const user = await response.json();
        
        app.innerHTML = `
            <h2 style="margin-bottom: 25px; text-align: center;">Профиль</h2>
            
            <div class="profile-card">
                ${user.picture ? `<img src="${user.picture}" alt="Avatar">` : ''}
                <h2>${user.full_name || 'Пользователь'}</h2>
                <p><strong>Email:</strong> ${user.email}</p>
                <p><strong>ID:</strong> ${user.id}</p>
                <p><strong>Статус:</strong> ${user.is_active ? '✅ Активен' : '❌ Неактивен'}</p>
            </div>
            
            <button onclick="logout()">Выйти</button>
        `;
        
    } catch (error) {
        showMessage('Ошибка загрузки профиля', 'error');
        logout();
    }
}

function loginWithGoogle() {
    window.location.href = `${API_BASE}/auth/google/login`;
}

function logout() {
    authToken = null;
    localStorage.removeItem('authToken');
    updateNav();
    showPage('home');
}

function showMessage(text, type = 'error') {
    const messageDiv = document.getElementById('message');
    if (messageDiv) {
        messageDiv.innerHTML = `<div class="${type}">${text}</div>`;
        setTimeout(() => {
            messageDiv.innerHTML = '';
        }, 5000);
    }
}
