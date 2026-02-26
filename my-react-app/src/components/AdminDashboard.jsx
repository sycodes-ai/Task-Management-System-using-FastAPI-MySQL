import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';

function AdminDashboard({ user }) {
    const [tasks, setTasks] = useState([]);
    const [users, setUsers] = useState([]);
    const [newTaskTitle, setNewTaskTitle] = useState('');
    const [newTaskDesc, setNewTaskDesc] = useState('');
    const [selectedUserId, setSelectedUserId] = useState('');
    const navigate = useNavigate();

    useEffect(() => {
        fetchTasks();
        fetchUsers();
    }, []);

    const fetchTasks = async () => {
        try {
            const { data } = await api.get('/tasks/');
            setTasks(data);
        } catch (err) {
            console.error('Failed to fetch tasks', err);
        }
    };

    const fetchUsers = async () => {
        try {
            const { data } = await api.get('/users/');
            // Filter strictly to staff members if desired, or all users
            setUsers(data.filter(u => u.role === 'staff' || u.role === 'admin'));
            if (data.length > 0) {
                setSelectedUserId(data[0].id);
            }
        } catch (err) {
            console.error('Failed to fetch users', err);
        }
    };

    const handleCreateTask = async (e) => {
        e.preventDefault();
        if (!newTaskTitle.trim() || !selectedUserId) return;
        try {
            await api.post('/tasks/', { title: newTaskTitle, description: newTaskDesc, assignee_id: parseInt(selectedUserId) });
            setNewTaskTitle('');
            setNewTaskDesc('');
            fetchTasks();
        } catch (err) {
            console.error('Failed to create task', err);
        }
    };

    const handleToggleTask = async (task) => {
        try {
            await api.put(`/tasks/${task.id}`, {
                ...task,
                is_completed: !task.is_completed // Make sure this matches backend schema
            });
            fetchTasks();
        } catch (err) {
            console.error('Failed to update task', err);
        }
    };

    const handleDeleteTask = async (id) => {
        try {
            await api.delete(`/tasks/${id}`);
            fetchTasks();
        } catch (err) {
            console.error('Failed to delete task', err);
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
                    <h1>Admin Dashboard</h1>
                    <div className="user-controls">
                        <span className="user-greeting">Hello, {user?.custom_username} (Admin)</span>
                        <button onClick={handleLogout} className="text-button">Logout</button>
                    </div>
                </div>
            </header>

            <main className="dashboard-main">
                <section className="create-task-section">
                    <form className="create-task-form" onSubmit={handleCreateTask}>
                        <input
                            type="text"
                            placeholder="What needs to be done?"
                            value={newTaskTitle}
                            onChange={(e) => setNewTaskTitle(e.target.value)}
                            required
                        />
                        <input
                            type="text"
                            placeholder="Details (optional)"
                            value={newTaskDesc}
                            onChange={(e) => setNewTaskDesc(e.target.value)}
                        />
                        <select
                            value={selectedUserId}
                            onChange={(e) => setSelectedUserId(e.target.value)}
                            required
                        >
                            <option value="">Select Assignee</option>
                            {users.map(u => (
                                <option key={u.id} value={u.id}>{u.custom_username} ({u.role})</option>
                            ))}
                        </select>
                        <button type="submit" className="primary-button">Assign Task</button>
                    </form>
                </section>

                <section className="tasks-section">
                    {tasks.length === 0 ? (
                        <div className="empty-state">
                            <p>No tasks found.</p>
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
                                            <small>Assigned to User ID: {task.assignee_id}</small>
                                        </div>
                                    </div>
                                    <button
                                        className="delete-button"
                                        onClick={() => handleDeleteTask(task.id)}
                                        aria-label="Delete Task"
                                    >
                                        ×
                                    </button>
                                </div>
                            ))}
                        </div>
                    )}
                </section>
            </main>
        </div>
    );
}

export default AdminDashboard;
