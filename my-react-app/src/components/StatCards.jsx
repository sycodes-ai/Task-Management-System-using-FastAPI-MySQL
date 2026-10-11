const CARDS = [
    { key: 'total', label: 'Total' },
    { key: 'pending', label: 'Pending' },
    { key: 'in_progress', label: 'In Progress' },
    { key: 'completed', label: 'Completed' },
];

function StatCards({ stats }) {
    return (
        <div className="stat-cards">
            {CARDS.map(card => (
                <div key={card.key} className={`stat-card ${card.key}`}>
                    <span className="stat-value">{stats ? stats[card.key] : '–'}</span>
                    <span className="stat-label">{card.label}</span>
                </div>
            ))}
        </div>
    );
}

export default StatCards;
