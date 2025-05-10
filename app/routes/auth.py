from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
# from werkzeug import urls
from app.extensions import db
from app.models import User,Permissions
from flask import Blueprint
auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            if not next_page:
                next_page = url_for('admin.dashboard')
            return redirect(next_page)
        
        flash('اسم المستخدم أو كلمة المرور غير صحيحة')
    
    return render_template('admin/login.html',Permissions=Permissions)  # تأكد من وجود هذا القالب

@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))