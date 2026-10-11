export const PAGE_SIZE = 20;
export const SEARCH_DEBOUNCE_MS = 300;

export const STATUS_OPTIONS = [
    { value: 'pending', label: 'Pending' },
    { value: 'in_progress', label: 'In Progress' },
    { value: 'completed', label: 'Completed' },
];

// Turn an axios error into a message that can be shown to the user
export function getErrorMessage(err, fallback) {
    const detail = err.response?.data?.detail;
    if (Array.isArray(detail)) {
        // FastAPI validation errors (422)
        return detail.map(d => `${d.loc.slice(-1)}: ${d.msg}`).join(', ');
    }
    if (typeof detail === 'string') {
        return detail;
    }
    if (!err.response) {
        return 'Cannot reach the server. Please try again.';
    }
    return fallback;
}
