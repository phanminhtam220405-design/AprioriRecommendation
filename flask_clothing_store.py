"""
Flask E-commerce - Modern Clothing Store with Advanced Features
Run:
  python -m venv venv
  pip install flask
  python flask_clothing_store.py
Open http://127.0.0.1:5000
"""
from itertools import product

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_from_directory
from uuid import uuid4
import datetime
from functools import wraps
from collections import Counter
import json
import matplotlib.pyplot as plt
import os
import csv
import unicodedata
import pandas as pd
import unicodedata
from collections import Counter
import json
from mlxtend.frequent_patterns import apriori, association_rules
from mlxtend.preprocessing import TransactionEncoder
from werkzeug.utils import secure_filename
from database import db, init_db, Product, User, Order, Review, ReviewReply, ReviewLike, Voucher
from apriori import get_recommendations

app = Flask(__name__)
app.secret_key = "dev-secret-key-please-change-in-production"

# Upload configuration
UPLOAD_FOLDER = 'Images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # 32MB max

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///clothing_store.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Create upload folder if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Initialize database
init_db(app)

# Helper function to check allowed file
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Route to serve uploaded images
@app.route('/Images/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# ---------- Helper Functions ----------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash('Vui lòng đăng nhập để tiếp tục', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def staff_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session or session['user']['role'] not in ['admin', 'staff']:
            flash('Đây là khu vực dành cho nhân viên', 'error')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

def format_price(price):
    return f"{price:,.0f}đ".replace(',', '.')
def normalize_text(text):
    if not text:
        return ''
    text = str(text).lower()
    text = unicodedata.normalize('NFD', text)
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
    return text
def detect_product_gender(product):
    text = normalize_text(
        f"{product.name} {product.category} {product.description}"
    )

    female_keywords = [
        'nu', 'vay', 'dam', 'chan vay', 'croptop',
        'ao body', 'giay cao got', 'cardigan', 'legging','blazer'
    ]

    male_keywords = [
        'vest nam', 'ao polo nam', 'ao ba lo nam',
        'quan jean nam', 'quan short nam',
        'quan kaki nam', 'ca vat'
    ]

    if any(keyword in text for keyword in female_keywords):
        return 'female'

    if any(keyword in text for keyword in male_keywords):
        return 'male'

    return 'all'

def get_cart():
    return session.get('cart', [])

def get_wishlist():
    user_email = session.get('user', {}).get('email')
    if user_email:
        user = User.query.get(user_email)
        if user:
            return json.loads(user.wishlist) if user.wishlist else []
    return []

def calculate_cart_totals():
    cart = get_cart()
    subtotal = sum(item['price'] * item['qty'] for item in cart)
    
    # Calculate shipping
    shipping = 0 if subtotal >= 500000 else 30000
    
    # Calculate voucher discount
    voucher_discount = session.get('voucher_discount', 0)
    
    total = subtotal - voucher_discount + shipping
    return subtotal, shipping, voucher_discount, total

def get_featured_products():
    products = Product.query.filter_by(featured=True).all()
    return [p.to_dict() for p in products]

def get_best_sellers():
    products = Product.query.order_by(Product.sold.desc()).limit(8).all()
    return [p.to_dict() for p in products]

def get_categories():
    categories = db.session.query(Product.category).distinct().all()
    return [c[0] for c in categories]

# ---------- Context Processors ----------
@app.context_processor
def utility_processor():
    return {
        'now': datetime.datetime.now(),
        'wishlist_count': lambda: len(get_wishlist()),
        'cart_count': lambda: len(get_cart()),
        'format_price': format_price,
        'get_featured_products': get_featured_products,
        'get_best_sellers': get_best_sellers,
        'get_categories': get_categories
    }

# ---------- Routes ----------
@app.route('/')
def home():
    if 'user' in session and session['user']['role'] in ['admin', 'staff']:
        return redirect(url_for('admin_dashboard'))

    featured_products = Product.query.limit(12).all()

    categories = db.session.query(
        Product.category
    ).distinct().all()
# =====================================================
# PERSONALIZED RECOMMENDATION (TRANG CHỦ)
# =====================================================
# Mục đích:
# - Gợi ý sản phẩm cho khách hàng dựa trên lịch sử mua hàng.
#
# Quy trình:
# 1. Lấy toàn bộ đơn hàng của khách hàng.
# 2. Xác định category được mua nhiều nhất.
# 3. Xác định giới tính sản phẩm (Nam/Nữ/Unisex).
# 4. Áp dụng thuật toán Apriori để tìm category liên quan.
# 5. Chọn sản phẩm có lượt bán (sold) và đánh giá (rating) cao.
# 6. Hiển thị tối đa 6 sản phẩm gợi ý.
#
# Công thức thực tế:
# Apriori -> tìm category nên gợi ý
# Sold + Rating -> chọn sản phẩm tốt nhất trong category đó
# =====================================================
    personalized_products = []

    if 'user' in session and session['user']['role'] == 'user':
        user_email = session['user']['email']

        orders = Order.query.filter_by(
            user_email=user_email
        ).all()

        bought_categories = []
        bought_genders = []
        bought_product_ids = []

        for order in orders:
            try:
                items = json.loads(order.items) if order.items else []

                for item in items:
                    category = item.get('category')

                    product_id = (
                        item.get('product_id')
                        or item.get('id')
                        or item.get('pid')
                    )

                    product_obj = None

                    if product_id:
                        product_obj = Product.query.get(product_id)

                    if not category and product_obj:
                        category = product_obj.category

                    if category:
                        bought_categories.append(category)

                    if product_obj:
                        bought_genders.append(
                            detect_product_gender(product_obj)
                        )
                        bought_product_ids.append(product_obj.id)

            except Exception as e:
                print("Read order items error:", e)

        if bought_categories:
            most_common_category = Counter(bought_categories).most_common(1)[0][0]

            product_gender = None

            if bought_genders:
                product_gender = Counter(bought_genders).most_common(1)[0][0]
# Gọi các luật kết hợp được sinh ra từ thuật toán Apriori.
# most_common_category:
#     nhóm sản phẩm khách hàng mua nhiều nhất.
# product_gender:
#     Nam / Nữ / Unisex.
# Kết quả trả về:
#     danh sách category thường được mua kèm.
            try:
                recommendations = get_recommendations(
                    most_common_category,
                    product_gender
                )

                added_ids = set()

                for rec in recommendations:
                    category = rec.get("category") if isinstance(rec, dict) else rec

                    query = Product.query.filter_by(category=category)\
                        .filter(Product.stock > 0)

                    if bought_product_ids:
                        query = query.filter(~Product.id.in_(bought_product_ids))

                    products = query.order_by(
                        Product.sold.desc(),
                        Product.rating.desc()
                    ).limit(6).all()

                    for p in products:
                        p_gender = detect_product_gender(p)

                        if product_gender in ['male', 'female']:
                            if p_gender not in [product_gender, 'all', 'unisex']:
                                continue

                        if p.id not in added_ids:
                            personalized_products.append(p.to_dict())
                            added_ids.add(p.id)

                        if len(personalized_products) >= 6:
                            break

                    if len(personalized_products) >= 6:
                        break

            except Exception as e:
                print("Home recommendation error:", e)

        if bought_categories and not personalized_products:
            query = Product.query.filter(Product.stock > 0)

            if bought_product_ids:
                query = query.filter(~Product.id.in_(bought_product_ids))

            fallback_products = query.order_by(
                Product.sold.desc(),
                Product.rating.desc()
            ).limit(20).all()

            for p in fallback_products:
                p_gender = detect_product_gender(p)

                if bought_genders:
                    product_gender = Counter(bought_genders).most_common(1)[0][0]

                    if product_gender in ['male', 'female']:
                        if p_gender not in [product_gender, 'all', 'unisex']:
                            continue

                personalized_products.append(p.to_dict())

                if len(personalized_products) >= 6:
                    break

        print("HOME USER:", user_email)
        print("HOME ORDERS:", len(orders))
        print("HOME BOUGHT:", bought_categories)
        print("HOME GENDERS:", bought_genders)
        print("HOME RECOMMEND:", len(personalized_products))

    return render_template(
        'home.html',
        featured_products=[
            p.to_dict() for p in featured_products
        ],
        personalized_products=personalized_products,
        categories=categories
    )
@app.route('/products')
def products():
    category = request.args.get('category', '')
    search = request.args.get('q', '').strip()
    price_range = request.args.get('price', '')
    sort = request.args.get('sort', '')

    query = Product.query

    if category:
        query = query.filter_by(category=category)

    if price_range:
        if price_range == '0-200000':
            query = query.filter(Product.price <= 200000)
        elif price_range == '200000-500000':
            query = query.filter(Product.price >= 200000, Product.price <= 500000)
        elif price_range == '500000-999999999':
            query = query.filter(Product.price >= 500000)

    if sort == 'price_asc':
        query = query.order_by(Product.price.asc())
    elif sort == 'price_desc':
        query = query.order_by(Product.price.desc())
    elif sort == 'popular':
        query = query.order_by(Product.sold.desc())
    elif sort == 'rating':
        query = query.order_by(Product.rating.desc())
    elif sort == 'newest':
        query = query.order_by(Product.created_at.desc())

    products_list = query.all()

    if search:
        search_norm = normalize_text(search)

        keyword_map = {
            'ao': ['ao', 'thun', 'hoodie', 'somi', 'so mi', 'khoac', 'len', 'body', 'cardigan', 'blazer'],
            'quan': ['quan', 'jean', 'short', 'kaki', 'tay', 'jogger'],
            'vay': ['vay', 'dam', 'chan vay'],
            'giay': ['giay', 'sneaker', 'boot', 'dep', 'sandal'],
            'non': ['non', 'mu', 'cap'],
        }

        related_keywords = keyword_map.get(search_norm, [search_norm])

        products_list = [
            p for p in products_list
            if any(
                keyword in normalize_text(p.name)
                or keyword in normalize_text(p.category)
                or keyword in normalize_text(p.description)
                for keyword in related_keywords
            )
        ]

    return render_template(
        'products.html',
        products=[p.to_dict() for p in products_list],
        category=category,
        search=search,
        price_range=price_range,
        sort=sort
    )


@app.route('/product/<pid>')
def product_detail(pid):

    product = Product.query.get(pid)

    if not product:
        flash('Sản phẩm không tồn tại', 'error')
        return redirect('/products')

    # =========================
    # RELATED PRODUCTS CŨ
    # =========================
    related = Product.query.filter_by(
        category=product.category
    ).filter(Product.id != pid).limit(4).all()

    related_products = [p.to_dict() for p in related]

    # =========================
    # APRIORI RECOMMENDATION
    # =========================
    recommended_products = []

    try:
        product_gender = detect_product_gender(product)

        recommendations = get_recommendations(product.category, product_gender)

        if not recommendations:
            recommendations = get_recommendations(product.category)

        print("PRODUCT:", product.name)
        print("CATEGORY:", product.category)
        print("GENDER:", product_gender)
        print("RECOMMEND:", recommendations)

        cart_ids = [item['id'] for item in session.get('cart', [])]
        added_ids = set()

        for rec in recommendations:
            category = rec.get("category")
            confidence = rec.get("confidence", 0)

            query = Product.query.filter_by(category=category)\
                .filter(Product.id != pid)\
                .filter(Product.stock > 0)

            if cart_ids:
                query = query.filter(~Product.id.in_(cart_ids))

            products = query.order_by(
                Product.sold.desc(),
                Product.rating.desc()
            ).limit(3).all()

            for p in products:
                if p.id not in added_ids:
                    item = p.to_dict()
                    item["score"] = confidence
                    recommended_products.append(item)
                    added_ids.add(p.id)

                if len(recommended_products) >= 6:
                    break

            if len(recommended_products) >= 6:
                break

    except Exception as e:
        print("Apriori Error:", e)
    # Nếu Apriori không có gợi ý thì lấy sản phẩm bán chạy
    # =========================
    if not recommended_products:
        fallback_products = Product.query\
            .filter(Product.id != pid)\
            .filter(Product.stock > 0)\
            .order_by(
                Product.sold.desc(),
                Product.rating.desc()
            )\
            .limit(6)\
            .all()

        recommended_products = [
            p.to_dict()
            for p in fallback_products
        ]
    # =========================
    # REVIEW PAGINATION
    # =========================
    page = request.args.get('page', 1, type=int)

    per_page = 5

    user_email = session.get('user', {}).get('email')

    reviews_query = Review.query.filter_by(
        product_id=pid
    ).order_by(
        Review.created_at.desc()
    )

    reviews_pagination = reviews_query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    # =========================
    # RATING STATISTICS
    # =========================
    all_reviews = Review.query.filter_by(
        product_id=pid
    ).all()

    total_reviews = len(all_reviews)

    avg_rating = (
        sum([r.rating for r in all_reviews]) / total_reviews
        if total_reviews > 0 else 0
    )

    rating_stats = {
        '5': len([r for r in all_reviews if r.rating == 5]),
        '4': len([r for r in all_reviews if r.rating == 4]),
        '3': len([r for r in all_reviews if r.rating == 3]),
        '2': len([r for r in all_reviews if r.rating == 2]),
        '1': len([r for r in all_reviews if r.rating == 1]),
    }

    # =========================
    # CHECK USER CAN REVIEW
    # =========================
    can_review = False
    user_reviewed = False

    if user_email:

        existing_review = Review.query.filter_by(
            product_id=pid,
            user_email=user_email
        ).first()

        user_reviewed = existing_review is not None

        if not user_reviewed:

            user_orders = Order.query.filter_by(
                user_email=user_email,
                status='completed'
            ).all()

            for order in user_orders:

                order_items = json.loads(order.items) if order.items else []

                if any(
                    item.get('product_id') == pid or
                    item.get('id') == pid
                    for item in order_items
                ):
                    can_review = True
                    break

    return render_template(
        'product_detail.html',
        product=product.to_dict(),
        related_products=related_products,

        # APRIORI
        recommended_products=recommended_products,

        reviews=[
            r.to_dict(user_email)
            for r in reviews_pagination.items
        ],

        reviews_pagination=reviews_pagination,
        total_reviews=total_reviews,
        avg_rating=round(avg_rating, 1),
        rating_stats=rating_stats,
        can_review=can_review,
        user_reviewed=user_reviewed if user_email else False,
        user_email=user_email
    )


@app.route('/update-cart', methods=['POST'])
def update_cart():
    pid = request.form.get('pid')
    action = request.form.get('action')
    
    cart = get_cart()
    item = next((item for item in cart if item['id'] == pid), None)
    
    if item:
        if action == 'increase':
            item['qty'] += 1
        elif action == 'decrease' and item['qty'] > 1:
            item['qty'] -= 1
    
    session['cart'] = cart
    return redirect('/cart')

@app.route('/remove-from-cart', methods=['POST'])
def remove_from_cart():
    pid = request.form.get('pid')
    
    cart = get_cart()
    cart = [item for item in cart if item['id'] != pid]
    
    session['cart'] = cart
    flash('Đã xóa sản phẩm khỏi giỏ hàng', 'success')
    return redirect('/cart')

@app.route('/cart')
@login_required
def cart():

    if session['user']['role'] in ['admin', 'staff']:
        return redirect(url_for('admin_dashboard'))
    
    cart_items = session.get('cart', [])
    subtotal, shipping, voucher_discount, total = calculate_cart_totals()
    return render_template(
        'cart.html',
        cart=cart_items,
        subtotal=subtotal,
        shipping=shipping,
        voucher_discount=voucher_discount,
        total=total
    )
@app.route('/apply-voucher', methods=['POST'])
@login_required
def apply_voucher():
    code = request.form.get('voucher', '').upper().strip()
    voucher = Voucher.query.filter_by(code=code, active=True).first()
    
    if not voucher:
        flash('Mã giảm giá không hợp lệ', 'error')
        return redirect('/cart')
    
    subtotal, _, _, _ = calculate_cart_totals()
    
    if subtotal < voucher.min_order:
        flash(f'Đơn hàng tối thiểu {format_price(voucher.min_order)} để sử dụng mã này', 'error')
        return redirect('/cart')
    
    if voucher.type == 'percent':
        discount = subtotal * voucher.discount / 100
    elif voucher.type == 'shipping':
        discount = voucher.discount
        # Set shipping to 0
        session['free_shipping'] = True
    else:
        discount = voucher.discount
    
    session['voucher_code'] = code
    session['voucher_discount'] = discount
    
    flash(f'Áp dụng mã giảm giá thành công', 'success')
    return redirect('/cart')

@app.route('/remove-voucher', methods=['POST'])
@login_required
def remove_voucher():
    session.pop('voucher_code', None)
    session.pop('voucher_discount', None)
    session.pop('free_shipping', None)
    flash('Đã xóa mã giảm giá', 'success')
    return redirect('/cart')

@app.route('/add-to-wishlist', methods=['POST'])
@login_required
def add_to_wishlist():
    data = request.get_json()
    pid = data.get('pid')
    
    user_email = session['user']['email']
    user = User.query.get(user_email)
    if user:
        wishlist = json.loads(user.wishlist) if user.wishlist else []
        if pid not in wishlist:
            wishlist.append(pid)
            user.wishlist = json.dumps(wishlist)
            db.session.commit()
    
    return jsonify({'success': True})

@app.route('/remove-from-wishlist', methods=['POST'])
@login_required
def remove_from_wishlist():
    data = request.get_json()
    pid = data.get('pid')
    
    user_email = session['user']['email']
    user = User.query.get(user_email)
    if user:
        wishlist = json.loads(user.wishlist) if user.wishlist else []
        if pid in wishlist:
            wishlist.remove(pid)
            user.wishlist = json.dumps(wishlist)
            db.session.commit()
    
    return jsonify({'success': True})

# ---------- Review Routes ----------
@app.route('/product/<pid>/reviews')
def product_reviews(pid):
    """Get reviews for a product with pagination"""
    product = Product.query.get(pid)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    page = request.args.get('page', 1, type=int)
    per_page = 10
    sort = request.args.get('sort', 'recent')  # recent, helpful, rating_high, rating_low
    
    query = Review.query.filter_by(product_id=pid)
    
    # Apply sorting
    if sort == 'helpful':
        query = query.order_by(Review.helpful_count.desc())
    elif sort == 'rating_high':
        query = query.order_by(Review.rating.desc())
    elif sort == 'rating_low':
        query = query.order_by(Review.rating.asc())
    else:  # recent
        query = query.order_by(Review.created_at.desc())
    
    reviews = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Calculate rating statistics
    all_reviews = Review.query.filter_by(product_id=pid).all()
    total_reviews = len(all_reviews)
    avg_rating = sum([r.rating for r in all_reviews]) / total_reviews if total_reviews > 0 else 0
    
    rating_stats = {
        '5': len([r for r in all_reviews if r.rating == 5]),
        '4': len([r for r in all_reviews if r.rating == 4]),
        '3': len([r for r in all_reviews if r.rating == 3]),
        '2': len([r for r in all_reviews if r.rating == 2]),
        '1': len([r for r in all_reviews if r.rating == 1]),
    }
    
    user_email = session.get('user', {}).get('email')
    
    return jsonify({
        'reviews': [r.to_dict(user_email) for r in reviews.items],
        'total': total_reviews,
        'avg_rating': round(avg_rating, 1),
        'rating_stats': rating_stats,
        'has_next': reviews.has_next,
        'has_prev': reviews.has_prev,
        'page': page,
        'pages': reviews.pages
    })

@app.route('/product/<pid>/review', methods=['POST'])
@login_required
def add_review(pid):
    """Add a review for a product"""
    from database import ReviewReply
    
    product = Product.query.get(pid)
    if not product:
        return jsonify({'error': 'Sản phẩm không tồn tại'}), 404
    
    user_email = session['user']['email']
    
    # Check if user already reviewed this product
    existing_review = Review.query.filter_by(product_id=pid, user_email=user_email).first()
    if existing_review:
        return jsonify({'error': 'Bạn đã đánh giá sản phẩm này rồi'}), 400
    
    # Check if user has purchased this product
    user_orders = Order.query.filter_by(user_email=user_email, status='completed').all()
    has_purchased = False
    for order in user_orders:
        order_items = json.loads(order.items)
        # Check both 'product_id' and 'id' keys for compatibility
        if any(item.get('product_id') == pid or item.get('id') == pid for item in order_items):
            has_purchased = True
            break
    
    rating = request.form.get('rating', type=int)
    comment = request.form.get('comment', '')
    size = request.form.get('size', '')
    color = request.form.get('color', '')
    
    if not rating or rating < 1 or rating > 5:
        return jsonify({'error': 'Đánh giá phải từ 1 đến 5 sao'}), 400
    
    # Handle image uploads
    review_images = []
    if 'images' in request.files:
        files = request.files.getlist('images')
        for file in files[:5]:  # Maximum 5 images
            if file and allowed_file(file.filename):
                filename = f"review_{uuid4()}_{secure_filename(file.filename)}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                review_images.append(f"/Images/{filename}")
    
    review = Review(
        product_id=pid,
        user_email=user_email,
        rating=rating,
        comment=comment,
        images=json.dumps(review_images),
        size=size,
        color=color,
        verified_purchase=has_purchased,
        helpful_count=0
    )
    
    db.session.add(review)
    
    # Update product rating
    all_reviews = Review.query.filter_by(product_id=pid).all()
    all_reviews.append(review)
    new_avg_rating = sum([r.rating for r in all_reviews]) / len(all_reviews)
    product.rating = round(new_avg_rating, 1)
    product.reviews = len(all_reviews)
    
    db.session.commit()
    
    flash('Đánh giá của bạn đã được gửi thành công!', 'success')
    return jsonify({'success': True, 'review': review.to_dict()})

@app.route('/review/<int:review_id>/reply', methods=['POST'])
@staff_required
def reply_review(review_id):
    """Admin/Staff reply to a review"""
    from database import ReviewReply
    
    review = Review.query.get(review_id)
    if not review:
        return jsonify({'error': 'Đánh giá không tồn tại'}), 404
    
    comment = request.form.get('comment', '')
    if not comment:
        return jsonify({'error': 'Nội dung phản hồi không được để trống'}), 400
    
    reply = ReviewReply(
        review_id=review_id,
        user_email=session['user']['email'],
        comment=comment
    )
    
    db.session.add(reply)
    db.session.commit()
    
    flash('Phản hồi đã được gửi thành công!', 'success')
    return jsonify({'success': True, 'reply': reply.to_dict()})

@app.route('/review/<int:review_id>/helpful', methods=['POST'])
@login_required
def mark_helpful(review_id):
    """Toggle like/unlike a review (1 user = 1 like max)"""
    review = Review.query.get(review_id)
    if not review:
        return jsonify({'error': 'Đánh giá không tồn tại'}), 404
    
    user_email = session['user']['email']
    
    # Kiểm tra user đã like chưa
    existing_like = ReviewLike.query.filter_by(review_id=review_id, user_email=user_email).first()
    
    if existing_like:
        # Unlike: xóa like
        db.session.delete(existing_like)
        db.session.commit()
        liked = False
    else:
        # Like: thêm like mới
        new_like = ReviewLike(review_id=review_id, user_email=user_email)
        db.session.add(new_like)
        db.session.commit()
        liked = True
    
    # Đếm tổng số like
    total_likes = ReviewLike.query.filter_by(review_id=review_id).count()
    
    return jsonify({
        'success': True,
        'helpful_count': total_likes,
        'liked': liked
    })

@app.route('/reply/<int:reply_id>/edit', methods=['POST'])
@staff_required
def edit_reply(reply_id):
    """Edit a review reply (admin/staff only)"""
    reply = ReviewReply.query.get(reply_id)
    if not reply:
        return jsonify({'error': 'Phản hồi không tồn tại'}), 404
    
    user_email = session['user']['email']
    user_role = session['user']['role']
    
    # Chỉ người tạo reply hoặc admin mới được sửa
    if reply.user_email != user_email and user_role != 'admin':
        return jsonify({'error': 'Bạn không có quyền sửa phản hồi này'}), 403
    
    comment = request.form.get('comment', '').strip()
    if not comment:
        return jsonify({'error': 'Nội dung phản hồi không được để trống'}), 400
    
    reply.comment = comment
    db.session.commit()
    
    return jsonify({'success': True, 'reply': reply.to_dict()})

@app.route('/reply/<int:reply_id>/delete', methods=['POST'])
@staff_required
def delete_reply(reply_id):
    """Delete a review reply (admin/staff only)"""
    reply = ReviewReply.query.get(reply_id)
    if not reply:
        return jsonify({'error': 'Phản hồi không tồn tại'}), 404
    
    user_email = session['user']['email']
    user_role = session['user']['role']
    
    # Chỉ người tạo reply hoặc admin mới được xóa
    if reply.user_email != user_email and user_role != 'admin':
        return jsonify({'error': 'Bạn không có quyền xóa phản hồi này'}), 403
    
    db.session.delete(reply)
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/payment-confirmation/<order_id>')
@login_required
def payment_confirmation(order_id):
    order = Order.query.get(order_id)
    if not order:
        flash('Đơn hàng không tồn tại', 'error')
        return redirect('/my-orders')
    
    # Check if user owns this order
    if order.user_email != session['user']['email']:
        flash('Bạn không có quyền xem đơn hàng này', 'error')
        return redirect('/my-orders')
    
    return render_template('payment_confirmation.html', order=order.to_dict())

@app.route('/order/<order_id>')
@login_required
def order_detail(order_id):
    order = Order.query.get(order_id)
    if not order:
        flash('Đơn hàng không tồn tại', 'error')
        return redirect('/my-orders')
    
    # Check if user owns this order
    if order.user_email != session['user']['email'] and session['user']['role'] != 'admin':
        flash('Bạn không có quyền xem đơn hàng này', 'error')
        return redirect('/my-orders')
    
    order_dict = order.to_dict()
    
    # Kiểm tra sản phẩm nào chưa được đánh giá (nếu đơn hàng completed)
    if order.status == 'completed':
        user_email = session['user']['email']
        for item in order_dict['order_items']:
            product_id = item.get('product_id')
            if product_id:
                # Kiểm tra đã review chưa
                existing_review = Review.query.filter_by(
                    product_id=product_id,
                    user_email=user_email
                ).first()
                item['has_review'] = existing_review is not None
                item['review_id'] = existing_review.id if existing_review else None
            else:
                item['has_review'] = True  # Nếu không có product_id thì coi như đã review
    order_dict = order.to_dict()

# Fix items
    if 'items' not in order_dict:

        if hasattr(order, 'items'):

            try:
                order_dict['items'] = json.loads(order.items)

            except:
                order_dict['items'] = []

        else:
            order_dict['items'] = []
    return render_template('order_detail.html', order=order_dict)

@app.route('/my-orders')
@login_required
def my_orders():

    if session['user']['role'] in ['admin', 'staff']:
        return redirect(url_for('admin_dashboard'))

    user_email = session['user']['email']

    orders = Order.query.filter_by(
        user_email=user_email
    ).all()

    user_orders = [o.to_dict() for o in orders]

    user_orders.sort(
        key=lambda x: x['created_at'],
        reverse=True
    )

    return render_template(
        'my_orders.html',
        orders=user_orders
    )
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user' in session:
        # Redirect to admin panel if already logged in as admin/staff
        if session['user']['role'] in ['admin', 'staff']:
            return redirect('/admin')
        return redirect('/')
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember')
        
        user = User.query.get(email)
        if user and user.password == password:
            session['user'] = {
                'email': email,
                'name': user.name,
                'role': user.role
            }
            flash('Đăng nhập thành công', 'success')
            
            # Auto redirect admin/staff to admin panel
            if user.role in ['admin', 'staff']:
                return redirect('/admin')
            
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect('/')
        else:
            flash('Email hoặc mật khẩu không đúng', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user' in session:
        return redirect('/')
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        name = request.form.get('name')
        phone = request.form.get('phone')
        
        if not all([email, password, confirm_password, name]):
            flash('Vui lòng điền đầy đủ thông tin bắt buộc', 'error')
        elif password != confirm_password:
            flash('Mật khẩu xác nhận không khớp', 'error')
        elif User.query.get(email):
            flash('Email đã tồn tại', 'error')
        else:
            user = User(
                email=email,
                password=password,
                role='user',
                name=name,
                phone=phone,
                address='',
                wishlist='[]',
                created_at=datetime.datetime.now()
            )
            db.session.add(user)
            db.session.commit()
            flash('Đăng ký thành công. Vui lòng đăng nhập.', 'success')
            return redirect('/login')
    
    return render_template('register.html')

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        # In a real app, you would send a password reset email
        flash('Nếu email tồn tại, chúng tôi đã gửi hướng dẫn đặt lại mật khẩu', 'success')
        return redirect('/login')
    
    return render_template('forgot_password.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('cart', None)
    session.pop('voucher_code', None)
    session.pop('voucher_discount', None)
    session.clear()

    flash('Đã đăng xuất thành công', 'success')
    return redirect(url_for('home'))
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user_email = session['user']['email']
    user = User.query.get(user_email)
    
    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        address = request.form.get('address')
        
        if name:
            user.name = name
            session['user']['name'] = name
        
        user.phone = phone
        user.address = address
        
        db.session.commit()
        flash('Cập nhật thông tin thành công', 'success')
        return redirect('/profile')
    
    return render_template('profile.html', user=user.to_dict() if user else {})

@app.route('/change-password', methods=['POST'])
@login_required
def change_password():
    user_email = session['user']['email']
    user = User.query.get(user_email)
    
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    if not current_password or not new_password or not confirm_password:
        flash('Vui lòng điền đầy đủ thông tin', 'error')
    elif user.password != current_password:
        flash('Mật khẩu hiện tại không đúng', 'error')
    elif new_password != confirm_password:
        flash('Mật khẩu xác nhận không khớp', 'error')
    else:
        user.password = new_password
        db.session.commit()
        flash('Đổi mật khẩu thành công', 'success')
    
    return redirect('/profile')

@app.route('/admin/orders')
@staff_required
def admin_orders():
    orders = [o.to_dict() for o in Order.query.all()]
    orders.sort(key=lambda x: x['created_at'], reverse=True)
    return render_template('admin/orders.html', orders=orders)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session or session['user']['role'] != 'admin':
            flash('Bạn không có quyền truy cập trang này', 'error')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin/create-order', methods=['GET', 'POST'])
@admin_required
def admin_create_order():
    if request.method == 'GET':
        # Get all customers for dropdown
        customers = User.query.filter_by(role='user').all()
        products = Product.query.all()
        return render_template('admin/create_order.html', customers=customers, products=products)
    
    if request.method == 'POST':
        # Get form data
        customer_email = request.form.get('customer_email')
        customer_name = request.form.get('customer_name')
        customer_phone = request.form.get('customer_phone')
        customer_address = request.form.get('customer_address')
        payment_method = request.form.get('payment_method')
        payment_status = request.form.get('payment_status')
        notes = request.form.get('notes', '')
        
        # Get products from form (JSON array)
        import json
        products_json = request.form.get('products')
        if not products_json:
            flash('Vui lòng thêm ít nhất 1 sản phẩm', 'error')
            return redirect('/admin/create-order')
        
        try:
            cart_items = json.loads(products_json)
        except:
            flash('Dữ liệu sản phẩm không hợp lệ', 'error')
            return redirect('/admin/create-order')
        
        # Calculate totals
        subtotal = sum(item['price'] * item['qty'] for item in cart_items)
        shipping = 30000 if subtotal < 500000 else 0
        total = subtotal + shipping
        
        # Create order
        order = Order(
            id=str(uuid4()),
            user_email=customer_email,
            items=json.dumps(cart_items),
            shipping_info=json.dumps({
                'name': customer_name,
                'phone': customer_phone,
                'address': customer_address
            }),
            subtotal=subtotal,
            shipping=shipping,
            voucher_discount=0,
            total=total,
            payment_method=payment_method,
            payment_status=payment_status,
            status='pending',
            notes=notes,
            created_at=datetime.datetime.now().strftime('%d/%m/%Y %H:%M')
        )
        
        db.session.add(order)
        db.session.commit()
        save_order_to_apriori_csv(
            order.id,
            cart
        )
        flash(f'Đã tạo đơn hàng #{order.id[:8]} thành công', 'success')
        return redirect('/admin/orders')
    
    # GET request - show form
    products = [p.to_dict() for p in Product.query.all()]
    customers = User.query.filter_by(role='user').all()
    return render_template('admin/create_order.html', products=products, customers=customers)

@app.route('/admin/update-order-status', methods=['POST'])
@staff_required
def update_order_status():
    order_id = request.form.get('order_id')
    status = request.form.get('status')
    
    order = Order.query.get(order_id)
    if order:
        order.status = status
        db.session.commit()
        flash('Cập nhật trạng thái đơn hàng thành công', 'success')
    
    return redirect('/admin/orders')

@app.route('/templates/<template_name>')
def serve_template(template_name):
    return render_template(template_name)


@app.errorhandler(500)
def server_error(error):
    return render_template('500.html'), 500

@app.route('/payment/complete/<order_id>', methods=['POST'])
@login_required
def payment_complete(order_id):
    order = Order.query.get(order_id)
    if not order:
        return jsonify({'success':False}),404
    order.payment_status = 'paid'
    order.status = 'completed'
    db.session.commit()
    return jsonify({'success':True, 'redirect': url_for('home')})

@app.route('/admin/add-product', methods=['GET', 'POST'])
@staff_required
def admin_add_product():
    if request.method == 'POST':
        # Handle image upload
        image_url = ''
        if 'image_file' in request.files:
            file = request.files['image_file']
            if file and file.filename and allowed_file(file.filename):
                # Generate unique filename
                filename = secure_filename(file.filename)
                name, ext = os.path.splitext(filename)
                unique_filename = f"{name}_{uuid4().hex[:8]}{ext}"
                
                # Save file
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(filepath)
                image_url = f"/Images/{unique_filename}"
        
        # If no file uploaded, use URL from input
        if not image_url:
            image_url = request.form.get('image', '')
        
        # Get form values with proper handling of empty strings
        try:
            price = int(request.form.get('price', '0') or '0')
            old_price = int(request.form.get('old_price', '0') or '0')
            stock = int(request.form.get('stock', '0') or '0')
        except ValueError:
            flash('Giá và số lượng phải là số hợp lệ', 'error')
            return redirect('/admin/add-product')
        
        product = Product(
            id=str(uuid4()),
            name=request.form['name'],
            price=price,
            old_price=old_price,
            category=request.form.get('category', ''),
            image=image_url,
            images=json.dumps([image_url]),
            description=request.form.get('description', ''),
            stock=stock,
            sizes=json.dumps([s.strip() for s in request.form.get('sizes', '').split(',') if s.strip()]),
            colors=json.dumps([c.strip() for c in request.form.get('colors', '').split(',') if c.strip()]),
            color_images=json.dumps({}),
            rating=0,
            reviews=0,
            sold=0,
            featured=bool(request.form.get('featured'))
        )
        db.session.add(product)
        db.session.commit()
        flash('Đã thêm sản phẩm', 'success')
        return redirect(url_for('admin_products'))
    return render_template('admin/add_product.html')

@app.route('/admin/add-user', methods=['GET', 'POST'])
@admin_required
def admin_add_user():
    if request.method == 'POST':
        email = request.form.get('email')
        
        if User.query.get(email):
            flash('Email đã tồn tại', 'error')
            return redirect('/admin/add-user')
        
        user = User(
            email=email,
            password=request.form.get('password'),
            name=request.form.get('name'),
            phone=request.form.get('phone', ''),
            address=request.form.get('address', ''),
            role=request.form.get('role', 'user'),
            wishlist='[]',
            created_at=datetime.datetime.now()
        )
        db.session.add(user)
        db.session.commit()
        flash('Đã thêm tài khoản', 'success')
        return redirect('/admin/users')
    
    return render_template('admin/user_form.html', user=None)

@app.route('/admin/edit-user/<email>', methods=['GET', 'POST'])
@admin_required
def admin_edit_user(email):
    user = User.query.get(email)
    if not user:
        flash('Tài khoản không tồn tại', 'error')
        return redirect('/admin/users')
    
    if request.method == 'POST':
        user.name = request.form.get('name')
        user.phone = request.form.get('phone', '')
        user.address = request.form.get('address', '')
        user.role = request.form.get('role', 'user')
        
        new_password = request.form.get('new_password')
        if new_password:
            user.password = new_password
        
        db.session.commit()
        flash('Đã cập nhật tài khoản', 'success')
        return redirect('/admin/users')
    
    return render_template('admin/user_form.html', user=user.to_dict())

@app.route('/admin/delete-user', methods=['POST'])
@admin_required
def admin_delete_user():
    email = request.form.get('email')
    
    # Prevent deleting own account
    if email == session['user']['email']:
        flash('Không thể xóa tài khoản của chính mình', 'error')
        return redirect('/admin/users')
    
    user = User.query.get(email)
    if user:
        db.session.delete(user)
        db.session.commit()
        flash('Đã xóa tài khoản', 'success')
    
    return redirect('/admin/users')

# Admin Product Management
@app.route('/admin/edit-product/<product_id>', methods=['GET', 'POST'])
@staff_required
def admin_edit_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        flash('Sản phẩm không tồn tại', 'error')
        return redirect('/admin/products')
    
    if request.method == 'POST':
        # Handle image upload
        image_url = product.image  # Keep existing image by default
        if 'image_file' in request.files:
            file = request.files['image_file']
            if file and file.filename and allowed_file(file.filename):
                # Generate unique filename
                filename = secure_filename(file.filename)
                name, ext = os.path.splitext(filename)
                unique_filename = f"{name}_{uuid4().hex[:8]}{ext}"
                
                # Save file
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(filepath)
                image_url = f"/Images/{unique_filename}"
        
        # If no file uploaded, check if URL was changed
        if image_url == product.image:
            new_url = request.form.get('image', '')
            if new_url:
                image_url = new_url
        
        # Handle numeric fields safely
        try:
            price = int(request.form.get('price', '0') or '0')
            old_price = int(request.form.get('old_price', '0') or '0')
            stock = int(request.form.get('stock', '0') or '0')
        except ValueError:
            flash('Giá và số lượng phải là số hợp lệ', 'error')
            return redirect(f'/admin/edit-product/{product_id}')
        
        product.name = request.form.get('name')
        product.price = price
        product.old_price = old_price
        product.category = request.form.get('category', '')
        product.image = image_url
        product.images = json.dumps([image_url])
        product.description = request.form.get('description', '')
        product.stock = stock
        product.sizes = json.dumps([s.strip() for s in request.form.get('sizes', '').split(',') if s.strip()])
        product.colors = json.dumps([c.strip() for c in request.form.get('colors', '').split(',') if c.strip()])
        if not product.color_images:
            product.color_images = json.dumps({})
        product.featured = bool(request.form.get('featured'))
        
        db.session.commit()
        flash('Đã cập nhật sản phẩm', 'success')
        return redirect('/admin/products')
    
    return render_template('admin/edit_product.html', product=product.to_dict())

@app.route('/sale')
def sale_products():
    products = Product.query.filter(Product.old_price > Product.price).all()
    sale_products = [p.to_dict() for p in products]
    return render_template('products.html', 
                         products=sale_products,
                         category='',
                         search='',
                         price_range='',
                         sort='',
                         page_title='Sản phẩm khuyến mãi')

@app.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    if 'user' not in session:
        flash('Vui lòng đăng nhập để thêm vào giỏ hàng', 'error')
        return redirect('/login')
    
    pid = request.form.get('pid')
    color = request.form.get('color', 'Trắng')
    size = request.form.get('size', 'M')
    qty = int(request.form.get('qty', 1))
    
    product = Product.query.get(pid)
    if not product:
        flash('Sản phẩm không tồn tại', 'error')
        return redirect('/products')
    
    cart = get_cart()
    
    # Check if product already in cart with same color and size
    existing_item = next((item for item in cart if item['id'] == pid and 
                         item.get('color') == color and item.get('size') == size), None)
    
    if existing_item:
        existing_item['qty'] += qty
    else:
        cart.append({
            'id': pid,
            'name': product.name,
            'price': product.price,
            'image': product.image,
            'color': color,
            'size': size,
            'qty': qty
        })
    session['cart'] = cart

    flash('Đã thêm vào giỏ hàng', 'success')
    
    if request.referrer:
        return redirect(request.referrer)
    return redirect('/products')

@app.route('/wishlist')
@login_required
def wishlist():
    wishlist_ids = get_wishlist()
    wishlist_products = [p.to_dict() for p in Product.query.filter(Product.id.in_(wishlist_ids)).all()]
    return render_template('wishlist.html', wishlist_products=wishlist_products)

@app.route('/review/<int:review_id>/delete', methods=['POST'])
def delete_review(review_id):
    """Delete a review (only by owner or admin)"""
    review = Review.query.get(review_id)
    if not review:
        return jsonify({'error': 'Đánh giá không tồn tại'}), 404
    
    user_email = session.get('user', {}).get('email')
    user_role = session.get('user', {}).get('role')
    
    # Only review owner or admin can delete
    if review.user_email != user_email and user_role != 'admin':
        return jsonify({'error': 'Bạn không có quyền xóa đánh giá này'}), 403
    
    # Update product rating before deleting
    product = Product.query.get(review.product_id)
    if product:
        remaining_reviews = Review.query.filter_by(product_id=review.product_id).filter(Review.id != review_id).all()
        if remaining_reviews:
            new_avg_rating = sum([r.rating for r in remaining_reviews]) / len(remaining_reviews)
            product.rating = round(new_avg_rating, 1)
            product.reviews = len(remaining_reviews)
        else:
            product.rating = 0
            product.reviews = 0
    
    db.session.delete(review)
    db.session.commit()
    
    flash('Đánh giá đã được xóa', 'success')
    return jsonify({'success': True})


@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    cart = get_cart()
    if not cart:
        flash('Giỏ hàng trống', 'error')
        return redirect('/cart')
    
    if request.method == 'POST':
        # Process order
        name = request.form.get('name')
        phone = request.form.get('phone')
        address = request.form.get('address')
        payment_method = request.form.get('payment_method')
        notes = request.form.get('notes', '')
        
        print(f"DEBUG: payment_method from form = {payment_method}")
        
        subtotal, shipping, voucher_discount, total = calculate_cart_totals()
        
        order = Order(
            id=str(uuid4()),
            user_email=session['user']['email'],
            items=json.dumps(cart),
            shipping_info=json.dumps({
                'name': name,
                'phone': phone,
                'address': address
            }),
            subtotal=subtotal,
            shipping=shipping,
            voucher_discount=voucher_discount,
            total=total,
            payment_method=payment_method,
            payment_status='pending' if payment_method in ['banking', 'momo', 'qr'] else 'cod',
            status='pending',
            notes=notes,
            created_at=datetime.datetime.now().strftime('%d/%m/%Y %H:%M')
        )
        
        db.session.add(order)
        db.session.commit()
        
        # =====================================================
        # LƯU THÔNG TIN ĐƠN HÀNG VÀO CSV APRIORI (REALTIME)
        # =====================================================
        try:
            save_order_to_apriori_csv(order.id, cart)
        except Exception as e:
            print("APRIORI CSV SAVE ERROR:", e)
        
        # Clear cart and voucher
        session.pop('cart', None)
        session.pop('voucher_code', None)
        session.pop('voucher_discount', None)
        session.pop('free_shipping', None)
        
        # Redirect to confirmation page for all payment methods
        flash('Đặt hàng thành công!', 'success')
        return redirect(f'/payment-confirmation/{order.id}')
    
    subtotal, shipping, voucher_discount, total = calculate_cart_totals()
    
    # Get user info for pre-filling form
    user_email = session['user']['email']
    user = User.query.get(user_email)
    user_info = user.to_dict() if user else {}
    
    return render_template('checkout.html',
                         cart=cart,
                         subtotal=subtotal,
                         shipping=shipping,
                         voucher_discount=voucher_discount,
                         total=total,
                         user_info=user_info)

@app.route('/payment/<order_id>')
@login_required
def payment_page(order_id):
    order = Order.query.get(order_id)
    if not order:
        flash('Đơn hàng không tồn tại', 'error')
        return redirect('/my-orders')
    
    # Check if user owns this order
    if order.user_email != session['user']['email']:
        flash('Bạn không có quyền xem đơn hàng này', 'error')
        return redirect('/my-orders')
    
    # Generate QR code URL for bank transfer
    bank_info = None
    if order.payment_method in ['banking', 'qr']:
        # VietQR format: https://img.vietqr.io/image/{BANK}-{ACCOUNT_NO}-{TEMPLATE}.png?amount={AMOUNT}&addInfo={INFO}
        bank_info = {
            'name': 'VietcomBank',
            'account': '0123456789',
            'account_name': 'FASHION STORE',
            'qr': f'https://img.vietqr.io/image/VCB-0123456789-compact.png?amount={order.total}&addInfo=ORDER{order.id[:8]}&accountName=FASHION STORE',
            'url': f'https://img.vietqr.io/image/VCB-0123456789-compact.png?amount={order.total}&addInfo=ORDER{order.id[:8]}'
        }
    
    return render_template('payment.html', order=order.to_dict(), bank_info=bank_info)

@app.route('/admin')
@staff_required
def admin_dashboard():
    total_orders = Order.query.count()
    total_products = Product.query.count()
    total_users = User.query.count()

    # Calculate revenue
    completed_orders = Order.query.filter_by(status='completed').all()
    revenue = sum(order.total or 0 for order in completed_orders)

    # Calculate revenue by month and year
    from collections import defaultdict
    revenue_by_month = defaultdict(float)
    revenue_by_year = defaultdict(float)
    orders_by_month = defaultdict(int)
    orders_by_year = defaultdict(int)

    all_orders = Order.query.all()
    for order in all_orders:
        if order.created_at:
            try:
                date_parts = order.created_at.split(' ')[0].split('/')
                if len(date_parts) == 3:
                    day, month, year = date_parts
                    month_key = f"{month}/{year}"
                    year_key = year

                    if order.status == 'completed':
                        revenue_by_month[month_key] += order.total or 0
                        revenue_by_year[year_key] += order.total or 0

                    orders_by_month[month_key] += 1
                    orders_by_year[year_key] += 1
            except Exception:
                pass

    sorted_months = sorted(
        revenue_by_month.items(),
        key=lambda x: (x[0].split('/')[1], x[0].split('/')[0]),
        reverse=True
    )[:12]

    sorted_years = sorted(
        revenue_by_year.items(),
        key=lambda x: x[0],
        reverse=True
    )

    recent_orders = [o.to_dict() for o in Order.query.limit(5).all()]
    recent_orders.sort(key=lambda x: x['created_at'], reverse=True)

    # =========================
    # CUSTOMER PURCHASE ANALYTICS
    # =========================
    customer_stats = []
    users = User.query.filter_by(role='user').all()

    for user in users:
        user_orders = Order.query.filter_by(user_email=user.email).all()

        total_spent = 0
        bought_items = []
        combo_counter = Counter()

        for order in user_orders:
            total_spent += order.total or 0

            try:
                items = json.loads(order.items) if order.items else []
            except Exception:
                items = []

            names = [
                item.get('name', '')
                for item in items
                if item.get('name')
            ]

            bought_items.extend(names)

            for i in range(len(names)):
                for j in range(i + 1, len(names)):
                    combo = f"{names[i]} + {names[j]}"
                    combo_counter[combo] += 1

        customer_stats.append({
            'email': user.email,
            'name': user.name,
            'phone': user.phone,
            'total_orders': len(user_orders),
            'total_spent': total_spent,
            'bought_items': Counter(bought_items).most_common(5),
            'combos': combo_counter.most_common(3)
        })

    customer_stats.sort(key=lambda x: x['total_spent'], reverse=True)

    # =========================
    # APRIORI ASSOCIATION RULES
    # =========================
    transactions = []

    for order in Order.query.all():
        try:
            items = json.loads(order.items) if order.items else []
        except Exception:
            items = []

        names = [
            item.get('name')
            for item in items
            if item.get('name')
        ]

        # Apriori cần đơn có từ 2 sản phẩm trở lên
        if len(names) >= 2:
            transactions.append(names)

    apriori_rules = []
    apriori_chart_labels = []
    apriori_chart_confidence = []

    if transactions:
        try:
            te = TransactionEncoder()
            te_array = te.fit(transactions).transform(transactions)
            df = pd.DataFrame(te_array, columns=te.columns_)

            frequent_itemsets = apriori(
                df,
                min_support=0.005,
                use_colnames=True
            )

            if not frequent_itemsets.empty:
                rules = association_rules(
                    frequent_itemsets,
                    metric='confidence',
                    min_threshold=0.1
                )

                if not rules.empty:
                    rules = rules.sort_values(
                        by=['confidence', 'lift'],
                        ascending=False
                    )

                    for _, row in rules.head(10).iterrows():
                        from_items = ', '.join(list(row['antecedents']))
                        to_items = ', '.join(list(row['consequents']))

                        apriori_rules.append({
                            'from_items': from_items,
                            'to_items': to_items,
                            'support': round(row['support'] * 100, 2),
                            'confidence': round(row['confidence'] * 100, 2),
                            'lift': round(row['lift'], 2)
                        })

                    apriori_chart_labels = [
                        f"{rule['from_items']} → {rule['to_items']}"
                        for rule in apriori_rules[:5]
                    ]

                    apriori_chart_confidence = [
                        rule['confidence']
                        for rule in apriori_rules[:5]
                    ]

        except Exception as e:
            print("Apriori Dashboard Error:", e)

    return render_template(
        'admin/dashboard.html',
        total_orders=total_orders,
        total_products=total_products,
        total_users=total_users,
        revenue=revenue,
        revenue_by_month=sorted_months,
        revenue_by_year=sorted_years,
        orders_by_month=orders_by_month,
        orders_by_year=orders_by_year,
        recent_orders=recent_orders,
        customer_stats=customer_stats,
        apriori_rules=apriori_rules,
        apriori_chart_labels=apriori_chart_labels,
        apriori_chart_confidence=apriori_chart_confidence
    )

@app.route('/admin/products')
@staff_required
def admin_products():
    products = [p.to_dict() for p in Product.query.all()]
    return render_template('admin/products.html', products=products)

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


# Admin User Management
@app.route('/admin/users')
@admin_required
def admin_users():

    role_filter = request.args.get('role', 'all')

    if role_filter == 'all':
        users = User.query.all()
    else:
        users = User.query.filter_by(role=role_filter).all()

    users_data = []

    for u in users:

        user_dict = u.to_dict()

        user_dict['order_count'] = Order.query.filter_by(
            user_email=u.email,
            status='completed'
        ).count()

        users_data.append(user_dict)

    all_count = User.query.count()
    admin_count = User.query.filter_by(role='admin').count()
    staff_count = User.query.filter_by(role='staff').count()
    user_count = User.query.filter_by(role='user').count()

    return render_template(
        'admin/users.html',
        users=users_data,
        role=role_filter,
        all_count=all_count,
        admin_count=admin_count,
        staff_count=staff_count,
        user_count=user_count
    )


@app.route('/admin/delete-product', methods=['POST'])
@admin_required
def admin_delete_product():
    product_id = request.form.get('product_id')
    product = Product.query.get(product_id)
    
    if product:
        db.session.delete(product)
        db.session.commit()
        flash('Đã xóa sản phẩm', 'success')
    
    return redirect('/admin/products')

@app.route('/admin/delete-order', methods=['POST'])
@admin_required
def admin_delete_order():
    order_id = request.form.get('order_id')
    order = Order.query.get(order_id)
    
    if order:
        db.session.delete(order)
        db.session.commit()
        flash(f'Đã xóa đơn hàng #{order_id[:8]}', 'success')
    else:
        flash('Đơn hàng không tồn tại', 'error')
    
    return redirect('/admin/orders')


@app.route('/admin/edit-order/<order_id>', methods=['GET', 'POST'])
@staff_required
def admin_edit_order(order_id):
    order = Order.query.get(order_id)

    if not order:
        flash('Đơn hàng không tồn tại', 'error')
        return redirect('/admin/orders')

    if request.method == 'POST':
        shipping_info = json.loads(order.shipping_info) if order.shipping_info else {}

        shipping_info['name'] = request.form.get('customer_name')
        shipping_info['phone'] = request.form.get('customer_phone')
        shipping_info['address'] = request.form.get('customer_address')

        order.shipping_info = json.dumps(shipping_info)
        order.payment_method = request.form.get('payment_method')
        order.payment_status = request.form.get('payment_status')
        order.status = request.form.get('status')
        order.notes = request.form.get('notes', '')

        products_json = request.form.get('products')

        if products_json:
            try:
                cart_items = json.loads(products_json)
                order.items = products_json

                subtotal = sum(
                    item['price'] * item['qty']
                    for item in cart_items
                )

                shipping = 0 if subtotal >= 500000 else 30000
                voucher_discount = order.voucher_discount or 0
                total = subtotal + shipping - voucher_discount

                order.subtotal = subtotal
                order.shipping = shipping
                order.total = total

            except Exception as e:
                print("Edit order products error:", e)
                flash('Dữ liệu sản phẩm không hợp lệ', 'error')
                return redirect(f'/admin/edit-order/{order_id}')

        db.session.commit()

        flash(f'Đã cập nhật đơn hàng #{order_id[:8]}', 'success')
        return redirect('/admin/orders')

    order_dict = order.to_dict()

    products = [
        p.to_dict()
        for p in Product.query.all()
    ]

    return render_template(
    'admin/edit_order.html',
    order=order_dict,
    order_items=order_dict.get('order_items', []),
    products=products
)
@app.route('/admin/statistics')
@staff_required
def admin_statistics():
    customer_stats = []
    apriori_rules = []

    chart_labels = []
    chart_values = []

    total_invoices = 0
    total_products = 0
    total_rules = 0
    max_confidence = 0
    max_lift = 0

    transactions = []

    # ====================================
    # ĐỌC DỮ LIỆU TỪ FILE CSV APRIORI
    # ====================================

    try:

        df = pd.read_csv(
            'data/du_lieu_apriori.csv',
            encoding='utf-8'
        )

        invoices = df.groupby(
            'InvoiceID'
        )['Category'].apply(list)

        transactions = invoices.tolist()

        total_invoices = len(invoices)

        total_products = len(
            set(
                item
                for trans in transactions
                for item in trans
            )
        )

    except Exception as e:

        print("CSV ERROR:", e)

        transactions = []

    # ====================================
    # THỐNG KÊ KHÁCH HÀNG
    # ====================================

    users = User.query.filter_by(role='user').all()

    for user in users:

        user_orders = Order.query.filter_by(
            user_email=user.email
        ).all()

        total_spent = 0

        bought_items = []

        combo_counter = Counter()

        for order in user_orders:

            total_spent += order.total or 0

            try:
                items = json.loads(order.items) if order.items else []
            except:
                items = []

            names = [
                item.get('name')
                for item in items
                if item.get('name')
            ]

            bought_items.extend(names)

            for i in range(len(names)):
                for j in range(i + 1, len(names)):
                    combo_counter[
                        f"{names[i]} + {names[j]}"
                    ] += 1

        customer_stats.append({

            'email': user.email,

            'name': user.name,

            'phone': user.phone,

            'total_orders': len(user_orders),

            'total_spent': total_spent,

            'bought_items': Counter(
                bought_items
            ).most_common(5),

            'combos': combo_counter.most_common(3)

        })

    customer_stats.sort(
        key=lambda x: x['total_spent'],
        reverse=True
    )

    # ====================================
    # APRIORI
    # ====================================

    if transactions:

        try:

            te = TransactionEncoder()

            te_data = te.fit(
                transactions
            ).transform(
                transactions
            )

            basket = pd.DataFrame(
                te_data,
                columns=te.columns_
            )

            frequent_itemsets = apriori(
                basket,
                min_support=0.01,
                use_colnames=True
            )

            if not frequent_itemsets.empty:

                rules = association_rules(
                    frequent_itemsets,
                    metric='confidence',
                    min_threshold=0.1
                )

                rules = rules.sort_values(
                    by='confidence',
                    ascending=False
                )

                total_rules = len(rules)

                if not rules.empty:

                    max_confidence = round(
                        rules['confidence'].max() * 100,
                        2
                    )

                    max_lift = round(
                        rules['lift'].max(),
                        2
                    )

                for _, row in rules.head(10).iterrows():

                    from_items = ', '.join(
                        list(row['antecedents'])
                    )

                    to_items = ', '.join(
                        list(row['consequents'])
                    )

                    apriori_rules.append({

                        'from_items': from_items,

                        'to_items': to_items,

                        'support': round(
                            row['support'] * 100,
                            2
                        ),

                        'confidence': round(
                            row['confidence'] * 100,
                            2
                        ),

                        'lift': round(
                            row['lift'],
                            2
                        )

                    })

                    chart_labels.append(
                        f"{from_items} → {to_items}"
                    )

                    chart_values.append(
                        round(
                            row['confidence'] * 100,
                            2
                        )
                    )

        except Exception as e:

            print(
                "Apriori statistics error:",
                e
            )

    return render_template(

        'admin/statistics.html',

        customer_stats=customer_stats,

        apriori_rules=apriori_rules,

        chart_labels=chart_labels,

        chart_values=chart_values,

        total_invoices=total_invoices,

        total_products=total_products,

        total_rules=total_rules,

        max_confidence=max_confidence,

        max_lift=max_lift

    )

    # GET request
    order_dict = order.to_dict()
    products = [p.to_dict() for p in Product.query.all()]
    return render_template('admin/edit_order.html', order=order_dict, products=products)

def save_order_to_apriori_csv(order_id, cart):
    csv_file = 'data/du_lieu_apriori.csv'

    os.makedirs('data', exist_ok=True)

    file_exists = os.path.isfile(csv_file)

    with open(
        csv_file,
        mode='a',
        newline='',
        encoding='utf-8'
    ) as f:

        writer = csv.writer(f)

        if not file_exists:
            writer.writerow([
                'InvoiceID', 'ProductID', 'ProductName', 'Category', 
                'Size', 'Color', 'Quantity', 'Price', 'OrderDate'
            ])

        order_date_str = datetime.datetime.now().strftime("%d/%m/%Y")

        for item in cart:

            product = Product.query.get(
                item['id']
            )

            if product:

                writer.writerow([
                    order_id,
                    product.id,
                    product.name,
                    product.category,
                    item.get('size', 'M'),
                    item.get('color', 'Đen'),
                    item.get('qty', 1),
                    product.price,
                    order_date_str
                ])

if __name__ == '__main__':
    print("=" * 50)
    print("Flask Clothing Store Starting...")
    print("Server will be available at: http://127.0.0.1:5000")
    print("Press CTRL+C to stop the server")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)