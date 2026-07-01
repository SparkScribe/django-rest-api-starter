# Django REST API Starter

![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)
![Django 5](https://img.shields.io/badge/Django-5+-092E20.svg)
![DRF](https://img.shields.io/badge/DRF-3.15+-a30000.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791.svg)
![Docker](https://img.shields.io/badge/Docker-ready-2496ED.svg)

A compact Django REST Framework service showing patterns I use on production backends: JWT auth, pagination, filtering, OpenAPI docs, Docker, and pytest.

Domain: simple order-management API (customers, orders, line items).

## Features

- Django 5 + Django REST Framework
- JWT authentication (simplejwt)
- Paginated list endpoints with django-filter
- OpenAPI schema via drf-spectacular (Swagger UI)
- Split settings (base / local / production)
- Docker Compose (web + PostgreSQL)
- pytest-django tests

## Quick start

```bash
git clone https://github.com/sparkscribe/django-rest-api-starter.git
cd django-rest-api-starter
cp .env.example .env
docker compose up --build
# Swagger: http://localhost:8000/api/schema/swagger-ui/
```

Create a user for JWT login:

```bash
docker compose exec web python manage.py createsuperuser
```

## API overview

| Method | Endpoint | Auth | Notes |
|--------|----------|------|-------|
| GET | `/api/v1/health/` | No | Health check |
| POST | `/api/v1/auth/token/` | No | Obtain JWT pair |
| POST | `/api/v1/auth/token/refresh/` | No | Refresh access token |
| GET | `/api/v1/customers/` | Yes | Paginated list |
| POST | `/api/v1/customers/` | Yes | Create customer |
| GET | `/api/v1/customers/{id}/` | Yes | Customer detail |
| GET | `/api/v1/orders/` | Yes | Paginated; filter `?status=` `?customer_id=` |
| POST | `/api/v1/orders/` | Yes | Create with nested line items |
| GET | `/api/v1/orders/{id}/` | Yes | Order detail |
| PATCH | `/api/v1/orders/{id}/` | Yes | Status transitions only |
| GET | `/api/schema/swagger-ui/` | No | OpenAPI docs |

## Local development (without Docker)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Run tests:

```bash
pytest
```

## Project layout

```
config/settings/     # base, local, production
apps/accounts/       # JWT routes, health check
apps/orders/         # customers, orders, line items
tests/               # pytest-django
```

## Production notes

- Settings are split under `config/settings/` — use `DJANGO_SETTINGS_MODULE=config.settings.production` in deploy.
- All API endpoints except `/health/` and schema docs require a valid JWT.
- Order list view uses `select_related("customer")` and `prefetch_related("items")` to avoid N+1 queries.
- Status changes follow a fixed transition map (draft → paid/cancelled, paid → shipped/cancelled).
- For background jobs (email, webhooks), add Celery as a separate worker service — not included here to keep the starter small.

## Author

Ankit Vaghani — [SparkScribe Technologies](https://github.com/sparkscribe)

See also: [fastapi-production-api-starter](https://github.com/sparkscribe/fastapi-production-api-starter)
