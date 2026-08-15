#!/usr/bin/env bash
set -e

# Start uvicorn API server
uvicorn app.main:app --host 127.0.0.1 --port 8000
