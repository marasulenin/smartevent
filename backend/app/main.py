
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.routers import (
    auth,
    events,
    bookings,
    tickets,
    notifications,
    organizer_analytics,
    admin_analytics,
    payments,
    coupons,
    reviews,
    phase4,
)

from app.utils.dependencies import (
    require_user,
    require_organizer,
    require_admin,
)

app = FastAPI(
    title="SmartEvent API",
    description="Event Discovery & Ticket Booking System",
    version="1.0.0",
)

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

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static",
)

# Existing routers
app.include_router(auth.router)
app.include_router(events.router)
app.include_router(bookings.router)
app.include_router(tickets.router)
app.include_router(notifications.router)
app.include_router(organizer_analytics.router)
app.include_router(payments.router)
app.include_router(coupons.router)
app.include_router(reviews.router)
app.include_router(admin_analytics.router)

# Phase 4: Modules 18–24
app.include_router(phase4.router)


# RBAC test endpoints
@app.get("/test/user-access", tags=["RBAC Test"])
def test_user_access(current_user=Depends(require_user)):
    return {
        "message": "USER access granted",
        "user_id": current_user.id,
        "username": current_user.username,
        "role": current_user.role,
    }


@app.get("/test/organizer-access", tags=["RBAC Test"])
def test_organizer_access(current_user=Depends(require_organizer)):
    return {
        "message": "ORGANIZER access granted",
        "user_id": current_user.id,
        "username": current_user.username,
        "role": current_user.role,
    }


@app.get("/test/admin-access", tags=["RBAC Test"])
def test_admin_access(current_user=Depends(require_admin)):
    return {
        "message": "ADMIN access granted",
        "user_id": current_user.id,
        "username": current_user.username,
        "role": current_user.role,
    }


@app.get("/")
def root():
    return {
        "message": "Welcome to SmartEvent API",
        "status": "running",
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}
