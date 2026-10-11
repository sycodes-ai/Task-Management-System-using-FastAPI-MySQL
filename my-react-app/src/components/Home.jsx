import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';
import { getErrorMessage } from '../utils';
import AdminDashboard from './AdminDashboard';
import StaffDashboard from './StaffDashboard';

function Home() {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [attempt, setAttempt] = useState(0);
    const navigate = useNavigate();

    useEffect(() => {
        let cancelled = false;
        api.get('/users/me')
            .then(({ data }) => {
                if (!cancelled) setUser(data);
            })
            .catch((err) => {
                // A 401 is handled by the API client (back to /login)
                if (!cancelled) setError(getErrorMessage(err, 'Could not load your profile.'));
            })
            .finally(() => {
                if (!cancelled) setLoading(false);
            });
        return () => { cancelled = true; };
    }, [attempt]);

    const retry = () => {
        setError('');
        setLoading(true);
        setAttempt(n => n + 1);
    };

    const logout = () => {
        localStorage.removeItem('token');
        navigate('/login');
    };

    if (loading) {
        return <div className="dashboard-layout"><div className="header-content"><h2>Loading...</h2></div></div>;
    }

    if (!user) {
        return (
            <div className="dashboard-layout">
                <div className="dashboard-main">
                    <div className="error-message" role="alert">{error || 'Could not load your profile.'}</div>
                    <button onClick={retry} className="secondary-button">Try again</button>{' '}
                    <button onClick={logout} className="text-button">Log out</button>
                </div>
            </div>
        );
    }

    if (user.role === 'admin') {
        return <AdminDashboard user={user} />;
    } else {
        return <StaffDashboard user={user} />;
    }
}

export default Home;
