import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';
import AdminDashboard from './AdminDashboard';
import StaffDashboard from './StaffDashboard';

function Home() {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();

    useEffect(() => {
        const fetchUser = async () => {
            try {
                const { data } = await api.get('/users/me');
                setUser(data);
            } catch (err) {
                localStorage.removeItem('token');
                navigate('/login');
            } finally {
                setLoading(false);
            }
        };
        fetchUser();
    }, [navigate]);

    if (loading) {
        return <div className="dashboard-layout"><div className="header-content"><h2>Loading...</h2></div></div>;
    }

    if (!user) {
        return null; // Will redirect via useEffect
    }

    if (user.role === 'admin') {
        return <AdminDashboard user={user} />;
    } else {
        return <StaffDashboard user={user} />;
    }
}

export default Home;
