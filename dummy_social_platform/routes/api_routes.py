from flask import Blueprint, jsonify, request
from dummy_social_platform.models import db, Post, User
from datetime import datetime
import os

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/posts', methods=['GET'])
def get_posts():
    posts = Post.query.filter_by(is_taken_down=False).all()
    return jsonify({
        'posts': [{
            'post_id': p.id,
            'username': p.author.username,
            'image_url': f'/static/uploads/{p.image_filename}',
            'caption': p.caption,
            'timestamp': p.created_at.isoformat()
        } for p in posts]
    })

@bp.route('/posts/<int:post_id>/takedown', methods=['POST'])
def takedown_post(post_id):
    # Simulated API Key validation can be added here
    data = request.get_json() or {}
    post = Post.query.get_or_404(post_id)
    post.is_taken_down = True
    post.taken_down_at = datetime.utcnow()
    post.taken_down_reason = data.get('reason', 'Policy violation')
    post.taken_down_case_id = data.get('case_id', 'Unknown')
    db.session.commit()
    
    return jsonify({
        'status': 'SUCCESS',
        'post_id': post.id,
        'taken_down_at': post.taken_down_at.isoformat()
    })
