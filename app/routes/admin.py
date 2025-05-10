from flask import Blueprint, render_template, redirect, url_for, flash,request,jsonify
from flask_login import login_required, current_user
from app.models import Product, Order, User,Permissions,Permission,Branch,ProductPriceHistory,Offer
from app.extensions import db
from werkzeug.utils import secure_filename
import os
from config import Config
import secrets
from PIL import Image

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

admin = Blueprint('admin', __name__)

def save_picture(form_picture, path, output_size=None):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_name = random_hex + f_ext
    picture_path = os.path.join(app.root_path, path, picture_name)
    i = Image.open(form_picture)
    if output_size:
        i.thumbnail(output_size)
    i.save(picture_path)
    return picture_name

@admin.route('/')
@login_required
def dashboard():
    # if not current_user.has_permission(Permissions.MANAGE_PRODUCTS):
    #     flash('غير مسموح بالوصول', 'danger')
    #     return redirect(url_for('admin.dashboard'))
    
    products_count = Product.query.count()
    orders_count = Order.query.count()
    return render_template('admin/dashboard.html', 
                         products_count=products_count,
                         orders_count=orders_count,Permissions=Permissions)

@admin.route('/products')
@login_required
def products():
    # if not current_user.has_permission(Permissions.MANAGE_PRODUCTS):
    #     flash('غير مسموح بالوصول', 'danger')
    #     return redirect(url_for('admin.dashboard'))
    
    products = Product.query.order_by(Product.updated_at.desc()).all()
    return render_template('admin/products.html', products=products,Permissions=Permissions)
@admin.route('/products/add', methods=['GET', 'POST'])
@login_required
def add_product():
    if not current_user.has_permission(Permissions.MANAGE_PRODUCTS):
        flash('ليس لديك صلاحية الوصول', 'danger')
        return redirect(url_for('admin.dashboard'))
    
    if request.method == 'POST':
        # معالجة بيانات النموذج
        name = request.form.get('name')
        description = request.form.get('description')
        price = float(request.form.get('price'))
        stock = request.form.get('stock')
        visible = request.form.get('visible') == 'on'
        # معالجة تحميل الصورة
        image_url = None
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(Config.UPLOAD_FOLDER, filename))
                image_url = f'uploads/{filename}'
        
        # إنشاء المنتج
        product = Product(
            name=name,
            description=description,
            price=price,
            stock=stock,
            image_url=image_url,
            visible=visible
        )
        
        db.session.add(product)
        db.session.commit()
        flash('تمت إضافة المنتج بنجاح', 'success')
        return redirect(url_for('admin.products'))
    
    return render_template('admin/add_product.html')

@admin.route('/products/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_product(id):
    if not current_user.has_permission(Permissions.MANAGE_PRODUCTS):
        flash('ليس لديك صلاحية الوصول', 'danger')
        return redirect(url_for('admin.dashboard'))
    
    product = Product.query.get_or_404(id)
    
    if request.method == 'POST':
        product.name = request.form.get('name')
        product.description = request.form.get('description')
        # product.price = float(request.form.get('price'))
        product.stock = request.form.get('stock')
        product.visible = request.form.get('visible') == 'on'
        new_price=float(request.form.get('price'))
        if product.price != new_price:
            # حفظ السعر القديم
            history = ProductPriceHistory(
                product_id=product.id,
                old_price=product.price
            )
            db.session.add(history)

            # تحديث السعر الجديد
            product.price = new_price
            db.session.commit()
        # تحديث الصورة إذا تم تحميل جديدة
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(Config.UPLOAD_FOLDER, filename))
                product.image_url = f'uploads/{filename}'
        
        db.session.commit()
        flash('تم تحديث المنتج بنجاح', 'success')
        return redirect(url_for('admin.products'))
    
    return render_template('admin/edit_product.html', product=product)
@admin.route('/products/<int:id>')
@login_required
def view_product(id):
    product = Product.query.get_or_404(id)
    return render_template('admin/product_detail.html', product=product)
@admin.route('/products/delete/<int:id>', methods=['POST'])
@login_required
def delete_product(id):
    if not current_user.has_permission(Permissions.MANAGE_PRODUCTS):
        flash('ليس لديك صلاحية الوصول', 'danger')
        return redirect(url_for('admin.dashboard'))
    
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    flash('تم حذف المنتج بنجاح', 'success')
    return redirect(url_for('admin.dashboard'))

@admin.route('/products/toggle_visibility/<int:product_id>', methods=['POST'])
@login_required
def toggle_visibility(product_id):
    if not current_user.has_permission(Permissions.MANAGE_PRODUCTS):
        flash('ليس لديك صلاحية الوصول', 'danger')
        return redirect(url_for('auth.login'))

    product = Product.query.get_or_404(product_id)
    product.visible = not product.visible
    db.session.commit()
    flash(f"تم {'إظهار' if product.visible else 'إخفاء'} المنتج")
    return redirect(url_for('admin.products'))

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}


@admin.route('/orders')
@login_required
def orders():
    # if not current_user.is_admin:
    #     flash('غير مسموح بالوصول', 'danger')
    #     return redirect(url_for('admin.dashboard'))
    
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return render_template('admin/orders.html', orders=orders,Permissions=Permissions)

def require_manage_users():
    if not current_user.has_permission(Permissions.MANAGE_USERS):
        flash('غير مسموح بالوصول', 'danger')
        return redirect(url_for('admin.dashboard'))

@admin.route('/users')
@login_required
def list_users():
    require_manage_users()
    users = User.query.all()
    return render_template('admin/listuser.html', users=users)

@admin.route('/users/add', methods=['GET', 'POST'])
@login_required
def add_user():
    require_manage_users()
    permissions = Permission.query.all()
    branch=Branch.query.all()
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        branch_id = request.form['branch_id']
        selected_perms = request.form.getlist('permissions')
        user = User(username=username,branch_id=branch_id)
        user.set_password(password)
        user.permissions = Permission.query.filter(Permission.name.in_(selected_perms)).all()
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('admin.list_users'))
    return render_template('admin/adduser.html', permissions=permissions,branchs=branch)

@admin.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    require_manage_users()
    user = User.query.get_or_404(user_id)
    permissions = Permission.query.all()
    branch=Branch.query.all()
    if request.method == 'POST':
        user.username = request.form['username']
        if request.form['password']:
            password =request.form['password']
            user.password =user.set_password(password)
        selected_perms = request.form.getlist('permissions')
        user.permissions = Permission.query.filter(Permission.name.in_(selected_perms)).all()
        db.session.commit()
        return redirect(url_for('admin.list_users'))
    return render_template('admin/adduser.html', user=user, permissions=permissions,branchs=branch)

@admin.route('/users/delete/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    require_manage_users()
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('admin.list_users'))
@admin.route('/admin/create-offer', methods=['GET', 'POST'])
@login_required
def create_offer():
    require_manage_users()

    if request.method == 'POST':
        title = request.form['title']
        description = request.form.get('description')
        product_id = request.form.get('product_id') or None
        discount = request.form.get('discount') or 0
        min_quantity = request.form.get('min_quantity') or 0
        payment_condition = request.form.get('payment_condition')
        end_date = request.form.get('end_date')
        active = 'active' in request.form

        try:
            offer = Offer(
                title=title,
                description=description,
                product_id=int(product_id) if product_id else None,
                discount=float(discount),
                min_quantity=int(min_quantity),
                payment_condition=payment_condition,
                end_date=datetime.strptime(end_date, '%Y-%m-%d') if end_date else None,
                active=active
            )
            db.session.add(offer)
            db.session.commit()
            flash('تم حفظ العرض بنجاح', 'success')
            return redirect(url_for('admin.create_offer'))
        except Exception as e:
            db.session.rollback()
            flash('حدث خطأ أثناء حفظ العرض: ' + str(e), 'danger')

    return render_template('admin/offers.html')
# @admin.route('/create_offer', methods=['POST'])
# @login_required
# def create_offer():
#     require_manage_users()
#     try:
#         data = request.get_json()  # قراءة بيانات العرض

#         title = data['title']
#         description = data['description']
#         product_id = data['product_id']
#         discount_percentage = data['discount_percentage']
#         min_quantity = data['min_quantity']
#         payment_condition = data['payment_condition']
#         end_date = data['end_date']  # يجب أن يتم إدخال تاريخ نهاية العرض

#         # تحقق من وجود المنتج
#         product = Product.query.get(product_id)
#         if not product:
#             return jsonify({"error": "المنتج غير موجود"}), 400

#         offer = Offer(
#             title=title,
#             description=description,
#             product_id=product_id,
#             discount_percentage=discount_percentage,
#             min_quantity=min_quantity,
#             payment_condition=payment_condition,
#             end_date=end_date
#         )
        
#         db.session.add(offer)
#         db.session.commit()

#         return jsonify({"message": "تم إضافة العرض بنجاح"}), 201
#     except Exception as e:
#         db.session.rollback()
#         return jsonify({"error": str(e)}), 400
