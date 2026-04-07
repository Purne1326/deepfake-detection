from sqlalchemy import Column, String, DateTime, JSON, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import os

Base = declarative_base()

class AuditLog(Base):
    __tablename__ = 'audit_logs'
    id = Column(String(36), primary_key=True)
    action_type = Column(String(50))
    platform = Column(String(50))
    post_id = Column(String(100))
    url = Column(String(200))
    reason = Column(String(255))
    status = Column(String(50))
    timestamp = Column(DateTime, default=datetime.utcnow)
    details = Column(JSON)

class ProtectedPerson(Base):
    __tablename__ = 'protected_persons'
    id = Column(String(36), primary_key=True)
    name = Column(String(100), nullable=False)
    handle = Column(String(100), unique=True, nullable=False)
    risk_level = Column(String(20), default="NORMAL") # NORMAL, ELEVATED, HIGH
    onboarded_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(20), default="ACTIVE")

class AuditLogger:
    def __init__(self, db_url=None):
        if db_url is None:
            db_url = os.environ.get("DATABASE_URL", "sqlite:///audit.db")
            
        # Fix for Render: SQLAlchemy requires 'postgresql://' but Render provides 'postgres://'
        if db_url and db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql://", 1)
            
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def log_event(self, action_type, platform, post_id, url, reason, status, details):
        import uuid
        log_entry = AuditLog(
            id=str(uuid.uuid4()),
            action_type=action_type,
            platform=platform,
            post_id=post_id,
            url=url,
            reason=reason,
            status=status,
            timestamp=datetime.utcnow(),
            details=details
        )
        self.session.add(log_entry)
        self.session.commit()
        print(f"Audit log created: {action_type} - {platform}:{post_id} - {status}")

    def log_detection_case(self, packet):
        self.log_event(
            "DETECTION_RECEIVED",
            packet.get("platform"),
            packet.get("post_id"),
            packet.get("post_url"),
            "System logged incoming pipeline case match",
            "RECEIVED",
            packet
        )

    def log_report_prepared(self, packet, details=None):
        self.log_event(
            "REPORT_PREPARED",
            packet.get("platform"),
            packet.get("post_id"),
            packet.get("post_url"),
            "Evidence packet built and written to disk.",
            "PREPARED",
            details or {}
        )

    def log_takedown_requested(self, packet, response):
        self.log_event(
            "TAKEDOWN_REQUESTED",
            packet.get("platform"),
            packet.get("post_id"),
            packet.get("post_url"),
            response.get("reason", "Action initiated based on compliance check."),
            response.get("status", "UNKNOWN"),
            response
        )
        
    def log_error(self, platform, post_id, error_message):
        self.log_event(
            "SYSTEM_ERROR",
            platform,
            post_id,
            "N/A",
            error_message,
            "ERROR",
            {"error": error_message}
        )
