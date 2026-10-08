from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.routers import (
    auth,
    events,
    bookings,
    tickets,
    notifications,
)

from app.utils.dependencies import (
    require_user,
    require_organizer,
    require_admin,
)


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="SmartEvent API",
    description="Event Discovery & Ticket Booking System",
    version="1.0.0",
)


# ============================================================
# CORS CONFIGURATION
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# STATIC FILES
# ============================================================

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static",
)


# ============================================================
# ROUTERS
# ============================================================

app.include_router(
    auth.router
)

app.include_router(
    events.router
)

app.include_router(
    bookings.router
)

app.include_router(
    tickets.router
)

app.include_router(
    notifications.router
)


# ============================================================
# RBAC TEST ENDPOINTS
# ============================================================

@app.get(
    "/test/user-access",
    tags=["RBAC Test"],
)
def test_user_access(
    current_user=Depends(require_user),
):
    return {
        "message": "USER access granted",
        "user_id": current_user.id,
        "username": current_user.username,
        "role": current_user.role,
    }


@app.get(
    "/test/organizer-access",
    tags=["RBAC Test"],
)
def test_organizer_access(
    current_user=Depends(require_organizer),
):
    return {
        "message": "ORGANIZER access granted",
        "user_id": current_user.id,
        "username": current_user.username,
        "role": current_user.role,
    }


@app.get(
    "/test/admin-access",
    tags=["RBAC Test"],
)
def test_admin_access(
    current_user=Depends(require_admin),
):
    return {
        "message": "ADMIN access granted",
        "user_id": current_user.id,
        "username": current_user.username,
        "role": current_user.role,
    }


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():
    return {
        "message": "Welcome to SmartEvent API",
        "status": "running",
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }