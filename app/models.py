from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask import url_for
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db 
import os

# ===== جدول المنتجات =====
class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(255))
    stock = db.Column(db.String(10), default="متوفر")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    visible = db.Column(db.Boolean, default=True)  # True = ظاهر، False = مخفي


    order_items = db.relationship('OrderItem', back_populates='product', lazy=True)
    offers = db.relationship('Offer', backref='product', lazy=True)

    def get_image_url(self):
        if self.image_url:
            return url_for('static', filename=f'uploads/{os.path.basename(self.image_url)}')
        return url_for('static', filename='uploads/product.jpg')
    
    def __repr__(self):
        return f'<Product {self.name}>'

# ===== جدول علاقة بين العملاء والأصناف =====
# class CustomerInterest(db.Model):
#     __tablename__ = 'customer_interests'
#     customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), primary_key=True)
#     category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), primary_key=True)

#     customer = db.relationship('Customer', backref='interests', lazy=True)
#     category = db.relationship('Category', backref='interested_customers', lazy=True)
# # ===== جدول العملاء =====
class ProductPriceHistory(db.Model):
    __tablename__ = 'product_price_history'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    old_price = db.Column(db.Float, nullable=False)
    changed_at = db.Column(db.DateTime, default=datetime.utcnow)

    product = db.relationship('Product', backref='price_history')

class Customer(db.Model, UserMixin):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=False)

    # ربط العملاء بالأصناف التي يهتمون بها
    orders = db.relationship('Order', backref='customer', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_interested_products(self):
        interested_categories = self.interests
        products = Product.query.filter(Product.category_id.in_([category.id for category in interested_categories])).all()
        return products
    
    def __repr__(self):
        return f'<Customer {self.username}>'


############################
# ===== جدول الفروع =====
class Branch(db.Model):
    __tablename__ = 'branches'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(255))

    customers = db.relationship('Customer', backref='branch', lazy=True)
    orders = db.relationship('Order', backref='branch', lazy=True)
    users = db.relationship('User', back_populates='branch', lazy=True)


# جدول الصلاحيات
class Permission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.String(128))



# جدول وسطي لربط المستخدمين بالصلاحيات
user_permissions = db.Table('user_permissions',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    db.Column('permission_id', db.Integer, db.ForeignKey('permission.id', ondelete='CASCADE'), primary_key=True)
)
# ===== جدول المسؤولين (المدير + رؤساء الفروع) =====
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)#id user
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'))  # Null for manager
    permissions = db.relationship('Permission', secondary=user_permissions, backref='users')
    branch = db.relationship('Branch', back_populates='users')

    def has_permission(self, perm_name):
        return any(p.name == perm_name for p in self.permissions)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    def __repr__(self):
        return f'<User {self.username}>'


# ===== جدول المنتجات =====

# ===== جدول العروض =====

class Offer(db.Model):
    __tablename__ = 'offers'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=True)
    discount = db.Column(db.Float)  # نسبة الخصم مثلاً 10 تعني 10%
    
    min_quantity = db.Column(db.Integer, nullable=True)  # الحد الأدنى للاستفادة من العرض
    payment_condition = db.Column(db.String(100), nullable=True)  # شرط الدفع (مثل الدفع الفوري)
    end_date = db.Column(db.Date, nullable=True)  # تاريخ انتهاء العرض

    active = db.Column(db.Boolean, default=True)




# ===== جدول الطلبات =====
class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=False)
    total = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='قيد المعالجة')  # pending, approved, rejected# مثل: قيد المعالجة، تم التوصيل، ملغاة
    total_price = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    order_items = db.relationship('OrderItem', backref='order', lazy=True)


# ===== تفاصيل المنتجات في الطلب =====
class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)# الكمية
    unit_price = db.Column(db.Float, nullable=False)# سعر الوحده
    total_price = db.Column(db.Float, nullable=False) # مجموع كمية الكلي للكمية
    # إضافة العلاقة بين الطلب والمنتج
    product = db.relationship('Product', back_populates='order_items', lazy=True)
class Permissions:
    MANAGE_PRODUCTS = 'manage_products'
    MANAGE_USERS = 'manage_users'
    MANAGE_OFFERS = 'manage_offers'
    VIEW_ALL_ORDERS = 'view_all_orders'
    VIEW_BRANCH_ORDERS = 'view_branch_orders'
    VIEW_ALL_REPORTS = 'view_all_reports'
    VIEW_BRANCH_REPORTS = 'view_branch_reports'
    VIEW_ALL_BRANCHES = 'view_all_branches'

permission_choices = [
    Permissions.MANAGE_PRODUCTS,
    Permissions.MANAGE_USERS,
    Permissions.MANAGE_OFFERS,
    Permissions.VIEW_ALL_ORDERS,
    Permissions.VIEW_BRANCH_ORDERS,
    Permissions.VIEW_ALL_REPORTS,
    Permissions.VIEW_BRANCH_REPORTS,
    Permissions.VIEW_ALL_BRANCHES,
]

# دالة لإضافة صلاحيات للمستخدم
def assign_permissions_to_user(user_id, permission_names):
    user = User.query.get(user_id)
    permissions = Permission.query.filter(Permission.name.in_(permission_names)).all()
    
    for permission in permissions:
        user.permissions.append(permission)
    
    db.session.commit()

# دالة لإضافة صلاحية جديدة
def add_permission(permission_name, description):
    permission = Permission(name=permission_name, description=description)
    db.session.add(permission)
    db.session.commit()

# دالة لاسترجاع صلاحيات المستخدم
def get_user_permissions(user_id):
    user = User.query.get(user_id)
    return [permission.name for permission in user.permissions]