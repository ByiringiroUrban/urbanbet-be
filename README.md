# UrbanBet Backend

Django + PostgreSQL REST API for the UrbanBet sports betting platform.

## Tech Stack

- **Python** 3.11+
- **Django** 5.0
- **Django REST Framework** 3.15
- **PostgreSQL** (via psycopg2)
- **JWT Auth** via `djangorestframework-simplejwt`
- **API Docs** via `drf-spectacular` (Swagger UI)

---

## Project Structure

```
backend/
├── manage.py
├── requirements.txt
├── .env.example
├── urbanbet/           # Django project config
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── users/              # Authentication & user profiles
├── sports/             # Sports, leagues, events, markets
│   └── management/commands/seed_data.py
├── bets/               # Bet placement & history
├── payments/           # Deposits, withdrawals, transactions
├── predictions/        # AI predictions
└── casino/             # Casino games & sessions
```

---

## Setup

### 1. Create & activate a virtual environment

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` with your values:

```env
SECRET_KEY=your-secret-key
DEBUG=True
DB_NAME=urbanbet_db
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432
CORS_ALLOWED_ORIGINS=http://localhost:5173
```

### 4. Create the PostgreSQL database

```sql
CREATE DATABASE urbanbet_db;
```

### 5. Run migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create a superuser (admin)

```bash
python manage.py createsuperuser
```

### 7. Seed initial data

```bash
python manage.py seed_data
```

This populates: sports, countries, leagues, events, markets, predictions, casino games.

### 8. Run the development server

```bash
python manage.py runserver
```

API is available at: `http://localhost:8000/`

---

## API Endpoints

### Auth (`/api/auth/`)

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/auth/register/` | No | Register new user |
| POST | `/api/auth/login/` | No | Login, get JWT tokens |
| POST | `/api/auth/social-login/` | No | Social login (Google/Facebook/Apple) |
| POST | `/api/auth/logout/` | Yes | Invalidate refresh token |
| GET/PUT | `/api/auth/profile/` | Yes | Get / update profile |
| POST | `/api/auth/change-password/` | Yes | Change password |
| DELETE | `/api/auth/delete-account/` | Yes | Deactivate account |
| POST | `/api/auth/token/refresh/` | No | Refresh access token |

### Sports (`/api/sports/`)

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/sports/` | No | List all sports |
| GET | `/api/sports/countries/` | No | List countries |
| GET | `/api/sports/leagues/` | No | List leagues (filter by `sport`, `country`) |
| GET | `/api/sports/events/` | No | List events (filter by `sport`, `league`, `status`, `is_live`) |
| GET | `/api/sports/events/live/` | No | Live events only |
| GET | `/api/sports/events/<id>/` | No | Event detail with markets |
| GET | `/api/sports/events/<id>/markets/` | No | Markets for an event |

### Bets (`/api/bets/`)

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/bets/place/` | Yes | Place a bet |
| GET | `/api/bets/history/` | Yes | User's bet history |
| GET | `/api/bets/<id>/` | Yes | Single bet detail |

### Payments (`/api/payments/`)

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/payments/deposit/` | Yes | Deposit funds |
| POST | `/api/payments/withdraw/` | Yes | Withdraw funds |
| GET | `/api/payments/history/` | Yes | Transaction history |
| GET | `/api/payments/<id>/` | Yes | Single transaction |

### Predictions (`/api/predictions/`)

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/predictions/` | No | All predictions |
| GET | `/api/predictions/featured/` | No | Featured predictions |
| GET | `/api/predictions/<id>/` | No | Single prediction |

### Casino (`/api/casino/`)

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/casino/games/` | No | List games (filter by `category`, `is_new`, `is_popular`) |
| GET | `/api/casino/games/<id>/` | No | Game detail |
| POST | `/api/casino/sessions/start/` | Yes | Start a game session |
| POST | `/api/casino/sessions/<id>/end/` | Yes | End a session |
| POST | `/api/casino/sessions/<id>/spin/` | Yes | Simulate a slot spin |
| GET | `/api/casino/sessions/history/` | Yes | User session history |

### Admin endpoints

All admin endpoints require `IsAdminUser` (staff flag or superuser).

- `GET /api/auth/admin/users/` — list all users
- `PATCH /api/auth/admin/users/<id>/balance/` — adjust balance
- `POST/PATCH/DELETE /api/sports/admin/events/<id>/` — manage events
- `PATCH /api/bets/admin/<id>/status/` — settle a bet (won/lost/cancelled)
- `GET /api/bets/admin/stats/` — wagering statistics
- `GET /api/payments/admin/stats/` — payment statistics
- `POST/PATCH/DELETE /api/predictions/admin/<id>/` — manage predictions
- `POST/PATCH/DELETE /api/casino/admin/games/<id>/` — manage games

---

## API Docs

Interactive Swagger UI: `http://localhost:8000/api/docs/`

---

## Authentication

All protected endpoints require the `Authorization` header:

```
Authorization: Bearer <access_token>
```

Tokens expire after 60 minutes. Use `/api/auth/token/refresh/` with the `refresh` token to get a new access token.

---

## Payment Methods

Supported deposit/withdrawal methods:
- `momo` — MTN Mobile Money (requires `phone_number`)
- `airtel` — Airtel Money (requires `phone_number`)
- `irembo` — Irembo Pay
- `card` — Credit/Debit Card

---

## Currency

The platform supports **RWF** (Rwandan Franc) and **USD**.  
Default exchange rate: `1 USD = 1200 RWF` (configurable via `EXCHANGE_RATE_USD_TO_RWF` in `.env`).
