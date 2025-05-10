from flask import Blueprint, jsonify, request
from app.models import Product, Order, OrderItem, User,Branch,Offer
from app import db
from datetime import datetime

api = Blueprint('api', __name__)

@api.route('/api/branches', methods=['GET'])
def get_branches():
    branches = Branch.query.all()
    return jsonify([{'id': b.id, 'name': b.name} for b in branches])

@api.route('/api/register', methods=['POST'])
def register_user():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    branch_id = data.get('branch_id')

    if not username or not password or not branch_id:
        return jsonify({'error': 'Missing fields'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'User already exists'}), 409

    user = User(username=username, branch_id=branch_id)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201

@api.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()
    if user and user.check_password(user.password_hash, password):
        return jsonify({'status': 'success', 'message': 'تم تسجيل الدخول', 'user_id': user.id})
    else:
        return jsonify({'status': 'error', 'message': 'اسم المستخدم أو كلمة المرور غير صحيحة'}), 401
@api.route('/api/products', methods=['GET'])
def get_products():
    products = Product.query.filter_by(visible=True).all()
    return jsonify([
        {
            'id': p.id,
            'name': p.name,
            'price': p.price,
            'description': p.description,
            'image_url': p.image_url
        } for p in products
    ])

# @api.route('/api/orders', methods=['POST'])
# def create_order():
#     data = request.json
#     user_id = data.get('user_id')
#     items = data.get('items')  # قائمة من المنتجات

#     if not user_id or not items:
#         return jsonify({'error': 'Invalid request'}), 400

#     order = Order(user_id=user_id)
#     db.session.add(order)
#     db.session.commit()

#     for item in items:
#         order_item = OrderItem(
#             order_id=order.id,
#             product_id=item['product_id'],
#             quantity=item['quantity'],
#             unit_price=item['unit_price'],
#             total_price=item['total_price']
#         )
#         db.session.add(order_item)

#     db.session.commit()
#     return jsonify({'message': 'Order created successfully'}), 201

from flask import request, jsonify
from app.models import Order, OrderItem, Product
from app import db

@api.route('/api/create_order', methods=['POST'])
def create_order():
    try:
        data = request.get_json()
        
        customer_id = data['customer_id']
        branch_id = data['branch_id']
        cart = data['cart']  # القائمة التي تحتوي على المنتجات والكميات (مثال: [{'product_id': 1, 'quantity': 2}, ...])
        
        # حساب إجمالي السعر للطلب
        total_price = 0
        for item in cart:
            product = Product.query.get(item['product_id'])
            total_price += product.price * item['quantity']
        
        # إنشاء الطلب
        order = Order(
            customer_id=customer_id,
            branch_id=branch_id,
            total_price=total_price,
            status="في الانتظار"
        )
        db.session.add(order)
        db.session.commit()

        # إضافة العناصر إلى الطلب
        for item in cart:
            product = Product.query.get(item['product_id'])
            order_item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=item['quantity'],
                unit_price=product.price,
                total_price=product.price * item['quantity']
            )
            db.session.add(order_item)
        
        db.session.commit()
        
        return jsonify({"message": "تم إرسال الطلب بنجاح", "order_id": order.id}), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@api.route('/api/offers', methods=['GET'])
def get_offers():
    offers = Offer.query.filter(Offer.end_date >= datetime.utcnow()).all()  # الحصول على العروض التي لم تنتهي بعد
    offer_list = []

    for offer in offers:
        offer_list.append({
            'title': offer.title,
            'description': offer.description,
            'product_name': offer.product.name,
            'discount_percentage': offer.discount_percentage,
            'min_quantity': offer.min_quantity,
            'payment_condition': offer.payment_condition,
            'start_date': offer.start_date,
            'end_date': offer.end_date
        })

    return jsonify(offer_list)

##################################

# @api.route('/products', methods=['GET'])
# def get_products():
#     products = Product.query.all()
#     return jsonify([{
#         'id': p.id,
#         'name': p.name,
#         'description': p.description,
#         'price': p.price,
#         'image_url': p.image_url,
#         'stock': p.stock
#     } for p in products])

# @api.route('/orders', methods=['POST'])
# def create_order():
#     data = request.get_json()
    
#     # التحقق من صحة البيانات
#     if not all(key in data for key in ['user_id', 'items', 'total']):
#         return jsonify({'error': 'بيانات ناقصة'}), 400
    
#     # إنشاء الطلب
#     order = Order(
#         user_id=data['user_id'],
#         total=data['total'],
#         status='pending'
#     )
#     db.session.add(order)
    
#     # إضافة العناصر
#     for item in data['items']:
#         product = Product.query.get(item['product_id'])
#         if not product:
#             continue
            
#         order_item = OrderItem(
#             order=order,
#             product_id=item['product_id'],
#             quantity=item['quantity'],
#             price=item['price']
#         )
#         db.session.add(order_item)
    
#     db.session.commit()
    
#     return jsonify({
#         'success': True,
#         'order_id': order.id
#     }), 201