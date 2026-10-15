# SmartEvent – Event Discovery & Ticket Booking System

SmartEvent is a full-stack event discovery and ticket booking application built using **FastAPI, React, SQLAlchemy, SQLite, JWT authentication, Alembic, and QR code generation**.

The application allows users to discover events, register and log in, book tickets, manage bookings, make simulated payments, apply coupons, submit reviews, receive notifications, and access digital tickets with QR codes. It also includes organizer management, analytics, and advanced event discovery features.

**GitHub Repository:** https://github.com/marasulenin/smartevent

---

## Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Installation and Setup](#installation-and-setup)
- [Database Migrations](#database-migrations)
- [API Documentation](#api-documentation)
- [Frontend Pages](#frontend-pages)
- [Project Modules](#project-modules)
- [Security](#security)
- [Booking Flow](#booking-flow)
- [Testing Status](#testing-status)
- [Future Improvements](#future-improvements)
- [Author](#author)

---

## Features

### 1. Authentication and Authorization

- User registration and login
- JWT-based authentication
- Password hashing using `pwdlib`
- Protected backend API endpoints
- Protected frontend routes
- User profile management
- Role-based access control
- User, Organizer, and Admin authorization support
- Bearer token authentication
- Pydantic request validation

### 2. Event Management and Discovery

- Browse available events
- Search events by title
- Filter events by category
- Paginated event listings
- View detailed event information
- Display ticket prices and availability
- Event date and location information
- Organizer event creation and management
- Organizer ownership validation
- Event updates and cancellation
- Event status management
- Admin event deletion

### 3. Ticket Booking

- Book event tickets
- Select ticket quantity
- Maximum 10 tickets per booking
- Automatic total price calculation
- Ticket inventory validation
- Sold-out prevention
- Booking confirmation
- Booking history
- Booking cancellation
- Inventory restoration after cancellation
- Booking ownership validation

### 4. Payments

- Payment records associated with bookings
- Simulated payment processing
- Successful and failed payment outcomes
- Transaction ID generation
- Payment status tracking
- Payment confirmation workflow

> The current payment implementation includes simulation. Live payment processing requires the appropriate payment gateway configuration and verification.

### 5. Coupons and Discounts

- Coupon-related functionality
- Discount application support
- Integration with the booking and payment workflow

### 6. Reviews and Ratings

- Event review functionality
- Rating and review submission support
- Review-related API endpoints

### 7. Digital QR Tickets

- Unique ticket code generation
- QR code generation
- QR image storage
- Ticket listing and details
- QR code display in the frontend
- Ticket ownership validation

### 8. Notifications

- Booking confirmation notifications
- Booking cancellation notifications
- Notification listing
- Unread notification count
- Mark notifications as read
- Notification support for event-related updates

### 9. Organizer Dashboard and Analytics

- Organizer event management
- Create and manage events
- Organizer analytics functionality
- Event-related booking information
- Role-based access to organizer features

### 10. Phase 4 – Advanced Features

Phase 4 introduces the following features:

| Module | Feature |
|---|---|
| 18 | Real-time ticket availability |
| 19 | Personalized event recommendations |
| 20 | Wishlist management |
| 21 | Live event updates |
| 22 | Profile enhancements |
| 23 | Advanced event search filters |
| 24 | AI chatbot interface |

The Phase 4 implementation includes a live availability component, a Phase 4 dashboard, backend routes, schemas, models, and a database migration. End-to-end verification of these features is still in progress.

---

## Technology Stack

### Backend

- Python
- FastAPI
- SQLAlchemy
- SQLite
- Alembic
- Pydantic
- JWT authentication
- `pwdlib`
- QRCode
- Pillow
- Uvicorn

### Frontend

- React
- Vite
- JavaScript
- React Router
- Axios
- CSS

### Development Tools

- Visual Studio Code
- Git
- GitHub
- FastAPI Swagger UI
- PowerShell

---

## Project Structure

```text
smartevent/
│
├── backend/
│   ├── app/
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── event.py
│   │   │   ├── booking.py
│   │   │   ├── ticket.py
│   │   │   ├── notification.py
│   │   │   ├── phase4.py
│   │   │   └── __init__.py
│   │   │
│   │   ├── schemas/
│   │   │   ├── auth.py
│   │   │   ├── event.py
│   │   │   ├── booking.py
│   │   │   ├── ticket.py
│   │   │   ├── notification.py
│   │   │   ├── phase4.py
│   │   │   └── __init__.py
│   │   │
│   │   ├── routers/
│   │   │   ├── auth.py
│   │   │   ├── events.py
│   │   │   ├── bookings.py
│   │   │   ├── tickets.py
│   │   │   ├── notifications.py
│   │   │   ├── phase4.py
│   │   │   └── __init__.py
│   │   │
│   │   ├── utils/
│   │   │   ├── security.py
│   │   │   ├── dependencies.py
│   │   │   └── __init__.py
│   │   │
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── main.py
│   │   └── __init__.py
│   │
│   ├── alembic/
│   │   ├── versions/
│   │   └── env.py
│   ├── alembic.ini
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── EventCard.jsx
│   │   │   ├── Navbar.jsx
│   │   │   └── LiveAvailability.jsx
│   │   ├── context/
│   │   │   └── AuthContext.jsx
│   │   ├── pages/
│   │   │   ├── Login.jsx
│   │   │   ├── Register.jsx
│   │   │   ├── Home.jsx
│   │   │   ├── EventDetails.jsx
│   │   │   ├── BookingConfirmation.jsx
│   │   │   ├── BookingHistory.jsx
│   │   │   ├── Tickets.jsx
│   │   │   ├── Notifications.jsx
│   │   │   └── Phase4Hub.jsx
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   ├── package.json
│   └── ...
│
├── screenshots/
├── .gitignore
└── README.md
```

*Note: The structure above highlights the principal files. Additional modules, routers, models, pages, and migration files may exist in the working repository.*

---

## Installation and Setup

### Prerequisites

Install the following before running SmartEvent:

- Python
- Node.js and npm
- Git

### 1. Clone the repository

```powershell
git clone https://github.com/marasulenin/smartevent.git
cd smartevent
```

### 2. Set up the backend

From the project root:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
cd backend
```

If the virtual environment already exists, activate it instead of creating a new one.

Install the dependencies:

```powershell
python -m pip install fastapi uvicorn sqlalchemy alembic pydantic pydantic-settings python-dotenv python-jose python-multipart email-validator pwdlib qrcode pillow
```

If the project contains a `requirements.txt` file, prefer installing the pinned project dependencies:

```powershell
python -m pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file in the `backend` directory.

Example development configuration:

```env
DATABASE_URL=sqlite:///./smartevent.db

SECRET_KEY=replace-with-a-strong-random-secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

Add any additional variables required by the project's payment or frontend configuration.

**Security:** Never commit real environment files, API keys, passwords, or production secrets to GitHub. Keep `.env` files in `.gitignore`.

### 4. Apply database migrations

From the `backend` directory:

```powershell
python -m alembic upgrade head
```

Check the current migration:

```powershell
python -m alembic current
```

Check for model changes that require a migration:

```powershell
python -m alembic check
```

### 5. Start the backend

From the `backend` directory:

```powershell
python -m uvicorn app.main:app --reload
```

Backend URL:

http://127.0.0.1:8000

Swagger API documentation:

http://127.0.0.1:8000/docs

ReDoc documentation:

http://127.0.0.1:8000/redoc

### 6. Start the frontend

Open a second terminal:

```powershell
cd C:\Users\shyamsundar\smartevent\frontend
npm install
npm run dev
```

Frontend URL:

http://localhost:5173/

For a production build:

```powershell
npm run build
```

---

## API Documentation

The backend uses the `/api/v1` API prefix.

### Authentication

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/v1/auth/register` | Register an account |
| POST | `/api/v1/auth/login` | Log in |
| GET | `/api/v1/auth/profile` | Retrieve the authenticated user's profile |

Protected endpoints require a valid token:

```http
Authorization: Bearer <access_token>
```

### Events

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/v1/events` | List events |
| GET | `/api/v1/events/{event_id}` | Retrieve event details |
| POST | `/api/v1/events` | Create an event |
| PUT | `/api/v1/events/{event_id}` | Update an event |
| PATCH | `/api/v1/events/{event_id}/cancel` | Cancel an event |
| DELETE | `/api/v1/events/{event_id}` | Delete an event, subject to authorization |

Example search:

```http
GET /api/v1/events?search=conference
```

Example category filter:

```http
GET /api/v1/events?category=Tech
```

Example pagination:

```http
GET /api/v1/events?skip=0&limit=10
```

### Bookings

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/v1/bookings` | Create a booking |
| GET | `/api/v1/bookings` | Retrieve booking history |
| GET | `/api/v1/bookings/{booking_id}` | Retrieve booking details |
| PUT | `/api/v1/bookings/{booking_id}/cancel` | Cancel a booking |

Example booking request:

```json
{
  "event_id": 1,
  "ticket_quantity": 2
}
```

The backend calculates the total price and validates ticket availability.

### Tickets

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/v1/tickets/booking/{booking_id}` | Generate tickets for a booking |
| GET | `/api/v1/tickets` | Retrieve the user's tickets |
| GET | `/api/v1/tickets/{ticket_id}` | Retrieve ticket details |

QR code images are served from the application's configured static QR-code directory.

### Notifications

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/v1/notifications` | Retrieve notifications |
| GET | `/api/v1/notifications/unread-count` | Retrieve the unread count |
| PUT | `/api/v1/notifications/{notification_id}/read` | Mark a notification as read |

### Additional Modules

The application also contains payment, coupon, review, organizer analytics, and Phase 4 functionality. Refer to Swagger at `/docs` for the exact routes, request schemas, and response formats registered by the current backend.

---

## Frontend Pages

### Login and Registration

Users can register, log in, and access protected application features.

### Home – Event Discovery

Users can browse events, search by title, filter by category, navigate paginated results, and open event details.

### Event Details

Users can view event information, select a ticket quantity, view the total price, and proceed with booking. The page also includes live ticket availability functionality.

### Booking Confirmation

Displays booking information and confirmation details.

### Booking History

Allows users to view their bookings and access supported cancellation actions.

### Digital