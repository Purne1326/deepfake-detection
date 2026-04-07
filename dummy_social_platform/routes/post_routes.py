from flask import Blueprint, render_template, redirect, url_for, flash, request, session, current_app
from dummy_social_platform.models import db, Post, User
import os
from werkzeug.utils import secure_filename
import uuid

bp = Blueprint('post', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

@bp.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
        
    if request.method == 'POST':
        if 'image' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['image']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4()}_{filename}"
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(filepath)
            
            new_post = Post(
                user_id=session['user_id'],
                image_filename=unique_filename,
                caption=request.form.get('caption', '')
            )
            db.session.add(new_post)
            db.session.commit()
            return redirect(url_for('feed.feed'))
    return render_template('upload.html')

@bp.route('/<int:post_id>')
def view_post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', post=post)

from datetime import datetime

@bp.route('/api/posts/<int:post_id>/takedown', methods=['POST'])
def api_takedown(post_id):
    """
    API call for internal services to trigger a post takedown.
    """
    # Mocking API Key check for production-readiness demonstration
    api_key = request.headers.get('X-API-Key')
    if api_key != "dummy_secret_key":
        return {"error": "Unauthorized Access Detected"}, 401
        
    post = Post.query.get_or_404(post_id)
    payload = request.get_json() or {}
    
    post.is_taken_down = True
    post.taken_down_at = datetime.utcnow()
    post.taken_down_reason = payload.get('reason', 'Policy Violation')
    post.taken_down_case_id = payload.get('case_id', 'IDL-AUTO')
    
    db.session.commit()
    
    print(f"API: Post {post_id} removed by Identity Link Dashboard. Reason: {post.taken_down_reason}")
    
    return {
        "status": "SUCCESS",
        "message": "Post was successfully removed.",
        "taken_down_at": post.taken_down_at.strftime('%Y-%m-%d %H:%M:%S')
    }, 200

@bp.route('/api/posts', methods=['GET'])
def api_get_posts():
    """
    API for scrapers to list non-takedown posts.
    """
    posts = Post.query.filter_by(is_taken_down=False).all()
    posts_data = []
    for p in posts:
        posts_data.append({
            "post_id": p.id,
            "username": p.author.username,
            "caption": p.caption,
            "image_url": f"/static/uploads/{p.image_filename}" if p.image_filename else None,
            "timestamp": p.created_at.isoformat()
        })
    return {"posts": posts_data}, 200
