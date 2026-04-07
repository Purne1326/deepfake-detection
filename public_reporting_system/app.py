from flask import Flask, render_template, request, redirect, url_for, flash
import os
import uuid
from werkzeug.utils import secure_filename
from member3_detection.inference import DetectionInferenceEngine
from member4_automation_compliance.audit_logger import AuditLogger

app = Flask(__name__)
app.secret_key = 'public-secret-key'
app.config['UPLOAD_FOLDER'] = 'public_reporting_system/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB limit

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

engine = DetectionInferenceEngine()
auditor = AuditLogger()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/report', methods=['GET', 'POST'])
def report():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('No selected file', 'error')
            return redirect(request.url)
        
        if file:
            filename = secure_filename(file.filename)
            unique_id = str(uuid.uuid4())[:8]
            save_name = f"{unique_id}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], save_name)
            file.save(filepath)
            
            # Run analysis
            results = engine.analyze(filepath)
            
            # Log deepfake misuse report
            name = request.form.get('name', 'Anonymous')
            email = request.form.get('email', 'N/A')
            description = request.form.get('description', '')
            
            case_details = {
                "reporter_name": name,
                "reporter_email": email,
                "description": description,
                "source": "PUBLIC_PORTAL",
                "risk_score": results['deepfake']['score'],
                "detection_results": results
            }
            
            auditor.log_event(
                action_type="DETECTION_RECEIVED",
                platform="PUBLIC_SUBMISSION",
                post_id=unique_id,
                url=save_name,
                reason=f"Public Identity Misuse Report by {name}",
                status="PENDING_REVIEW",
                details=case_details
            )
            
            return render_template('results.html', results=results, report_id=unique_id)
            
    return render_template('report.html')

@app.route('/success/<report_id>')
def success(report_id):
    return render_template('success.html', report_id=report_id)

if __name__ == '__main__':
    app.run(port=5002, debug=True)
