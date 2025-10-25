SalahkaarPro Backend (Python, FastAPI)

Overview
- Modular microservices scaffold for Auth, API Gateway, and common libs
- MySQL for transactional data, MongoDB available for document/report storage
- Env-driven config; minimal i18n hooks included

Services
- api_gateway: Routes/proxies to underlying services
- services/auth: Registration, login, JWT-based auth
- common: Shared config, DB connectors, i18n, security utils

Quick Start
1) Prerequisites
- Python 3.10+
- MySQL running with DB `salahkaarpro`
- Optional MongoDB at `mongodb://localhost:27017`

2) Setup
- Copy `.env.example` to `.env` and adjust as needed (already prefilled with provided MySQL creds)
- Create and activate a virtual env
  - `python -m venv .venv && .\.venv\Scripts\activate`
- Install dependencies
  - `pip install -r requirements.txt`

3) Run services (separate terminals)
- Auth service: `uvicorn services.auth.main:app --host 0.0.0.0 --port 8001`
- API Gateway: `uvicorn api_gateway.main:app --host 0.0.0.0 --port 8000`

4) Test
- Health: `GET http://localhost:8001/health`, `GET http://localhost:8000/health`
- Register: `POST http://localhost:8001/auth/register`
- Login: `POST http://localhost:8001/auth/login`
- Me: `GET http://localhost:8001/auth/me` with `Authorization: Bearer <token>`

Notes
- Tables auto-create on auth service startup (SQLAlchemy)
- API Gateway currently proxies `/auth/*` to the Auth service
- i18n reads `Accept-Language` (`en`, `hi`) for basic messages