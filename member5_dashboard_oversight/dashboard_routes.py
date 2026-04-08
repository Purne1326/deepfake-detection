from flask import Blueprint, render_template, abort, request
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from sqlalchemy import func
# Real implementation would import AuditLog from Member 4
from member4_automation_compliance.audit_logger import AuditLog, Base, create_engine, sessionmaker
import os
import json

# Ensure uploads directory exists
UPLOAD_FOLDER = "member5_dashboard_oversight/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

bp = Blueprint('dashboard', __name__)

def get_session():
    db_url = os.environ.get("DATABASE_URL", "sqlite:///audit.db") # Matches Member 4
    
    # Fix for Render: SQLAlchemy requires 'postgresql://' but Render provides 'postgres://'
    if db_url and db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
        
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()

@bp.app_context_processor
def inject_global_data():
    """Injects threat level and pending counts into all templates globally."""
    session = get_session()
    pending_logs = session.query(AuditLog).filter_by(status='PENDING_REVIEW').all()
    pending = len(pending_logs)
    
    max_risk = 0
    for log in pending_logs:
        try:
            details = json.loads(log.details) if isinstance(log.details, str) else log.details
            risk = details.get('risk_score', 0) if details else 0
            if risk > max_risk:
                max_risk = risk
        except:
            continue
            
    threat_level = "NORMAL"
    if pending > 0:
        if max_risk > 0.85:
            threat_level = "CRITICAL"
        elif max_risk > 0.5:
            threat_level = "ELEVATED"
        else:
            threat_level = "MONITORING"
            
    return dict(
        threat_level=threat_level, 
        pending=pending,
        datetime=datetime,
        timedelta=timedelta
    )

@bp.route('/')
@bp.route('/dashboard')
@login_required
def index():
    session = get_session()
    recent_logs = session.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(10).all()
    
    total_cases = session.query(AuditLog).filter_by(action_type='DETECTION_RECEIVED').count()
    takedowns = session.query(AuditLog).filter_by(action_type='TAKEDOWN_REQUESTED', status='SUCCESS').count()
    
    # --- Real Graph Data Start ---
    # Aggregate DETECTIONS over the last 15 days
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=14)
    
    daily_counts = session.query(
        func.date(AuditLog.timestamp).label('date'),
        func.count(AuditLog.id).label('count')
    ).filter(
        AuditLog.timestamp >= start_date,
        AuditLog.action_type == 'DETECTION_RECEIVED'
    ).group_by(func.date(AuditLog.timestamp)).all()
    
    counts_map = {str(d.date): d.count for d in daily_counts}
    
    chart_data = []
    for i in range(15):
        d = (start_date + timedelta(days=i)).date()
        chart_data.append(counts_map.get(str(d), 0))
    # --- Real Graph Data End ---

    pending_alerts = session.query(AuditLog).filter_by(status='PENDING_REVIEW').order_by(AuditLog.timestamp.desc()).limit(10).all()

    return render_template('dashboard.html', 
                          logs=recent_logs, 
                          total_cases=total_cases, 
                          takedowns=takedowns,
                          chart_data=chart_data,
                          pending_alerts=pending_alerts)

@bp.route('/alerts')
@login_required
def alerts():
    session = get_session()
    pending_items = session.query(AuditLog).filter_by(status='PENDING_REVIEW').order_by(AuditLog.timestamp.desc()).all()
    return render_template('alerts.html', alerts=pending_items)

@bp.route('/cases')
@login_required
def cases():
    session = get_session()
    all_logs = session.query(AuditLog).filter_by(action_type='DETECTION_RECEIVED').order_by(AuditLog.timestamp.desc()).all()
    
    # Safely parse JSON details for every log to ensure templates can access them
    for log in all_logs:
        if isinstance(log.details, str):
            try:
                import json
                log.details = json.loads(log.details)
            except:
                log.details = {}
        elif log.details is None:
            log.details = {}
            
    return render_template('cases.html', cases=all_logs)

from member4_automation_compliance.audit_logger import AuditLog, ProtectedPerson, Base, create_engine, sessionmaker
import uuid

@bp.route('/access', methods=['GET', 'POST'])
@login_required
def access():
    session = get_session()
    
    if request.method == 'POST':
        name = request.form.get('name')
        handle = request.form.get('handle')
        risk = request.form.get('risk_level', 'NORMAL')
        
        if name and handle:
            new_person = ProtectedPerson(
                id=str(uuid.uuid4()),
                name=name,
                handle=handle,
                risk_level=risk
            )
            session.add(new_person)
            session.commit()
            
    persons = session.query(ProtectedPerson).order_by(ProtectedPerson.onboarded_at.desc()).all()
    return render_template('access.html', persons=persons)

@bp.route('/remove-protection/<person_id>', methods=['POST'])
@login_required
def remove_protection(person_id):
    session = get_session()
    person = session.query(ProtectedPerson).filter_by(id=person_id).first()
    if person:
        session.delete(person)
        session.commit()
    from flask import redirect, url_for
    return redirect(url_for('dashboard.access'))

@bp.route('/audit')
@login_required
def audit():
    session = get_session()
    all_logs = session.query(AuditLog).order_by(AuditLog.timestamp.desc()).all()
    return render_template('audit.html', logs=all_logs)

@bp.route('/api/v1/latest-audit')
@login_required
def latest_audit_api():
    session = get_session()
    latest = session.query(AuditLog).order_by(AuditLog.timestamp.desc()).first()
    if latest:
        return {
            "id": latest.id,
            "reason": latest.reason,
            "status": latest.status,
            "timestamp": latest.timestamp.isoformat()
        }
    return {}, 200

@bp.route('/reports')
@login_required
def reports():
    session = get_session()
    total_scans = session.query(AuditLog).filter_by(action_type='DETECTION_RECEIVED').count()
    total_takedowns = session.query(AuditLog).filter_by(action_type='TAKEDOWN_REQUESTED', status='SUCCESS').count()
    return render_template('reports.html', total_scans=total_scans, total_takedowns=total_takedowns)

from werkzeug.utils import secure_filename

@bp.route('/forensic-scan', methods=['GET', 'POST'])
@login_required
def forensic_scan():
    if request.method == 'POST':
        if 'file' not in request.files:
             return render_template('forensic_scan.html', error="No file uploaded")
        
        file = request.files['file']
        if file.filename == '':
            return render_template('forensic_scan.html', error="No file selected")
        
        if file:
            filename = secure_filename(file.filename)
            upload_path = os.path.join("member5_dashboard_oversight/uploads", filename)
            file.save(upload_path)
            
            from member3_detection.inference import DetectionInferenceEngine
            engine = DetectionInferenceEngine()
            results = engine.analyze(upload_path)
            
            from member4_automation_compliance.audit_logger import AuditLogger
            auditor = AuditLogger()
            
            case_details = {
                "victim_user_id": "MANUAL_UPLOAD",
                "match_confidence": results['deepfake'].get('confidence', 0),
                "platform": "Local / External",
                "risk_score": results['deepfake']['score'],
                "detection_results": results
            }
            
            auditor.log_event(
                action_type="DETECTION_RECEIVED",
                platform="LOCAL_UPLOAD",
                post_id=f"M-{filename[:10]}",
                url=filename,
                reason="Manual Forensic Scan Submission",
                status="COMPLETED",
                details=case_details
            )
            
            return render_template('forensic_scan.html', success=True, results=results, filename=filename)

    return render_template('forensic_scan.html')

@bp.route('/download-report/<report_name>')
@login_required
def download_report(report_name):
    content = f"--- DEEPFAKE OVERSIGHT FORENSIC REPORT ---\nGenerated: {datetime.utcnow()}\nReport: {report_name}\nStatus: VERIFIED\n\n[Forensic Data Scrubbed]"
    from flask import Response
    return Response(
        content,
        mimetype="text/plain",
        headers={"Content-disposition": f"attachment; filename={report_name.lower().replace(' ', '_')}.txt"}
    )

from flask import redirect, url_for, flash

@bp.route('/approve-case/<log_id>', methods=['POST'])
@login_required
def approve_case(log_id):
    from member4_automation_compliance.takedown_manager import TakedownManager
    manager = TakedownManager()
    result = manager.approve_manual_case(log_id)
    
    if result.get("status") == "SUCCESS":
        flash(f"Successfully processed approval for case #{log_id[:8]}", "success")
    else:
        flash(f"Error during approval: {result.get('message', 'Unknown Error')}", "error")
        
    return redirect(url_for('dashboard.index'))
