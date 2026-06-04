"""
SQLite Database Configuration for Flask Clothing Store
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

# Models
class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    old_price = db.Column(db.Integer, default=0)
    category = db.Column(db.String(100))
    image = db.Column(db.String(500))
    images = db.Column(db.Text)  # JSON array
    description = db.Column(db.Text)
    stock = db.Column(db.Integer, default=0)
    sizes = db.Column(db.Text)  # JSON array
    colors = db.Column(db.Text)  # JSON array
    color_images = db.Column(db.Text)  # JSON object mapping colors to image URLs
    rating = db.Column(db.Float, default=0.0)
    reviews = db.Column(db.Integer, default=0)
    sold = db.Column(db.Integer, default=0)
    featured = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'old_price': self.old_price,
            'category': self.category,
            'image': self.image,
            'images': json.loads(self.images) if self.images else [],
            'description': self.description,
            'stock': self.stock,
            'sizes': json.loads(self.sizes) if self.sizes else [],
            'colors': json.loads(self.colors) if self.colors else [],
            'color_images': json.loads(self.color_images) if self.color_images else {},
            'rating': self.rating,
            'reviews': self.reviews,
            'sold': self.sold,
            'featured': self.featured,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class User(db.Model):
    __tablename__ = 'users'
    
    email = db.Column(db.String(120), primary_key=True)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='user')
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    wishlist = db.Column(db.Text)  # JSON array
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # Relationships
    orders = db.relationship('Order', backref='user', lazy=True)
    
    def to_dict(self):
        return {
            'email': self.email,
            'password': self.password,
            'role': self.role,
            'name': self.name,
            'phone': self.phone,
            'address': self.address,
            'wishlist': json.loads(self.wishlist) if self.wishlist else [],
            'orders': [order.id for order in self.orders],
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.String(36), primary_key=True)
    user_email = db.Column(db.String(120), db.ForeignKey('users.email'), nullable=False)
    items = db.Column(db.Text, nullable=False)  # JSON array
    shipping_info = db.Column(db.Text)  # JSON object
    subtotal = db.Column(db.Integer, nullable=False)
    shipping = db.Column(db.Integer, default=0)
    voucher_discount = db.Column(db.Integer, default=0)
    total = db.Column(db.Integer, nullable=False)
    payment_method = db.Column(db.String(50))
    payment_status = db.Column(db.String(20), default='pending')
    status = db.Column(db.String(20), default='pending')
    notes = db.Column(db.Text)
    created_at = db.Column(db.String(50))
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_email': self.user_email,
            'order_items': json.loads(self.items) if self.items else [],
            'shipping_info': json.loads(self.shipping_info) if self.shipping_info else {},
            'subtotal': self.subtotal,
            'shipping': self.shipping,
            'voucher_discount': self.voucher_discount,
            'total': self.total,
            'payment_method': self.payment_method,
            'payment_status': self.payment_status,
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at
        }


class Review(db.Model):
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_id = db.Column(db.String(36), nullable=False)
    user_email = db.Column(db.String(120), nullable=False)
    order_id = db.Column(db.String(36))  # Đơn hàng đã mua
    rating = db.Column(db.Integer, nullable=False)  # 1-5 sao
    comment = db.Column(db.Text)
    images = db.Column(db.Text)  # JSON array - ảnh đánh giá
    size = db.Column(db.String(10))  # Size đã mua
    color = db.Column(db.String(50))  # Màu đã mua
    verified_purchase = db.Column(db.Boolean, default=False)  # Đã mua hàng
    helpful_count = db.Column(db.Integer, default=0)  # Số lượt hữu ích
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # Relationship với phản hồi
    replies = db.relationship('ReviewReply', backref='review', lazy=True, cascade='all, delete-orphan')
    likes = db.relationship('ReviewLike', backref='review', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self, user_email=None):
        user = User.query.filter_by(email=self.user_email).first()
        # Đếm số lượt like thực tế từ ReviewLike table
        actual_helpful_count = ReviewLike.query.filter_by(review_id=self.id).count()
        # Kiểm tra user hiện tại đã like chưa
        user_liked = False
        if user_email:
            user_liked = ReviewLike.query.filter_by(review_id=self.id, user_email=user_email).first() is not None
        
        return {
            'id': self.id,
            'product_id': self.product_id,
            'user_email': self.user_email,
            'user_name': user.name if user else 'Người dùng',
            'order_id': self.order_id,
            'rating': self.rating,
            'comment': self.comment,
            'images': json.loads(self.images) if self.images else [],
            'size': self.size,
            'color': self.color,
            'verified_purchase': self.verified_purchase,
            'helpful_count': actual_helpful_count,
            'user_liked': user_liked,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'replies': [reply.to_dict() for reply in self.replies]
        }


class ReviewReply(db.Model):
    __tablename__ = 'review_replies'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    review_id = db.Column(db.Integer, db.ForeignKey('reviews.id'), nullable=False)
    user_email = db.Column(db.String(120), nullable=False)  # Admin/Staff
    comment = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    def to_dict(self):
        user = User.query.filter_by(email=self.user_email).first()
        return {
            'id': self.id,
            'review_id': self.review_id,
            'user_email': self.user_email,
            'user_name': user.name if user else 'Quản trị viên',
            'user_role': user.role if user else 'admin',
            'comment': self.comment,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class ReviewLike(db.Model):
    __tablename__ = 'review_likes'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    review_id = db.Column(db.Integer, db.ForeignKey('reviews.id'), nullable=False)
    user_email = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # Unique constraint: 1 user chỉ like 1 review 1 lần
    __table_args__ = (db.UniqueConstraint('review_id', 'user_email', name='unique_review_like'),)


class Voucher(db.Model):
    __tablename__ = 'vouchers'
    
    code = db.Column(db.String(50), primary_key=True)
    discount = db.Column(db.Integer, nullable=False)
    min_order = db.Column(db.Integer, default=0)
    type = db.Column(db.String(20), nullable=False)  # fixed, percent, shipping
    active = db.Column(db.Boolean, default=True)
    
    def to_dict(self):
        return {
            'code': self.code,
            'discount': self.discount,
            'min_order': self.min_order,
            'type': self.type,
            'active': self.active
        }


def init_db(app):
    """Initialize database with Flask app"""
    db.init_app(app)
    
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Initialize with sample data if empty
        if User.query.count() == 0:
            init_sample_data()


def init_sample_data():
    """Initialize database with sample data"""
    from uuid import uuid4
    
    # Create admin user
    admin = User(
        email='admin@example.com',
        password='admin123',
        role='admin',
        name='Admin',
        phone='0901234567',
        address='123 Nguyễn Huệ, Q1, TP.HCM',
        wishlist='[]',
        created_at=datetime.now()
    )
    db.session.add(admin)
    
    # Create staff user
    staff = User(
        email='staff@example.com',
        password='staff123',
        role='staff',
        name='Nhân Viên',
        phone='0907654321',
        address='456 Lê Lợi, Q1, TP.HCM',
        wishlist='[]',
        created_at=datetime.now()
    )
    db.session.add(staff)
    
    # Create sample products
    products_data = [
        {
            "name": "Áo thun Basic",
            "price": 199000,
            "old_price": 299000,
            "category": "Áo thun",
            "image": "/Images/thuntrang.png",
            "images": ["/Images/thuntrang.png", "/Images/thunden.png", "/Images/thunau.png"],
            "description": "Áo thun cotton mềm, phù hợp mọi lứa tuổi. Chất liệu thấm hút mồ hôi tốt.",
            "stock": 50,
            "sizes": ["S", "M", "L", "XL"],
            "colors": ["Trắng", "Đen", "Nâu"],
            "color_images": {
                "Trắng": "/Images/thuntrang.png",
                "Đen": "/Images/thunden.png",
                "Nâu": "/Images/thunau.png"
            },
            "rating": 4.0,
            "reviews": 1,
            "sold": 340,
            "featured": True
        },
        {
            "name": "Áo khoác Hoodie",
            "price": 399000,
            "old_price": 599000,
            "category": "Áo khoác",
            "image": "/Images/hoodiexam.png",
            "images": ["/Images/hoodiexam.png", "/Images/hoodiexanhnavy.png", "/Images/hoodienau.png"],
            "description": "Hoodie ấm, thiết kế trẻ trung. Form rộng thoải mái.",
            "stock": 30,
            "sizes": ["M", "L", "XL", "XXL"],
            "colors": ["Xám", "Xanh navy", "Nâu"],
            "color_images": {
                "Xám": "/Images/hoodiexam.png",
                "Xanh navy": "/Images/hoodiexanhnavy.png",
                "Nâu": "/Images/hoodienau.png"
            },
            "rating": 4.5,
            "reviews": 2,
            "sold": 156,
            "featured": True
        },
        {
            "name": "Quần Jeans Nam",
            "price": 549000,
            "old_price": 749000,
            "category": "Quần",
            "image": "/Images/jeanxanhdam.png",
            "images": ["/Images/jeanxanhdam.png", "/Images/jeanxanhnhat.png", "/Images/jeanden.png"],
            "description": "Quần jeans co giãn, ôm vừa. Chất liệu denim cao cấp.",
            "stock": 20,
            "sizes": ["28", "29", "30", "31", "32"],
            "colors": ["Xanh đậm", "Xanh nhạt", "Đen"],
            "color_images": {
                "Xanh đậm": "/Images/jeanxanhdam.png",
                "Xanh nhạt": "/Images/jeanxanhnhat.png",
                "Đen": "/Images/jeanden.png"
            },
            "rating": 4.5,
            "reviews": 2,
            "sold": 445,
            "featured": True
        },
        {
            "name": "Áo sơ mi Công sở",
            "price": 279000,
            "old_price": 399000,
            "category": "Áo sơ mi",
            "image": "/Images/somitrang.png",
            "images": ["/Images/somitrang.png", "/Images/somixanh.png", "/Images/sominau.png"],
            "description": "Áo sơ mi lịch sự, phù hợp văn phòng.",
            "stock": 45,
            "sizes": ["S", "M", "L", "XL"],
            "colors": ["Trắng", "Xanh nhạt", "Nâu"],
            "color_images": {
                "Trắng": "/Images/somitrang.png",
                "Xanh nhạt": "/Images/somixanh.png",
                "Nâu": "/Images/sominau.png"
            },
            "rating": 4.5,
            "reviews": 2,
            "sold": 189,
            "featured": True
        },
        {
            "name": "Váy dài",
            "price": 459000,
            "old_price": 599000,
            "category": "Váy",
            "image": "/Images/vaybe.png",
            "images": ["/Images/vaybe.png", "/Images/vayxanh.png"],
            "description": "Váy dài phong cách vintage, sang trọng.",
            "stock": 15,
            "sizes": ["S", "M", "L"],
            "colors": ["Be", "Xanh"],
            "color_images": {
                "Be": "/Images/vaybe.png",
                "Xanh": "/Images/vayxanh.png"
            },
            "rating": 0.0,
            "reviews": 0,
            "sold": 78,
            "featured": False
        },
        {
            "name": "Quần short Nam",
            "price": 189000,
            "old_price": 259000,
            "category": "Quần",
            "image": "/Images/shortden.png",
            "images": ["/Images/shortden.png", "/Images/shortxanh.png"],
            "description": "Quần short thoáng mát, phù hợp tập luyện.",
            "stock": 60,
            "sizes": ["M", "L", "XL"],
            "colors": ["Đen", "Xanh"],
            "color_images": {
                "Đen": "/Images/shortden.png",
                "Xanh": "/Images/shortxanh.png"
            },
            "rating": 0.0,
            "reviews": 0,
            "sold": 567,
            "featured": False
        },
        {
            "name": "Áo len phong cách cho nam",
            "price": 789000,
            "old_price": 999000,
            "category": "Áo len",
            "image": "/Images/lenxam.png",
            "images": ["/Images/lenxam.png", "/Images/lenden.png", "/Images/lennavy.png"],
            "description": "Áo len cashmere cao cấp, giữ ấm tốt.",
            "stock": 25,
            "sizes": ["S", "M", "L"],
            "colors": ["Xám", "Đen", "Navy"],
            "color_images": {
                "Xám": "/Images/lenxam.png",
                "Đen": "/Images/lenden.png",
                "Navy": "/Images/lennavy.png"
            },
            "rating": 0.0,
            "reviews": 0,
            "sold": 123,
            "featured": False
        },
        {
            "name": "Áo Body Giữ Nhiệt Bamboo Cổ Tròn",
            "price": 329000,
            "old_price": 429000,
            "category": "Áo body",
            "image": "/Images/bodytrang.png",
            "images": ["/Images/bodytrang.png", "/Images/bodyden.png"],
            "description": "Áo Body Giữ Nhiệt Bamboo Cổ Tròn thanh lịch, dễ phối đồ.",
            "stock": 35,
            "sizes": ["S", "M", "L"],
            "colors": ["Trắng", "Đen"],
            "color_images": {
                "Trắng": "/Images/bodytrang.png",
                "Đen": "/Images/bodyden.png"
            },
            "rating": 0.0,
            "reviews": 0,
            "sold": 98,
            "featured": False
        },
        {
        "name": "Áo Hoodie Basic",
        "price": 399000,
        "old_price": 499000,
        "category": "Áo khoác",
        "image": "/Images/hoodie1.png",
        "images": ["/Images/hoodie1.png"],
        "description": "Hoodie basic form rộng trẻ trung.",
        "stock": 25,
        "sizes": ["M", "L", "XL"],
        "colors": ["Đen", "Nâu"],
        "color_images": {"Nâu": "/Images/hoodie1.png"},
        "color_images": {"Đen": "/Images/hoodie1den.png"},
        "rating": 4.7,
        "reviews": 15,
        "sold": 120,
        "featured": True
    },

    {
        "name": "Áo Thun Local Brand",
        "price": 199000,
        "old_price": 259000,
        "category": "Áo thun",
        "image": "/Images/aothun1.png",
        "images": ["/Images/aothun1.png"],
        "description": "Áo thun cotton mềm mịn.",
        "stock": 50,
        "sizes": ["S", "M", "L"],
        "colors": ["Xám", "Trắng"],
        "color_images": {"Xám": "/Images/aothun1.png"},
        "color_images": {"Trắng": "/Images/aothun1trang.png"},
        "rating": 4.5,
        "reviews": 18,
        "sold": 220,
        "featured": True
    },

    {
        "name": "Quần Jeans Slimfit",
        "price": 549000,
        "old_price": 650000,
        "category": "Quần",
        "image": "/Images/jean1.png",
        "images": ["/Images/jean1.png"],
        "description": "Jeans co giãn form slimfit.",
        "stock": 30,
        "sizes": ["29", "30", "31", "32"],
        "colors": ["Xanh đậm"],
        "color_images": {"Xanh đậm": "/Images/jean1.png"},
        "rating": 4.6,
        "reviews": 12,
        "sold": 95,
        "featured": True
    },

    {
        "name": "Áo Sơ Mi Công Sở",
        "price": 299000,
        "old_price": 399000,
        "category": "Áo sơ mi",
        "image": "/Images/somi1.png",
        "images": ["/Images/somi1.png"],
        "description": "Áo sơ mi thanh lịch cho dân văn phòng.",
        "stock": 35,
        "sizes": ["M", "L", "XL"],
        "colors": ["Trắng", "Xanh"],
        "color_images": {"Trắng": "/Images/somi1trang.png"},
        "color_images": {"Xanh": "/Images/somi1.png"},
        "rating": 4.4,
        "reviews": 9,
        "sold": 60,
        "featured": True
    },

    {
        "name": "Váy Tennis Nữ",
        "price": 280000,
        "old_price": 350000,
        "category": "Váy",
        "image": "/Images/vay1.png",
        "images": ["/Images/vay1.png"],
        "description": "Váy tennis trẻ trung năng động.",
        "stock": 20,
        "sizes": ["S", "M"],
        "colors": ["Trắng"],
        "color_images": {"Trắng": "/Images/vay1.png"},
        "rating": 4.7,
        "reviews": 22,
        "sold": 110,
        "featured": True
    },

    {
        "name": "Áo Cardigan Hàn Quốc",
        "price": 430000,
        "old_price": 520000,
        "category": "Cardigan",
        "image": "/Images/cardigan1.png",
        "images": ["/Images/cardigan1.png"],
        "description": "Cardigan phong cách Hàn Quốc.",
        "stock": 18,
        "sizes": ["M", "L"],
        "colors": ["Trắng", "Đen"],
        "color_images": {"Trắng": "/Images/cardigan1.png"},
        "color_images": {"Đen": "/Images/cardigan1den.png"},
        "rating": 4.8,
        "reviews": 11,
        "sold": 70,
        "featured": True
    },

    {
        "name": "Áo Blazer Nữ",
        "price": 720000,
        "old_price": 850000,
        "category": "Blazer",
        "image": "/Images/blazer1.png",
        "images": ["/Images/blazer1.png"],
        "description": "Blazer nữ sang trọng.",
        "stock": 12,
        "sizes": ["S", "M", "L"],
        "colors": ["Be", "Đen"],
        "color_images": {"Be": "/Images/blazer1.png"},
        "color_images": {"Đen": "/Images/blazer1den.png"},
        "rating": 4.6,
        "reviews": 10,
        "sold": 45,
        "featured": True
    },

    {
        "name": "Nón Lưỡi Trai Basic",
        "price": 120000,
        "old_price": 180000,
        "category": "Nón",
        "image": "/Images/non1.png",
        "images": ["/Images/non1.png"],
        "description": "Nón basic dễ phối đồ.",
        "stock": 40,
        "sizes": ["FreeSize"],
        "colors": ["Đen", "Trắng"],
        "color_images": {"Đen": "/Images/non1.png"},
        "color_images": {"Trắng": "/Images/non1trang.png"},
        "rating": 4.3,
        "reviews": 14,
        "sold": 150,
        "featured": True
    },

    {
        "name": "Giày Sneaker Trắng",
        "price": 650000,
        "old_price": 790000,
        "category": "Giày",
        "image": "/Images/giay1.png",
        "images": ["/Images/giay1.png"],
        "description": "Sneaker trắng basic unisex.",
        "stock": 22,
        "sizes": ["38", "39", "40", "41"],
        "colors": ["Trắng"],
        "color_images": {"Trắng": "/Images/giay1.png"},
        "rating": 4.9,
        "reviews": 31,
        "sold": 250,
        "featured": True
    },

    {
        "name": "Quần Jogger Nam",
        "price": 320000,
        "old_price": 390000,
        "category": "Quần",
        "image": "/Images/jogger1.png",
        "images": ["/Images/jogger1.png"],
        "description": "Jogger form rộng trẻ trung.",
        "stock": 28,
        "sizes": ["M", "L", "XL"],
        "colors": ["Đen", "Xám"],
        "color_images": {"Đen": "/Images/jogger1.png"},
        "color_images": {"Xám": "/Images/jogger1xam.png"},
        "rating": 4.5,
        "reviews": 16,
        "sold": 130,
        "featured": True
    }
    ]
    
    for p_data in products_data:
        product = Product(
            id=str(uuid4()),
            name=p_data['name'],
            price=p_data['price'],
            old_price=p_data['old_price'],
            category=p_data['category'],
            image=p_data['image'],
            images=json.dumps(p_data['images']),
            description=p_data['description'],
            stock=p_data['stock'],
            sizes=json.dumps(p_data['sizes']),
            colors=json.dumps(p_data['colors']),
            color_images=json.dumps(p_data.get('color_images', {})),
            rating=p_data['rating'],
            reviews=p_data['reviews'],
            sold=p_data['sold'],
            featured=p_data.get('featured', False)
        )
        db.session.add(product)
    
    db.session.commit()  # Commit products first to get IDs
    
    # Get product IDs for reviews
    product_ao_thun = Product.query.filter_by(name="Áo thun Basic").first()
    product_hoodie = Product.query.filter_by(name="Áo khoác Hoodie").first()
    product_jeans = Product.query.filter_by(name="Quần Jeans Nam").first()
    product_somi = Product.query.filter_by(name="Áo sơ mi Công sở").first()
    
    # Create sample users for reviews
    sample_users = [
        User(email='nguyen.van.a@gmail.com', password='user123', role='user', name='Nguyễn Văn A', 
             phone='0901111111', address='123 Lê Văn Việt, Q9, TP.HCM', wishlist='[]'),
        User(email='tran.thi.b@gmail.com', password='user123', role='user', name='Trần Thị B',
             phone='0902222222', address='456 Nguyễn Văn Linh, Q7, TP.HCM', wishlist='[]'),
        User(email='le.van.c@gmail.com', password='user123', role='user', name='Lê Văn C',
             phone='0903333333', address='789 Võ Văn Ngân, Thủ Đức, TP.HCM', wishlist='[]'),
        User(email='pham.thi.d@gmail.com', password='user123', role='user', name='Phạm Thị D',
             phone='0904444444', address='321 Điện Biên Phủ, Q3, TP.HCM', wishlist='[]'),
        User(email='hoang.van.e@gmail.com', password='user123', role='user', name='Hoàng Văn E',
             phone='0905555555', address='654 Lý Thường Kiệt, Q10, TP.HCM', wishlist='[]'),
    ]
    for user in sample_users:
        db.session.add(user)
    
    db.session.commit()
    
    # Create sample orders for users (để họ có thể đánh giá sản phẩm)
    sample_orders = [
        Order(
            id=str(uuid4()),
            user_email='nguyen.van.a@gmail.com',
            items=json.dumps([
                {"product_id": product_ao_thun.id, "name": "Áo thun Basic", "price": 199000, "quantity": 2, "size": "M", "color": "Trắng", "image": "/Images/thuntrang.png"},
                {"product_id": product_jeans.id, "name": "Quần Jeans Nam", "price": 549000, "quantity": 1, "size": "30", "color": "Xanh đậm", "image": "/Images/jeanxanhdam.png"}
            ]),
            shipping_info=json.dumps({
                "name": "Nguyễn Văn A",
                "phone": "0901111111",
                "address": "123 Lê Văn Việt, Q9, TP.HCM"
            }),
            subtotal=947000,
            shipping=30000,
            voucher_discount=0,
            total=977000,
            payment_method='cod',
            payment_status='completed',
            status='completed',
            notes='Giao hàng nhanh',
            created_at='2024-11-10 10:00:00'
        ),
        Order(
            id=str(uuid4()),
            user_email='tran.thi.b@gmail.com',
            items=json.dumps([
                {"product_id": product_ao_thun.id, "name": "Áo thun Basic", "price": 199000, "quantity": 1, "size": "L", "color": "Đen", "image": "/Images/thunden.png"}
            ]),
            shipping_info=json.dumps({
                "name": "Trần Thị B",
                "phone": "0902222222",
                "address": "456 Nguyễn Văn Linh, Q7, TP.HCM"
            }),
            subtotal=199000,
            shipping=30000,
            voucher_discount=0,
            total=229000,
            payment_method='bank',
            payment_status='completed',
            status='completed',
            notes='',
            created_at='2024-11-08 14:30:00'
        ),
        Order(
            id=str(uuid4()),
            user_email='le.van.c@gmail.com',
            items=json.dumps([
                {"product_id": product_ao_thun.id, "name": "Áo thun Basic", "price": 199000, "quantity": 1, "size": "XL", "color": "Nâu", "image": "/Images/thunau.png"},
                {"product_id": product_jeans.id, "name": "Quần Jeans Nam", "price": 549000, "quantity": 1, "size": "31", "color": "Xanh đậm", "image": "/Images/jeanxanhdam.png"}
            ]),
            shipping_info=json.dumps({
                "name": "Lê Văn C",
                "phone": "0903333333",
                "address": "789 Võ Văn Ngân, Thủ Đức, TP.HCM"
            }),
            subtotal=748000,
            shipping=30000,
            voucher_discount=50000,
            total=728000,
            payment_method='momo',
            payment_status='completed',
            status='completed',
            notes='Dùng mã GIAM50K',
            created_at='2024-11-12 09:15:00'
        ),
        Order(
            id=str(uuid4()),
            user_email='pham.thi.d@gmail.com',
            items=json.dumps([
                {"product_id": product_somi.id, "name": "Áo sơ mi Công sở", "price": 279000, "quantity": 2, "size": "M", "color": "Trắng", "image": "/Images/somitrang.png"}
            ]),
            shipping_info=json.dumps({
                "name": "Phạm Thị D",
                "phone": "0904444444",
                "address": "321 Điện Biên Phủ, Q3, TP.HCM"
            }),
            subtotal=558000,
            shipping=30000,
            voucher_discount=0,
            total=588000,
            payment_method='cod',
            payment_status='completed',
            status='completed',
            notes='',
            created_at='2024-10-25 16:45:00'
        ),
        Order(
            id=str(uuid4()),
            user_email='hoang.van.e@gmail.com',
            items=json.dumps([
                {"product_id": product_hoodie.id, "name": "Áo khoác Hoodie", "price": 399000, "quantity": 1, "size": "L", "color": "Xám", "image": "/Images/hoodiexam.png"}
            ]),
            shipping_info=json.dumps({
                "name": "Hoàng Văn E",
                "phone": "0905555555",
                "address": "654 Lý Thường Kiệt, Q10, TP.HCM"
            }),
            subtotal=399000,
            shipping=30000,
            voucher_discount=30000,
            total=399000,
            payment_method='bank',
            payment_status='completed',
            status='completed',
            notes='Dùng mã FREESHIP',
            created_at='2024-11-05 11:20:00'
        )
    ]
    
    for order in sample_orders:
        db.session.add(order)
    
    db.session.commit()
    
    # Create sample reviews with detailed feedback
    if product_ao_thun:
        reviews_ao_thun = [
            Review(
                product_id=product_ao_thun.id,
                user_email='pham.thi.d@gmail.com',
                rating=4,
                comment='Áo ok, nhưng size hơi rộng so với size thông thường. Nên chọn size nhỏ hơn 1 size. Chất vải mát, thấm hút tốt.',
                size='S',
                color='Trắng',
                verified_purchase=False,
                helpful_count=0,
                created_at=datetime(2024, 10, 28, 16, 45)
            )
        ]
        for review in reviews_ao_thun:
            db.session.add(review)
    
    if product_hoodie:
        reviews_hoodie = [
            Review(
                product_id=product_hoodie.id,
                user_email='nguyen.van.a@gmail.com',
                rating=5,
                comment='Mua lần thứ 2 rồi! Lần đầu mua màu xanh navy, giờ mua thêm màu nâu. Chất lượng ổn định, giá tốt.',
                size='XL',
                color='Nâu',
                verified_purchase=False,
                helpful_count=0,
                created_at=datetime(2024, 11, 8, 13, 30)
            ),
            Review(
                product_id=product_hoodie.id,
                user_email='tran.thi.b@gmail.com',
                rating=4,
                comment='Áo đẹp, ấm, nhưng hơi nặng. Thích hợp cho mùa đông. Túi hoodie rộng rãi, tiện lợi.',
                size='M',
                color='Xanh navy',
                verified_purchase=False,
                helpful_count=0,
                created_at=datetime(2024, 10, 30, 15, 20)
            )
        ]
        for review in reviews_hoodie:
            db.session.add(review)
    
    if product_jeans:
        reviews_jeans = [
            Review(
                product_id=product_jeans.id,
                user_email='pham.thi.d@gmail.com',
                rating=4,
                comment='Quần đẹp, chất denim dày dặn. Hơi khó mặc lúc đầu nhưng sau khi giặt thì vừa hơn. Đường may chắc chắn.',
                size='29',
                color='Xanh nhạt',
                verified_purchase=False,
                helpful_count=0,
                created_at=datetime(2024, 11, 6, 14, 30)
            ),
            Review(
                product_id=product_jeans.id,
                user_email='hoang.van.e@gmail.com',
                rating=5,
                comment='Mặc rất thoải mái, không bị gò bó. Màu đen sang trọng, dễ phối áo. Túi sau sâu, tiện lợi.',
                size='31',
                color='Đen',
                verified_purchase=False,
                helpful_count=0,
                created_at=datetime(2024, 10, 25, 9, 45)
            )
        ]
        for review in reviews_jeans:
            db.session.add(review)
    
    if product_somi:
        reviews_somi = [
            Review(
                product_id=product_somi.id,
                user_email='nguyen.van.a@gmail.com',
                rating=4,
                comment='Áo sơ mi lịch sự, phù hợp đi làm. Chất vải hơi dễ nhăn, cần là ủi. Màu trắng tinh không ngả vàng.',
                size='L',
                color='Trắng',
                verified_purchase=False,
                helpful_count=0,
                created_at=datetime(2024, 11, 9, 8, 30)
            ),
            Review(
                product_id=product_somi.id,
                user_email='tran.thi.b@gmail.com',
                rating=5,
                comment='Áo đẹp, form chuẩn công sở. Chất vải mỏng nhẹ, mặc mát. Màu xanh nhạt rất dễ thương, không quá nổi.',
                size='M',
                color='Xanh nhạt',
                verified_purchase=False,
                helpful_count=0,
                created_at=datetime(2024, 11, 3, 16, 0)
            )
        ]
        for review in reviews_somi:
            db.session.add(review)
    
    db.session.commit()
    
    # Create review replies from admin and staff
    review_1 = Review.query.filter_by(user_email='pham.thi.d@gmail.com', product_id=product_ao_thun.id).first()
    if review_1:
        reply_1 = ReviewReply(
            review_id=review_1.id,
            user_email='admin@example.com',
            comment='Cảm ơn bạn đã nhận xét! Shop đã cập nhật bảng size chi tiết hơn để khách hàng dễ chọn size phù hợp. Mong bạn tiếp tục ủng hộ!',
            created_at=datetime(2024, 10, 29, 10, 15)
        )
        db.session.add(reply_1)
    
    review_2 = Review.query.filter_by(user_email='nguyen.van.a@gmail.com', product_id=product_hoodie.id).first()
    if review_2:
        reply_2 = ReviewReply(
            review_id=review_2.id,
            user_email='staff@example.com',
            comment='Rất vui khi bạn hài lòng với sản phẩm! Cảm ơn bạn đã ủng hộ shop nhiều lần! 🔥',
            created_at=datetime(2024, 11, 8, 18, 30)
        )
        db.session.add(reply_2)
    
    review_3 = Review.query.filter_by(user_email='nguyen.van.a@gmail.com', product_id=product_somi.id).first()
    if review_3:
        reply_3 = ReviewReply(
            review_id=review_3.id,
            user_email='admin@example.com',
            comment='Cảm ơn bạn đã góp ý! Sản phẩm áo sơ mi của shop làm từ vải cotton cao cấp nên cần là ủi để đẹp nhất nhé!',
            created_at=datetime(2024, 11, 9, 14, 0)
        )
        db.session.add(reply_3)
    
    # Create vouchers
    vouchers_data = [
        {"code": "GIAM50K", "discount": 50000, "min_order": 500000, "type": "fixed", "active": True},
        {"code": "SALE20", "discount": 20, "min_order": 300000, "type": "percent", "active": True},
        {"code": "FREESHIP", "discount": 30000, "min_order": 0, "type": "shipping", "active": True},
        {"code": "WELCOME10", "discount": 10, "min_order": 200000, "type": "percent", "active": True}
    ]
    
    for v_data in vouchers_data:
        voucher = Voucher(
            code=v_data['code'],
            discount=v_data['discount'],
            min_order=v_data['min_order'],
            type=v_data['type'],
            active=v_data['active']
        )
        db.session.add(voucher)
    
    # Commit all changes
    db.session.commit()
