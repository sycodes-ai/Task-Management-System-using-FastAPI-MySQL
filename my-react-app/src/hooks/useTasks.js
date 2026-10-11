import { useCallback, useEffect, useRef, useState } from 'react';
import api from '../api';
import { PAGE_SIZE, SEARCH_DEBOUNCE_MS, getErrorMessage } from '../utils';

// Status filter, search text and page for a task list.
// Changing the filter or the search always goes back to page 1, and the
// search only reaches the API after the user stops typing for a moment.
export function useTaskQuery() {
    const [query, setQuery] = useState({ status: '', q: '', page: 1 });
    const [searchInput, setSearchInput] = useState('');
    const timer = useRef(null);

    useEffect(() => {
        const pending = timer;
        return () => clearTimeout(pending.current);
    }, []);

    const setStatus = useCallback((status) => {
        setQuery(prev => ({ ...prev, status, page: 1 }));
    }, []);

    const setSearch = useCallback((value) => {
        setSearchInput(value);
        clearTimeout(timer.current);
        timer.current = setTimeout(() => {
            const q = value.trim();
            setQuery(prev => (prev.q === q ? prev : { ...prev, q, page: 1 }));
        }, SEARCH_DEBOUNCE_MS);
    }, []);

    const setPage = useCallback((page) => {
        setQuery(prev => ({ ...prev, page }));
    }, []);

    return { query, searchInput, setStatus, setSearch, setPage };
}

// Loads one page of tasks (with the total from X-Total-Count) and the stats.
export function useTaskData(query) {
    const [reloadToken, setReloadToken] = useState(0);
    const [list, setList] = useState({ key: null, tasks: [], total: 0, error: '' });
    const [stats, setStats] = useState(null);
    const [statsError, setStatsError] = useState('');

    const { status, q, page } = query;
    const key = `${status}|${q}|${page}|${reloadToken}`;

    useEffect(() => {
        let cancelled = false;
        const params = { skip: (page - 1) * PAGE_SIZE, limit: PAGE_SIZE };
        if (status) params.status = status;
        if (q) params.q = q;
        api.get('/tasks/', { params })
            .then(({ data, headers }) => {
                if (!cancelled) {
                    setList({ key, tasks: data, total: Number(headers['x-total-count']) || 0, error: '' });
                }
            })
            .catch((err) => {
                if (!cancelled) {
                    setList({ key, tasks: [], total: 0, error: getErrorMessage(err, 'Failed to load tasks') });
                }
            });
        return () => { cancelled = true; };
    }, [key, status, q, page]);

    useEffect(() => {
        let cancelled = false;
        api.get('/tasks/stats')
            .then(({ data }) => {
                if (!cancelled) {
                    setStats(data);
                    setStatsError('');
                }
            })
            .catch((err) => {
                if (!cancelled) setStatsError(getErrorMessage(err, 'Failed to load task stats'));
            });
        return () => { cancelled = true; };
    }, [reloadToken]);

    const reload = useCallback(() => setReloadToken(n => n + 1), []);

    return {
        tasks: list.tasks,
        total: list.total,
        stats,
        error: list.error || statsError,
        loading: list.key !== key,
        initialLoading: list.key === null,
        reload,
    };
}
