from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
from app.routes import auth
from app.extensions import db,login_manager
from flask_migrate import Migrate
from flask_cors import CORS

migrate = Migrate(db)
login_manager.login_view = 'auth.login'
login_manager.login_message_category = "info"
def create_app(config_class=Config):
    app = Flask(__name__)
    CORS(app)
    app.config.from_object(config_class)
    
    db.init_app(app)
    login_manager.init_app(app)
    
    
    # تأجيل استيراد وتشغيل الـ blueprints لتجنب الاستيراد الدائري
    with app.app_context():
        from app.routes import admin, auth, api
        app.register_blueprint(admin.admin)
        app.register_blueprint(auth.auth)
        app.register_blueprint(api.api)
        
        # إنشاء جداول قاعدة البيانات

    
    return app