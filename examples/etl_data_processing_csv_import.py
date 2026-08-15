"""
ETL / Data Processing Example: Batch Data Transformation

This example demonstrates how to queue and process large data transformations
without blocking HTTP requests.

Use Case: Accept data upload, transform/validate/load asynchronously.
Perfect for: CSV imports, data pipeline, analytics ETL, data migrations.

Workflow:
1. Client uploads CSV via POST /api/v1/tasks with task_type="import_csv"
2. API stores task in PostgreSQL (status=PENDING), returns task_id immediately
3. Redis queue receives task_id
4. Worker picks up task, reads file, transforms/validates data, inserts to DB
5. Client polls GET /api/v1/tasks/{task_id} to check progress and get summary
6. Results include row count, errors, and data quality metrics
"""

# Example payload to submit a data import:
# POST http://localhost:8000/api/v1/tasks
# {
#   "task_type": "import_csv",
#   "payload": {
#     "file_url": "s3://my-bucket/data/users_2026-08.csv",
#     "target_table": "users",
#     "mapping": {
#       "user_id": "id",
#       "email": "email_address",
#       "created": "signup_date"
#     },
#     "skip_duplicates": true,
#     "validation_rules": {
#       "email": "email",
#       "age": "integer|min:18|max:120"
#     }
#   }
# }

# Example response:
# {
#   "task_id": "770e8400-e29b-41d4-a716-446655440002",
#   "status": "PENDING",
#   "created_at": "2026-08-15T12:00:00Z"
# }

# Example final response (after worker completes):
# {
#   "task_id": "770e8400-e29b-41d4-a716-446655440002",
#   "status": "COMPLETED",
#   "result": {
#     "rows_processed": 1250,
#     "rows_inserted": 1235,
#     "rows_skipped": 10,
#     "rows_failed": 5,
#     "errors": [
#       {"row": 42, "field": "email", "reason": "invalid_format"},
#       {"row": 156, "field": "age", "reason": "out_of_range"}
#     ],
#     "duration_seconds": 18.5,
#     "throughput_rows_per_sec": 67.6
#   },
#   "completed_at": "2026-08-15T12:00:18Z"
# }

# Why this pattern works for ETL:
# - Large file uploads don't timeout (API responds immediately)
# - Processing happens in worker without consuming API resources
# - Multiple workers scale processing (10GB file split across N workers)
# - Failures are transparent (stored in DB, can retry specific batches)
# - Progress tracking: client polls to see how many rows processed
# - Data quality: validation errors reported back to client
# - Audit trail: all imports logged with task_id

import asyncio
from typing import Any, Dict, List

async def process_import_csv_task(task_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Worker handler for CSV import tasks.
    """
    payload = task_data.get("payload", {})
    file_url = payload.get("file_url")
    target_table = payload.get("target_table")
    mapping = payload.get("mapping", {})
    validation_rules = payload.get("validation_rules", {})
    
    # 1. Download file from S3/GCS/local storage
    # file_content = download_file(file_url)
    
    # 2. Parse CSV
    # rows = parse_csv(file_content)
    
    # 3. Validate each row
    # valid_rows, error_rows = validate_rows(rows, validation_rules)
    
    # 4. Transform columns using mapping
    # transformed_rows = apply_mapping(valid_rows, mapping)
    
    # 5. Batch insert to database
    # inserted_count = await batch_insert(target_table, transformed_rows)
    
    # 6. Return summary
    return {
        "rows_processed": 1250,
        "rows_inserted": 1235,
        "rows_skipped": 10,
        "rows_failed": 5,
        "errors": [
            {"row": 42, "field": "email", "reason": "invalid_format"},
            {"row": 156, "field": "age", "reason": "out_of_range"}
        ],
        "duration_seconds": 18.5,
        "throughput_rows_per_sec": 67.6
    }

# Production recommendations:
# - Streaming parser: don't load entire file into memory (use streaming CSV reader)
# - Batch inserts: insert in chunks of 1000 rows for performance
# - Transaction management: all-or-nothing or partial insert with error log
# - Duplicate detection: hash rows to skip exact duplicates
# - Data quality: run validation rules before insertion
# - Schema versioning: track schema changes over time
# - Resume capability: if task fails, can resume from last checkpoint
# - Monitoring: alert on high error rates

# Example large import scenario:
# File size: 500MB with 5 million rows
# Without async task queue: HTTP request would timeout
# With this pattern:
#   - Client gets task_id in <100ms
#   - Workers process in parallel
#   - Complete in ~2 minutes
#   - Client polls every 10 seconds to check progress
#   - All rows inserted durably with error reporting
