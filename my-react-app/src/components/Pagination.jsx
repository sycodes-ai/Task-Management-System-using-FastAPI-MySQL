import { PAGE_SIZE } from '../utils';

function Pagination({ page, total, onPageChange, disabled = false }) {
    if (total === 0) return null;
    const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));

    return (
        <nav className="pagination" aria-label="Pagination">
            <button
                type="button"
                className="page-button"
                onClick={() => onPageChange(page - 1)}
                disabled={disabled || page <= 1}
            >
                Previous
            </button>
            <span className="page-info">Page {page} of {totalPages} <small>({total} tasks)</small></span>
            <button
                type="button"
                className="page-button"
                onClick={() => onPageChange(page + 1)}
                disabled={disabled || page >= totalPages}
            >
                Next
            </button>
        </nav>
    );
}

export default Pagination;
