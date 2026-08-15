#!/usr/bin/env bash
set -e

# Start the background worker
python -m app.workers.background_worker
