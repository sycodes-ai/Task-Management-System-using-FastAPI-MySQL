import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import api from '../api';
import { getErrorMessage } from '../utils';

function Register() {
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [submitting, setSubmitting] = useState(false);
    const navigate = useNavigate();

    const handleRegister = async (e) => {
        e.preventDefault();
        setError('');
        setSubmitting(true);
        try {
            // New accounts are always staff; the server decides the role
            await api.post('/users/register', {
                custom_username: username,
                email: email,
                password: password
            });
            navigate('/login');
        } catch (err) {
            setError(getErrorMessage(err, 'Registration failed'));
            setSubmitting(false);
        }
    };

    return (
        <div className="auth-container">
            <div className="auth-card">
                <h2>Create Account</h2>
                <p className="subtitle">Join to manage your tasks effectively</p>

                {error && <div className="error-message" role="alert">{error}</div>}

                <form onSubmit={handleRegister}>
                    <div className="form-group">
                        <label htmlFor="username">Username</label>
                        <input
                            id="username"
                            type="text"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            placeholder="Choose a username"
                            minLength={3}
                            maxLength={50}
                            required
                        />
                    </div>
                    <div className="form-group">
                        <label htmlFor="email">Email</label>
                        <input
                            id="email"
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
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
                            placeholder="At least 8 characters"
                            minLength={8}
                            required
                        />
                    </div>
                    <p className="note">New accounts are staff. Use the demo admin to assign tasks.</p>
                    <button type="submit" className="primary-button" disabled={submitting}>
                        {submitting ? 'Creating account...' : 'Register'}
                    </button>
                </form>

                <p className="auth-switch">
                    Already have an account? <Link to="/login">Sign in here</Link>
                </p>
            </div>
        </div>
    );
}

export default Register;
