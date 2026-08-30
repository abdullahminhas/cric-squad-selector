// ─── Login Form ──────────────────────────────────────────────────────────────
const loginForm = document.getElementById('login-form');
if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const btn     = document.getElementById('login-btn');
        const btnText = document.getElementById('login-btn-text');
        const spinner = document.getElementById('login-btn-spinner');
        const errorEl = document.getElementById('auth-error');

        btnText.textContent = 'Signing in…';
        spinner.classList.remove('hidden');
        btn.disabled = true;
        errorEl.classList.add('hidden');

        try {
            const res  = await fetch('/login', {
                method:  'POST',
                headers: { 'Content-Type': 'application/json' },
                body:    JSON.stringify({
                    username: document.getElementById('login-username').value.trim(),
                    password: document.getElementById('login-password').value,
                }),
            });
            const data = await res.json();

            if (!res.ok) {
                errorEl.textContent = data.error || 'Login failed.';
                errorEl.classList.remove('hidden');
            } else {
                window.location.href = '/';
            }
        } catch (_) {
            errorEl.textContent = 'Network error. Please try again.';
            errorEl.classList.remove('hidden');
        } finally {
            btnText.textContent = 'Sign In';
            spinner.classList.add('hidden');
            btn.disabled = false;
        }
    });
}

// ─── Register Form ───────────────────────────────────────────────────────────
const registerForm = document.getElementById('register-form');
if (registerForm) {
    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const btn     = document.getElementById('register-btn');
        const btnText = document.getElementById('register-btn-text');
        const spinner = document.getElementById('register-btn-spinner');
        const errorEl = document.getElementById('auth-error');
        const successEl = document.getElementById('auth-success');

        btnText.textContent = 'Creating…';
        spinner.classList.remove('hidden');
        btn.disabled = true;
        errorEl.classList.add('hidden');
        successEl.classList.add('hidden');

        try {
            const res  = await fetch('/register', {
                method:  'POST',
                headers: { 'Content-Type': 'application/json' },
                body:    JSON.stringify({
                    username: document.getElementById('reg-username').value.trim(),
                    email:    document.getElementById('reg-email').value.trim(),
                    password: document.getElementById('reg-password').value,
                }),
            });
            const data = await res.json();

            if (!res.ok) {
                errorEl.textContent = data.error || 'Registration failed.';
                errorEl.classList.remove('hidden');
            } else {
                successEl.textContent = 'Account created! Redirecting…';
                successEl.classList.remove('hidden');
                setTimeout(() => window.location.href = '/', 1000);
            }
        } catch (_) {
            errorEl.textContent = 'Network error. Please try again.';
            errorEl.classList.remove('hidden');
        } finally {
            btnText.textContent = 'Create Account';
            spinner.classList.add('hidden');
            btn.disabled = false;
        }
    });
}
