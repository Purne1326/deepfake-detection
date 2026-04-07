from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

bp = Blueprint('protection', __name__)

@bp.route('/register-face', methods=['GET', 'POST'])
@login_required
def register_face():
    if request.method == 'POST':
        # Simulated Face Registration
        flash(f"Face identity for {current_user.username} successfully registered and encrypted in Identity Command database.", "success")
        return redirect(url_for('feed.feed'))
    return render_template('register_face.html')
