import click
# from flask import Flask
from app import create_app
from app.extensions import db,login_manager
from app.models import User

app = create_app()
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)