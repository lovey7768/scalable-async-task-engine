# Scalable Async Task Engine

A small, production-style asynchronous task engine built with FastAPI, PostgreSQL and Redis. The project demonstrates how to accept short-lived HTTP requests (submit a job), persist the job reliably, hand the work to a background worker using Redis as a queue, and store results back in PostgreSQL for later retrieval.

This repository was originally developed to run inside Google Colab; the codebase includes an `app/` package and a notebook (`scalable_async_task_engine.ipynb`) that shows end-to-end setup and tests. The implementation in `app/` (reconstructed in the notebook) contains a minimal-but-complete example of the key components you would see in a real microservice.

Why this project exists (motive)

- Many real systems need to handle work that is too slow or unreliable to run inside a single HTTP request/response cycle (long-running processing, external API calls, ML inference, batch jobs).
- This project demonstrates a simple, robust pattern: accept a task synchronously, persist it, and process it asynchronously with a worker. The pattern decouples request handling from task execution, allowing better throughput, reliability, and observability.

The workflow (what happens when you submit a task)

1. Client submits a task via POST /api/v1/tasks with a JSON payload describing the job.
2. The FastAPI server creates a Task row in PostgreSQL with status PENDING and returns the task ID immediately to the client.
3. The server pushes the task ID onto a Redis list (a simple queue) so a background worker can pick it up.
4. A background worker (separate process) blocks on the Redis queue, pops a task ID when available, loads the Task row from PostgreSQL, updates status to PROCESSING, and runs the task's work (in this repo the work is simulated by app/services/ai_engine.py).
5. When the worker finishes, it persists the result to the Task row and marks the task COMPLETED (or FAILED if an error occurred).
6. The client can poll GET /api/v1/tasks/{task_id} to check the status and retrieve results when ready.

Why this pattern matters (importance & real-life value)

- Responsiveness: HTTP endpoints stay fast because heavy work is moved out of the request cycle.
- Reliability: Tasks are durably stored in PostgreSQL, so worker restarts or crashes do not lose work (you can re-enqueue or resume tasks).
- Scalability: Workers can be scaled horizontally (add more worker processes or hosts) and coordinate via Redis. The web layer can be scaled independently from workers.
- Fault isolation: A crashing worker affects only that worker process; the API can continue accepting tasks.
- Flexibility: You can implement different task types (image processing, ML inference, ETL steps, external API orchestration) without changing the request path.

Real-world use cases

- ML/AI inference: Accept user-uploaded data, enqueue model inference, return results when ready (useful for large models or batched inference).
- Email / notification delivery: Queue messages for later sending and reliably store delivery state.
- ETL / data processing pipelines: Offload heavy data transformation jobs to workers and persist results.
- Video/image processing: Transcode or process large media files asynchronously.
- Any long-running or retryable background job where immediate HTTP response is required.

Project structure (annotated)

```
.env.example            # example environment variables
Dockerfile              # container image for the API
docker-compose.yml      # quick dev stack: postgres, redis, api, worker
requirements.txt        # Python deps used in the example
run_server.sh           # helper to run the API locally (uvicorn)
run_worker.sh           # helper to run the worker process
scalable_async_task_engine.ipynb  # Colab notebook that recreates the app and runs tests in Colab
LICENSE
README.md

# The app/ package (created inside the notebook)
app/
  core/                 # configuration and async DB engine (create_async_engine)
  models/               # SQLAlchemy models (Task and TaskStatus enum)
  schemas/              # Pydantic request/response models for validation and responses
  services/             # example AIEngine (simulated analysis) and other business logic
  workers/              # background worker loop that consumes Redis queue and updates tasks
  main.py               # FastAPI entrypoint: submit task, check task, health check
```

How it fits together (runtime shape)

- Requests arrive at `app.main` (FastAPI). The POST endpoint saves a Task (SQLAlchemy + asyncpg) and LPUSHes the task ID to Redis. A separate worker process (`app.workers.background_worker`) BRPOPs from the Redis list, loads the Task by ID, performs the work (calls functions in `app.services`), and writes the results back to PostgreSQL. The API exposes GET /api/v1/tasks/{task_id} so clients can poll for completion.

How to run it (short path)

Prerequisites: Python 3.10+, PostgreSQL 14+, Redis 6+ (or use Docker Compose)

Local (venv)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # edit if necessary
# make sure Postgres and Redis are running and .env values match
./run_server.sh         # runs uvicorn app.main:app
./run_worker.sh         # in another terminal, runs the worker loop
```

With Docker Compose (recommended for quick tests)

```bash
cp .env.example .env
docker-compose up --build
```

Notes, scaling, and next steps

- Persistence: This example stores tasks and results in PostgreSQL (JSON column for results). In production you might archive results to object storage for large payloads.
- Queueing/Visibility: The example uses a simple Redis list as a queue. For at-least-once delivery and better monitoring consider Redis streams, RQ, Celery, or a cloud queue service with visibility timeouts.
- Concurrency: Workers in this repo are single-threaded asyncio processes; you can run multiple worker processes or use a process manager (systemd, supervisord, container orchestrator) to scale.
- Retries & Idempotency: Add retry logic and make task processing idempotent so re-processing does not cause duplicate side effects.
- Observability: Add request/worker metrics, distributed tracing, and structured logs to make production debugging easier.
- Security: Validate and sanitize inputs, secure DB/Redis connections, and configure least-privileged DB users.

Files worth inspecting

- `scalable_async_task_engine.ipynb` — a guided Colab notebook that rebuilds the app files, starts Postgres/Redis in the Colab environment, runs the API and worker, and performs an end-to-end test. It is the best place to see runnable code and an execution trace.
- `app/services/ai_engine.py` — simulated AI/text analysis worker logic.
- `app/workers/background_worker.py` — the worker loop that BRPOP/LPUSH coordination with Redis and performs PostgreSQL updates.

License

MIT
