# ScamReport

A platform for reporting, validating, and providing information about online scams - built around a Telegram bot, REST API, and administration panel.

The system is implemented according to the Product Design Document (PDD), using a layered, object-oriented architecture:

```text
Repository Layer  → Raw data access (SQLAlchemy Async)
Service Layer     → Business logic (Trust Score, State Machine, deduplication, ...)
API Layer         → FastAPI (administration panel / external integrations)
Bot Layer         → Aiogram 3 (end-user interaction with FSM)
````

## Project Structure

```text
scamreport/
├── app/
│   ├── core/                    # Configuration, database, security (JWT), exceptions, logging
│   ├── models/                  # SQLAlchemy 2.0 ORM models + domain enums
│   ├── schemas/                 # Pydantic API request/response schemas
│   ├── repositories/            # Repository pattern - data access abstraction
│   ├── services/                # Business logic - core domain layer
│   ├── api/
│   │   ├── deps.py              # Central FastAPI dependency injection
│   │   └── v1/                  # Version 1 API routers
│   ├── bot/
│   │   ├── handlers/             # Aiogram handlers (start, report_flow, search, profile)
│   │   ├── states/               # FSM states for the reporting workflow
│   │   ├── keyboards/            # Inline and reply keyboards
│   │   ├── container.py          # Service factory outside FastAPI DI
│   │   └── bot.py                # Bot entry point (Long Polling)
│   └── main.py                   # FastAPI entry point
├── migrations/                   # Alembic migrations (Async)
├── scripts/                      # One-off scripts (category seeding, super admin creation)
├── tests/                        # Unit tests (pytest + pytest-asyncio)
├── deploy/                       # Nginx and Prometheus configuration
├── docker-compose.yml             # API + Bot + Postgres + Redis + MinIO + Nginx + Prometheus + Grafana
├── Dockerfile
├── requirements.txt
└── .env.example
```

## Running with Docker Compose

```bash
cp .env.example .env

# Configure BOT_TOKEN, passwords, and SECRET_KEY in .env

docker compose up -d --build

docker compose run --rm migrator
docker compose run --rm api python -m scripts.seed_categories
docker compose run --rm api python -m scripts.bootstrap_super_admin <YOUR_TELEGRAM_ID>
```

Once the services are running:

| Service               | URL                                                      |
| --------------------- | -------------------------------------------------------- |
| API (Swagger)         | [http://localhost:8000/docs](http://localhost:8000/docs) |
| Nginx (Reverse Proxy) | [http://localhost](http://localhost)                     |
| Prometheus            | [http://localhost:9090](http://localhost:9090)           |
| Grafana               | [http://localhost:3000](http://localhost:3000)           |
| MinIO Console         | [http://localhost:9001](http://localhost:9001)           |

The bot runs independently using Long Polling through the `bot` service, so it does not require an exposed inbound port.

## Local Development

The application can also be run without Docker:

```bash
python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

cp .env.example .env
# Update DATABASE_URL and REDIS_URL to point to localhost

alembic upgrade head

python -m scripts.seed_categories

# Run the API
uvicorn app.main:app --reload

# Run the bot in a separate terminal
python -m app.bot.bot
```

## Tests

```bash
pytest -v
```

## Case Status State Machine

```text
REGISTERED
     ↓
PENDING_REVIEW
     ↓
UNDER_REVIEW
     ├──→ NEEDS_MORE_EVIDENCE
     │
     ├──→ REJECTED ──→ PENDING_REVIEW
     │
     └──→ APPROVED
              ↓
          ARCHIVED
```

Invalid state transitions are blocked by `CaseStatus.allowed_transitions()`.

Every status change is recorded in the `review_history` table, providing a complete review trail and improving auditability.

## Legal & Privacy Considerations

Several privacy and safety mechanisms are implemented directly in the codebase:

* Card numbers are masked by `PIIMaskingService` before being exposed publicly. Raw values are available only to the review team.
* A case can only be publicly published through `CaseService.publish()` when its status is `APPROVED` **and** it has at least the configured number of independent reporters (`MIN_INDEPENDENT_REPORTERS_TO_PUBLISH`, default: `2`). This helps reduce the risk of retaliatory, malicious, or bad-faith reports.
* Sensitive administrator actions such as approval, rejection, publication, and blocking are recorded in an immutable, append-only `AuditLog`.
* Case review status (`CaseStatus`) is kept separate from publication status (`PublishStatus`). This prevents the system from treating a report as a definitive declaration of guilt merely because information has been submitted or reviewed.
* This project provides technical infrastructure only. Public deployment of such a system - especially when publishing information that may identify individuals - requires legal review appropriate to the jurisdiction where the system operates, particularly regarding defamation, privacy, and data protection.

## Security Considerations for Sensitive Data

The following fields in the `reports` table currently contain raw sensitive values:

```text
subject_card_number
subject_phone_number
```

They are stored in plaintext because the review team requires access to the original values for validation.

For production deployments, **these fields must be protected with additional security controls**:

1. Enable column-level encryption, for example using PostgreSQL `pgcrypto` or a solution such as `sqlalchemy-utils` `EncryptedType`.

2. Restrict access to sensitive columns at the database level using appropriate roles and Row-Level Security (RLS).

3. Store `SECRET_KEY`, database credentials, MinIO credentials, and other secrets in a dedicated Secret Manager such as Vault or AWS Secrets Manager rather than keeping production secrets in `.env` files.

> **Important:** The current implementation should not be considered production-ready until appropriate encryption, access controls, secret management, monitoring, and legal requirements have been addressed.
```
```
