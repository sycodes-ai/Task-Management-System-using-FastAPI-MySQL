import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';

function Dashboard() {
    const [tasks, setTasks] = useState([]);
    const [newTaskTitle, setNewTaskTitle] = useState('');
    const [newTaskDesc, setNewTaskDesc] = useState('');
    const [user, setUser] = useState(null);
    const navigate = useNavigate();

    useEffect(() => {
        fetchUser();
        fetchTasks();
    }, []);

    const fetchUser = async () => {
        try {
            const { data } = await api.get('/users/me');
            setUser(data);
        } catch (err) {
            handleLogout();
        }
    };

    const fetchTasks = async () => {
        try {
            const { data } = await api.get('/tasks/');
            setTasks(data);
        } catch (err) {
            console.error('Failed to fetch tasks', err);
        }
    };

    const handleCreateTask = async (e) => {
        e.preventDefault();
        if (!newTaskTitle.trim()) return;
        try {
            await api.post('/tasks/', { title: newTaskTitle, description: newTaskDesc });
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
                completed: !task.completed
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
                    <h1>Task Board</h1>
                    <div className="user-controls">
                        <span className="user-greeting">Hello, {user?.custom_username}</span>
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
                        <button type="submit" className="primary-button">Add Task</button>
                    </form>
                </section>

                <section className="tasks-section">
                    {tasks.length === 0 ? (
                        <div className="empty-state">
                            <p>No tasks yet. Create one above!</p>
                        </div>
                    ) : (
                        <div className="task-grid">
                            {tasks.map(task => (
                                <div key={task.id} className={`task-card ${task.completed ? 'completed' : ''}`}>
                                    <div className="task-content" onClick={() => handleToggleTask(task)}>
                                        <div className="checkbox-wrapper">
                                            <div className={`custom-checkbox ${task.completed ? 'checked' : ''}`}></div>
                                        </div>
                                        <div>
                                            <h3>{task.title}</h3>
                                            {task.description && <p>{task.description}</p>}
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

export default Dashboard;
