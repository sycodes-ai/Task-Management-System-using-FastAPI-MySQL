import { STATUS_OPTIONS } from '../utils';

// Status filter buttons and an optional search box
function TaskToolbar({ status, onStatusChange, searchInput, onSearchChange }) {
    const filters = [{ value: '', label: 'All' }, ...STATUS_OPTIONS];

    return (
        <div className="task-toolbar">
            <div className="filter-group" role="group" aria-label="Filter by status">
                {filters.map(f => (
                    <button
                        key={f.value}
                        type="button"
                        className={`filter-button ${status === f.value ? 'active' : ''}`}
                        aria-pressed={status === f.value}
                        onClick={() => onStatusChange(f.value)}
                    >
                        {f.label}
                    </button>
                ))}
            </div>
            {onSearchChange && (
                <input
                    type="search"
                    className="search-input"
                    placeholder="Search tasks..."
                    aria-label="Search tasks"
                    value={searchInput}
                    onChange={(e) => onSearchChange(e.target.value)}
                />
            )}
        </div>
    );
}

export default TaskToolbar;
