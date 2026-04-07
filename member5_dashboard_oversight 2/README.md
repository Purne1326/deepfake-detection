# Member 5 — Oversight Dashboard

Human control and accountability layer over the non-consensual content detection pipeline.

## How to Run

    pip install -r requirements.txt
    export DATABASE_URL="postgresql://user:pass@localhost/nonconsent_detection"
    export MEMBER4_BASE_URL="http://member4-service:8004"
    streamlit run app.py --server.port 8005

## How to Run Tests

    cd member5_dashboard_oversight
    python -m pytest tests/ -v

## Default Credentials

| Username  | Password     | Role     |
|-----------|--------------|----------|
| admin     | 1234         | admin    |
| reviewer1 | Review@001!  | reviewer |
| reviewer2 | Review@002!  | reviewer |
| reviewer3 | Review@003!  | reviewer |
| reviewer4 | Review@004!  | reviewer |

Change all default passwords before deployment via environment variables.

## Architecture

    app.py               <- Streamlit entry point + CSS + nav
    authentication.py    <- Login page, session state, PBKDF2-SHA256 verify
    access_control.py    <- RBAC: can(action) helper + permission matrix
    data_access.py       <- PostgreSQL queries (detection_cases + audit_logs)
    member4_client.py    <- HTTP client for Member 4 approve/reject/retry
    dashboard_routes.py  <- All 6 page renderers
    tests/
      test_auth.py       <- 11 auth unit tests
      test_dashboard.py  <- 10 RBAC + data safety tests
