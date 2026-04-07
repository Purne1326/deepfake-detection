from flask import Blueprint, render_template, redirect, url_for, flash, request
from dummy_social_platform.models import db, User
from werkzeug.security import generate_password_hash, check_password_hash

bp = Blueprint('auth', __name__)

# Very simple session-based auth for dummy platform
# Using global or basic session dictionary for simplicity or Flask session
from flask import session

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('feed.feed'))
        flash('Invalid username or password')
    return render_template('login.html')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('auth.register'))
            
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful, please login')
        return redirect(url_for('auth.login'))
    return render_template('register.html')

@bp.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('auth.login'))
