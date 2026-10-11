import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';
import { STATUS_OPTIONS, getErrorMessage } from '../utils';
import { useTaskQuery, useTaskData } from '../hooks/useTasks';
import TaskToolbar from './TaskToolbar';
import StatCards from './StatCards';
import Pagination from './Pagination';

function StaffDashboard({ user }) {
    const navigate = useNavigate();
    const [actionError, setActionError] = useState('');
    const [updatingId, setUpdatingId] = useState(null);

    const { query, setStatus, setPage } = useTaskQuery();
    const { tasks, total, stats, error, loading, initialLoading, reload } = useTaskData(query);

    const handleStatusChange = async (task, newStatus) => {
        setActionError('');
        setUpdatingId(task.id);
        try {
            // Staff may only change the status
            await api.put(`/tasks/${task.id}`, { status: newStatus });
            reload();
        } catch (err) {
            setActionError(getErrorMessage(err, 'Failed to update task status'));
        } finally {
            setUpdatingId(null);
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
                <StatCards stats={stats} />
                <TaskToolbar status={query.status} onStatusChange={setStatus} />

                {(error || actionError) && (
                    <div className="error-message" role="alert">{error || actionError}</div>
                )}

                <section className="tasks-section" aria-busy={loading}>
                    {initialLoading ? (
                        <div className="empty-state"><p>Loading tasks...</p></div>
                    ) : tasks.length === 0 ? (
                        <div className="empty-state">
                            <p>{query.status ? 'No tasks match this filter.' : 'You have no tasks assigned yet.'}</p>
                        </div>
                    ) : (
                        <div className={`task-grid ${loading ? 'refreshing' : ''}`}>
                            {tasks.map(task => (
                                <div key={task.id} className={`task-card ${task.status === 'completed' ? 'completed' : ''}`}>
                                    <div className="task-content">
                                        <div className="task-status-control">
                                            <select
                                                value={task.status}
                                                onChange={(e) => handleStatusChange(task, e.target.value)}
                                                disabled={updatingId === task.id}
                                                aria-label={`Status of ${task.title}`}
                                                className={`status-select ${task.status}`}
                                            >
                                                {STATUS_OPTIONS.map(o => (
                                                    <option key={o.value} value={o.value}>{o.label}</option>
                                                ))}
                                            </select>
                                        </div>
                                        <div className="task-text">
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

                <Pagination page={query.page} total={total} onPageChange={setPage} disabled={loading} />
            </main>
        </div>
    );
}

export default StaffDashboard;
