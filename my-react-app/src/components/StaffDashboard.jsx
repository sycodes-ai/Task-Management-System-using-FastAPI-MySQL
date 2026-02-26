import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';

function StaffDashboard({ user }) {
    const [tasks, setTasks] = useState([]);
    const navigate = useNavigate();

    useEffect(() => {
        fetchTasks();
    }, []);

    const fetchTasks = async () => {
        try {
            const { data } = await api.get('/tasks/');
            setTasks(data);
        } catch (err) {
            console.error('Failed to fetch tasks', err);
        }
    };

    const handleToggleTask = async (task) => {
        try {
            await api.put(`/tasks/${task.id}`, {
                ...task,
                is_completed: !task.is_completed // Must match backend 'is_completed'
            });
            fetchTasks();
        } catch (err) {
            console.error('Failed to update task', err);
        }
    };

    const handleLogout = () => {
        localStorage.removeItem('token');
        navigate('/login');
    };

    return (
        <div className="dashboard-layout">
            <header className="dashboard-header">
                <div className="header-content">
                    <h1>My Tasks</h1>
                    <div className="user-controls">
                        <span className="user-greeting">Hello, {user?.custom_username} (Staff)</span>
                        <button onClick={handleLogout} className="text-button">Logout</button>
                    </div>
                </div>
            </header>

            <main className="dashboard-main">
                <section className="tasks-section">
                    {tasks.length === 0 ? (
                        <div className="empty-state">
                            <p>You have no tasks assigned yet.</p>
                        </div>
                    ) : (
                        <div className="task-grid">
                            {tasks.map(task => (
                                <div key={task.id} className={`task-card ${task.is_completed ? 'completed' : ''}`}>
                                    <div className="task-content">
                                        <div className="checkbox-wrapper" onClick={() => handleToggleTask(task)}>
                                            <div className={`custom-checkbox ${task.is_completed ? 'checked' : ''}`}></div>
                                        </div>
                                        <div>
                                            <h3>{task.title}</h3>
                                            {task.description && <p>{task.description}</p>}
                                        </div>
                                    </div>
                                    {/* Staff cannot delete tasks */}
                                </div>
                            ))}
                        </div>
                    )}
                </section>
            </main>
        </div>
    );
}

export default StaffDashboard;
