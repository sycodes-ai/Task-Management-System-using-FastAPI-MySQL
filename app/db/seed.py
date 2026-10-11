import logging

from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.models.task import Task
from app.models.user import User

logger = logging.getLogger(__name__)

DEMO_USERS = [
    # (username, email, password, role)
    ("demo_admin", "admin@demo.com", "Admin123!", "admin"),
    ("demo_staff", "staff@demo.com", "Staff123!", "staff"),
    ("alex", "alex@demo.com", "Staff123!", "staff"),
]

DEMO_TASKS = [
    # (title, description, status, assignee email)
    ("Prepare Q4 sales report", "Collect regional figures and summarise them for the board meeting.", "in_progress", "staff@demo.com"),
    ("Fix login page bug", "Users on Safari are redirected back to the login page after signing in.", "pending", "staff@demo.com"),
    ("Update customer FAQ", "Add answers about the new refund policy and delivery times.", "completed", "staff@demo.com"),
    ("Onboard new support agent", "Set up accounts and walk through the ticket workflow.", "pending", "staff@demo.com"),
    ("Review vendor contracts", "Check renewal dates and flag contracts that expire this quarter.", "in_progress", "alex@demo.com"),
    ("Plan team offsite", "Book a venue and send the agenda for the March offsite.", "pending", "alex@demo.com"),
    ("Migrate invoices to new system", "Export 2023 invoices and verify totals after import.", "completed", "alex@demo.com"),
    ("Write release notes for v2.1", "Summarise new features and known issues for customers.", "completed", "alex@demo.com"),
    ("Audit user permissions", "Remove access for accounts that have been inactive for 90 days.", "in_progress", "alex@demo.com"),
    ("Respond to partner enquiry", "Reply to the partnership request received on Monday.", "pending", "staff@demo.com"),
]

def seed_demo_data(db: Session) -> bool:
    """Create demo users and tasks if the users table is empty. Returns True if data was created."""
    if db.query(User.id).first() is not None:
        return False

    users = {}
    for username, email, password, role in DEMO_USERS:
        user = User(
            custom_username=username,
            email=email,
            hashed_password=get_password_hash(password),
            role=role,
        )
        db.add(user)
        users[email] = user
    db.flush()

    admin = users["admin@demo.com"]
    for title, description, status, assignee_email in DEMO_TASKS:
        db.add(Task(
            title=title,
            description=description,
            status=status,
            assignee_id=users[assignee_email].id,
            assigned_by_id=admin.id,
        ))
    db.commit()
    logger.info("Seeded demo data: %d users, %d tasks", len(DEMO_USERS), len(DEMO_TASKS))
    return True
