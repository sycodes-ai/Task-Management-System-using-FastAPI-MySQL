import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import api from '../api';
import { getErrorMessage } from '../utils';

const SHOW_DEMO = import.meta.env.VITE_DEMO_MODE !== 'false';
const DEMO_ACCOUNTS = {
    admin: { email: 'admin@demo.com', password: 'Admin123!' },
    staff: { email: 'staff@demo.com', password: 'Staff123!' },
};

function Login() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [submitting, setSubmitting] = useState(false);
    const navigate = useNavigate();

    const login = async (email, pass) => {
        setError('');
        setSubmitting(true);
        try {
            const formData = new URLSearchParams();
            formData.append('username', email);
            formData.append('password', pass);

            const response = await api.post('/login/access-token', formData, {
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
            });
            localStorage.setItem('token', response.data.access_token);
            navigate('/');
        } catch (err) {
            setError(getErrorMessage(err, 'Login failed'));
            setSubmitting(false);
        }
    };

    const handleLogin = (e) => {
        e.preventDefault();
        login(username, password);
    };

    const handleDemoLogin = (account) => {
        setUsername(account.email);
        setPassword(account.password);
        login(account.email, account.password);
    };

    return (
        <div className="auth-container">
            <div className="auth-card">
                <h2>Welcome Back</h2>
                <p className="subtitle">Sign in to manage your tasks</p>

                {error && <div className="error-message" role="alert">{error}</div>}

                <form onSubmit={handleLogin}>
                    <div className="form-group">
                        <label htmlFor="email">Email</label>
                        <input
                            id="email"
                            type="text"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            placeholder="Enter your email"
                            required
                        />
                    </div>
                    <div className="form-group">
                        <label htmlFor="password">Password</label>
                        <input
                            id="password"
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            placeholder="Enter your password"
                            required
                        />
                    </div>
                    <button type="submit" className="primary-button" disabled={submitting}>
                        {submitting ? 'Signing in...' : 'Sign In'}
                    </button>
                </form>

                {SHOW_DEMO && (
                    <div className="demo-box">
                        <h3>Demo accounts</h3>
                        <p>Try the app without registering.</p>
                        <div className="demo-buttons">
                            <button
                                type="button"
                                className="secondary-button"
                                disabled={submitting}
                                onClick={() => handleDemoLogin(DEMO_ACCOUNTS.admin)}
                            >
                                Log in as Admin
                            </button>
                            <button
                                type="button"
                                className="secondary-button"
                                disabled={submitting}
                                onClick={() => handleDemoLogin(DEMO_ACCOUNTS.staff)}
                            >
                                Log in as Staff
                            </button>
                        </div>
                    </div>
                )}

                <p className="auth-switch">
                    Don't have an account? <Link to="/register">Create one</Link>
                </p>
            </div>
        </div>
    );
}

export default Login;
