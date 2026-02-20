from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import users, tasks

app = FastAPI(
    title="Task Management System API",
    description="API for managing users and tasks",
    version="1.0.0"
)

# Configure CORS (Cross-Origin Resource Sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins in development
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.get("/", tags=["Root"])
def root():
    return {"message": "Welcome to the Task Management System API. Visit /docs for documentation."}

# Include API routers
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])
