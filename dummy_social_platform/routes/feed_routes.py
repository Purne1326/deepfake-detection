from flask import Blueprint, render_template, session, redirect, url_for
from dummy_social_platform.models import Post, User
from sqlalchemy import desc

bp = Blueprint('feed', __name__)

@bp.route('/')
@bp.route('/feed')
def feed():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
        
    # ONLY show active (non-taken-down) posts in the Safety Feed
    posts = Post.query.filter_by(is_taken_down=False).order_by(desc(Post.created_at)).all()
    user = User.query.get(session.get('user_id'))
    return render_template('feed.html', posts=posts, user=user, active_page='feed')

@bp.route('/profile/<username>')
def profile(username):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
        
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(user_id=user.id).order_by(desc(Post.created_at)).all()
    return render_template('profile.html', profile_user=user, posts=posts, active_page='profile')

@bp.route('/explore')
def explore():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    # Show clean posts only
    posts = Post.query.filter_by(is_taken_down=False).order_by(desc(Post.created_at)).all()
    return render_template('explore.html', posts=posts, active_page='explore')
