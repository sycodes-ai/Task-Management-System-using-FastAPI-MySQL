import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';
import { STATUS_OPTIONS, getErrorMessage } from '../utils';
import { useTaskQuery, useTaskData } from '../hooks/useTasks';
import TaskToolbar from './TaskToolbar';
import StatCards from './StatCards';
import Pagination from './Pagination';

function AdminDashboard({ user }) {
    const [users, setUsers] = useState([]);
    const [usersError, setUsersError] = useState('');
    const [newTaskTitle, setNewTaskTitle] = useState('');
    const [newTaskDesc, setNewTaskDesc] = useState('');
    const [selectedUserId, setSelectedUserId] = useState('');
    const [creating, setCreating] = useState(false);
    const [actionError, setActionError] = useState('');
    const navigate = useNavigate();

    const { query, searchInput, setStatus, setSearch, setPage } = useTaskQuery();
    const { tasks, total, stats, error, loading, initialLoading, reload } = useTaskData(query);

    // Editing State
    const [editingTaskId, setEditingTaskId] = useState(null);
    const [editFormData, setEditFormData] = useState({});
    const [saving, setSaving] = useState(false);

    // Delete confirmation State
    const [confirmDeleteId, setConfirmDeleteId] = useState(null);

    useEffect(() => {
        let cancelled = false;
        api.get('/users/')
            .then(({ data }) => {
                if (cancelled) return;
                setUsers(data);
                if (data.length > 0) {
                    setSelectedUserId(data[0].id);
                }
            })
            .catch((err) => {
                if (!cancelled) setUsersError(getErrorMessage(err, 'Failed to load users'));
            });
        return () => { cancelled = true; };
    }, []);

    const handleCreateTask = async (e) => {
        e.preventDefault();
        if (!newTaskTitle.trim() || !selectedUserId) return;
        setActionError('');
        setCreating(true);
        try {
            await api.post('/tasks/', {
                title: newTaskTitle,
                description: newTaskDesc.trim() || null,
                assignee_id: parseInt(selectedUserId)
            });
            setNewTaskTitle('');
            setNewTaskDesc('');
            setPage(1);
            reload();
        } catch (err) {
            setActionError(getErrorMessage(err, 'Failed to create task'));
        } finally {
            setCreating(false);
        }
    };

    const handleDeleteTask = async (id) => {
        setActionError('');
        try {
            await api.delete(`/tasks/${id}`);
            setConfirmDeleteId(null);
            // Deleting the last task on a page moves back one page
            if (tasks.length === 1 && query.page > 1) {
                setPage(query.page - 1);
            }
            reload();
        } catch (err) {
            setConfirmDeleteId(null);
            setActionError(getErrorMessage(err, 'Failed to delete task'));
        }
    };

    const startEditing = (task) => {
        setConfirmDeleteId(null);
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
        setActionError('');
        setSaving(true);
        try {
            await api.put(`/tasks/${id}`, {
                title: editFormData.title,
                description: editFormData.description,
                status: editFormData.status,
                assignee_id: parseInt(editFormData.assignee_id)
            });
            setEditingTaskId(null);
            reload();
        } catch (err) {
            setActionError(getErrorMessage(err, 'Failed to update task'));
        } finally {
            setSaving(false);
        }
    };

    const handleLogout = () => {
        localStorage.removeItem('token');
        navigate('/login');
    };

    const filtersActive = Boolean(query.status || query.q);

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
                <StatCards stats={stats} />

                <section className="create-task-section">
                    <form className="create-task-form" onSubmit={handleCreateTask}>
                        <input
                            type="text"
                            placeholder="What needs to be done?"
                            value={newTaskTitle}
                            onChange={(e) => setNewTaskTitle(e.target.value)}
                            maxLength={100}
                            required
                        />
                        <input
                            type="text"
                            placeholder="Details (optional)"
                            value={newTaskDesc}
                            onChange={(e) => setNewTaskDesc(e.target.value)}
                            maxLength={255}
                        />
                        <select
                            value={selectedUserId}
                            onChange={(e) => setSelectedUserId(e.target.value)}
                            aria-label="Assignee"
                            required
                        >
                            <option value="">Select Assignee</option>
                            {users.map(u => (
                                <option key={u.id} value={u.id}>{u.custom_username} ({u.role})</option>
                            ))}
                        </select>
                        <button type="submit" className="primary-button" disabled={creating}>
                            {creating ? 'Assigning...' : 'Assign Task'}
                        </button>
                    </form>
                </section>

                <TaskToolbar
                    status={query.status}
                    onStatusChange={setStatus}
                    searchInput={searchInput}
                    onSearchChange={setSearch}
                />

                {(error || usersError || actionError) && (
                    <div className="error-message" role="alert">{error || usersError || actionError}</div>
                )}

                <section className="tasks-section" aria-busy={loading}>
                    {initialLoading ? (
                        <div className="empty-state"><p>Loading tasks...</p></div>
                    ) : tasks.length === 0 ? (
                        <div className="empty-state">
                            <p>{filtersActive ? 'No tasks match your filters.' : 'No tasks found.'}</p>
                        </div>
                    ) : (
                        <div className={`task-grid ${loading ? 'refreshing' : ''}`}>
                            {tasks.map(task => {
                                const isEditing = editingTaskId === task.id;
                                return (
                                    <div key={task.id} className={`task-card ${task.status === 'completed' && !isEditing ? 'completed' : ''}`}>
                                        {isEditing ? (
                                            <div className="edit-task-form">
                                                <input
                                                    type="text"
                                                    name="title"
                                                    aria-label="Title"
                                                    value={editFormData.title}
                                                    onChange={handleEditChange}
                                                    maxLength={100}
                                                    required
                                                />
                                                <input
                                                    type="text"
                                                    name="description"
                                                    aria-label="Description"
                                                    value={editFormData.description}
                                                    onChange={handleEditChange}
                                                    maxLength={255}
                                                />
                                                <select
                                                    name="status"
                                                    aria-label="Status"
                                                    value={editFormData.status}
                                                    onChange={handleEditChange}
                                                >
                                                    {STATUS_OPTIONS.map(o => (
                                                        <option key={o.value} value={o.value}>{o.label}</option>
                                                    ))}
                                                </select>
                                                <select
                                                    name="assignee_id"
                                                    aria-label="Assignee"
                                                    value={editFormData.assignee_id}
                                                    onChange={handleEditChange}
                                                >
                                                    {users.map(u => (
                                                        <option key={u.id} value={u.id}>{u.custom_username}</option>
                                                    ))}
                                                </select>
                                                <div className="edit-actions">
                                                    <button onClick={() => saveEdit(task.id)} className="primary-button small" disabled={saving}>
                                                        {saving ? 'Saving...' : 'Save'}
                                                    </button>
                                                    <button onClick={cancelEditing} className="text-button small">Cancel</button>
                                                </div>
                                            </div>
                                        ) : (
                                            <>
                                                <div className="task-content">
                                                    <div className="task-text">
                                                        <h3>{task.title}</h3>
                                                        {task.description && <p>{task.description}</p>}
                                                        <div className="task-meta">
                                                            <span className={`status-badge ${task.status}`}>{task.status.replace('_', ' ').toUpperCase()}</span>
                                                            <small>Assigned to: {users.find(u => u.id === task.assignee_id)?.custom_username || 'Unknown'}</small>
                                                        </div>
                                                    </div>
                                                </div>
                                                <div className="task-actions">
                                                    {confirmDeleteId === task.id ? (
                                                        <>
                                                            <span className="confirm-text">Are you sure?</span>
                                                            <button className="danger-button" onClick={() => handleDeleteTask(task.id)}>Yes, delete</button>
                                                            <button className="text-button small" onClick={() => setConfirmDeleteId(null)}>Cancel</button>
                                                        </>
                                                    ) : (
                                                        <>
                                                            <button className="edit-button" onClick={() => startEditing(task)}>Edit</button>
                                                            <button
                                                                className="delete-button"
                                                                onClick={() => setConfirmDeleteId(task.id)}
                                                                aria-label={`Delete ${task.title}`}
                                                            >
                                                                Delete
                                                            </button>
                                                        </>
                                                    )}
                                                </div>
                                            </>
                                        )}
                                    </div>
                                )
                            })}
                        </div>
                    )}
                </section>

                <Pagination page={query.page} total={total} onPageChange={setPage} disabled={loading} />
            </main>
        </div>
    );
}

export default AdminDashboard;
