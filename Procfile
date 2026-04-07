dashboard: gunicorn member5_dashboard_oversight.app:app --bind 0.0.0.0:$PORT
social: gunicorn dummy_social_platform.app:app --bind 0.0.0.0:$PORT
public_reporting: gunicorn public_reporting_system.app:app --bind 0.0.0.0:$PORT
orchestrator: python scripts/orchestrator.py
