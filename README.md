# Scalable Async Task Engine

This repository demonstrates a small, production-style asynchronous task engine built with FastAPI, PostgreSQL and Redis. It includes a background worker that consumes task IDs from a Redis queue, runs async "AI" work (a simulated analysis), and stores results in PostgreSQL.

This project was originally developed to run inside Google Colab; the codebase contains the app package in `app/` and a notebook `scalable_async_task_engine.ipynb` which shows end-to-end setup and testing there.

Features
- FastAPI HTTP API for submitting tasks and checking status
- PostgreSQL (asyncpg + SQLAlchemy async) for durable task storage
- Redis queue for-worker coordination
- Background worker that processes tasks asynchronously
- Simple AI simulation module (app/services/ai_engine.py)

Requirements
- Python 3.10+
- PostgreSQL 14+ (or use the provided Docker Compose)
- Redis 6+

Quick start (local, virtualenv)

1. Create and activate a virtual environment

   python -m venv .venv
   source .venv/bin/activate

2. Install dependencies

   pip install -r requirements.txt

3. Copy environment example and edit if needed

   cp .env.example .env

4. Ensure PostgreSQL and Redis are running and .env values match.

   Example (Linux):
   sudo service postgresql start
   sudo service redis-server start

5. Initialize DB tables and start the API server

   # Start the FastAPI app (in one terminal)
   ./run_server.sh

6. Start the background worker (in another terminal)

   ./run_worker.sh

7. Use the API

   - Submit a task (returns task ID): POST /api/v1/tasks
   - Check task status/result: GET /api/v1/tasks/{task_id}
   - Health: GET /health

Docker (recommended for quick test)

1. Make sure Docker and docker-compose are installed.
2. Copy `.env.example` to `.env` and edit if you want to change DB credentials/ports.
3. Start services:

   docker-compose up --build

This brings up postgres, redis, api (uvicorn), and a worker.

Project layout

- app/
  - core/         configuration and database
  - models/       SQLAlchemy models (Task)
  - schemas/      Pydantic request/response models
  - services/     AI simulation and other service logic
  - workers/      background worker(s)
  - main.py       FastAPI application entrypoint

Notes and troubleshooting

- The repository includes a Colab notebook used to demonstrate running everything inside Google Colab. Running locally is recommended for development and production testing.
- If you see connection issues to PostgreSQL, verify host/port/credentials in `.env` and that the DB server is running.
- For Redis connection problems, ensure the Redis server is reachable from the container or host.

License

MIT
