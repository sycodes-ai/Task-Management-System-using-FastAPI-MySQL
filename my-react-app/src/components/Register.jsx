import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import api from '../api';

function Register() {
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const handleRegister = async (e) => {
        e.preventDefault();
        try {
            await api.post('/users/register', {
                custom_username: username,
                email: email,
                password: password
            });
            navigate('/login');
        } catch (err) {
            const detail = err.response?.data?.detail;
            if (Array.isArray(detail)) {
                // Handle FastAPI validation error arrays (e.g. 422 errors)
                setError(detail.map(d => `${d.loc.slice(-1)}: ${d.msg}`).join(', '));
            } else {
                // Handle string error messages
                setError(detail || 'Registration failed');
            }
        }
    };

    return (
        <div className="auth-container">
            <div className="auth-card">
                <h2>Create Account</h2>
                <p className="subtitle">Join to manage your tasks effectively</p>

                {error && <div className="error-message">{error}</div>}

                <form onSubmit={handleRegister}>
                    <div className="form-group">
                        <label>Username</label>
                        <input
                            type="text"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            placeholder="Choose a username"
                            required
                        />
                    </div>
                    <div className="form-group">
                        <label>Email</label>
                        <input
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            placeholder="Enter your email"
                            required
                        />
                    </div>
                    <div className="form-group">
                        <label>Password</label>
                        <input
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            placeholder="Create a strong password"
                            required
                        />
                    </div>
                    <button type="submit" className="primary-button">Register</button>
                </form>

                <p className="auth-switch">
                    Already have an account? <Link to="/login">Sign in here</Link>
                </p>
            </div>
        </div>
    );
}

export default Register;
