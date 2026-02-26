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

    // Editing State
    const [editingTaskId, setEditingTaskId] = useState(null);
    const [editFormData, setEditFormData] = useState({});

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

    const handleDeleteTask = async (id) => {
        try {
            await api.delete(`/tasks/${id}`);
            fetchTasks();
        } catch (err) {
            console.error('Failed to delete task', err);
        }
    };

    const startEditing = (task) => {
        setEditingTaskId(task.id);
        setEditFormData({
            title: task.title,
            description: task.description || '',
            status: task.status,
            assignee_id: task.assignee_id
        });
    };

    const cancelEditing = () => {
        setEditingTaskId(null);
        setEditFormData({});
    };

    const handleEditChange = (e) => {
        setEditFormData({
            ...editFormData,
            [e.target.name]: e.target.value
        });
    };

    const saveEdit = async (id) => {
        try {
            await api.put(`/tasks/${id}`, {
                title: editFormData.title,
                description: editFormData.description,
                status: editFormData.status,
                assignee_id: parseInt(editFormData.assignee_id)
            });
            setEditingTaskId(null);
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
                            {tasks.map(task => {
                                const isEditing = editingTaskId === task.id;
                                return (
                                    <div key={task.id} className={`task-card ${task.status === 'completed' && !isEditing ? 'completed' : ''}`}>
                                        {isEditing ? (
                                            <div className="edit-task-form">
                                                <input
                                                    type="text"
                                                    name="title"
                                                    value={editFormData.title}
                                                    onChange={handleEditChange}
                                                    required
                                                />
                                                <input
                                                    type="text"
                                                    name="description"
                                                    value={editFormData.description}
                                                    onChange={handleEditChange}
                                                />
                                                <select
                                                    name="status"
                                                    value={editFormData.status}
                                                    onChange={handleEditChange}
                                                >
                                                    <option value="pending">Pending</option>
                                                    <option value="in_progress">In Progress</option>
                                                    <option value="completed">Completed</option>
                                                </select>
                                                <select
                                                    name="assignee_id"
                                                    value={editFormData.assignee_id}
                                                    onChange={handleEditChange}
                                                >
                                                    {users.map(u => (
                                                        <option key={u.id} value={u.id}>{u.custom_username}</option>
                                                    ))}
                                                </select>
                                                <div className="edit-actions">
                                                    <button onClick={() => saveEdit(task.id)} className="primary-button small">Save</button>
                                                    <button onClick={cancelEditing} className="text-button small">Cancel</button>
                                                </div>
                                            </div>
                                        ) : (
                                            <>
                                                <div className="task-content">
                                                    <div>
                                                        <h3>{task.title}</h3>
                                                        {task.description && <p>{task.description}</p>}
                                                        <div className="task-meta">
                                                            <span className={`status-badge ${task.status}`}>{task.status.replace('_', ' ').toUpperCase()}</span>
                                                            <small>Assigned to: {users.find(u => u.id === task.assignee_id)?.custom_username || 'Unknown'}</small>
                                                        </div>
                                                    </div>
                                                </div>
                                                <div className="task-actions">
                                                    <button className="edit-button" onClick={() => startEditing(task)}>Edit</button>
                                                    <button
                                                        className="delete-button"
                                                        onClick={() => handleDeleteTask(task.id)}
                                                        aria-label="Delete Task"
                                                    >
                                                        ×
                                                    </button>
                                                </div>
                                            </>
                                        )}
                                    </div>
                                )
                            })}
                        </div>
                    )}
                </section>
            </main>
        </div>
    );
}

export default AdminDashboard;
