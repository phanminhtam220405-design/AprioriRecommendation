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
            "name": "Áo Thun Nam Basic",
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
            "name": "Áo Hoodie Unisex",
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
            "name": "Áo Sơ Mi Nữ Công Sở",
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
            "name": "Váy Nữ Dài",
            "price": 459000,
            "old_price": 599000,
            "category": "Váy",
            "image": "/Images/vaybe.png",
            "images": ["/Images/vaybe.png", "/Images/vayxanh.png"],
            "description": "Váy Nữ Dài phong cách vintage, sang trọng.",
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
            "name": "Áo Body Nữ Giữ Nhiệt Bamboo Cổ Tròn",
            "price": 329000,
            "old_price": 429000,
            "category": "Áo body",
            "image": "/Images/bodytrang.png",
            "images": ["/Images/bodytrang.png", "/Images/bodyden.png"],
            "description": "Áo Body Nữ Giữ Nhiệt Bamboo Cổ Tròn thanh lịch, dễ phối đồ.",
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
        "name": "Áo Hoodie Unisex Basic",
        "price": 399000,
        "old_price": 499000,
        "category": "Áo khoác",
        "image": "/Images/hoodie1.png",
        "images": ["/Images/hoodie1.png"],
        "description": "Hoodie basic form rộng trẻ trung.",
        "stock": 25,
        "sizes": ["M", "L", "XL"],
        "colors": ["Đen", "Nâu"],
        "color_images": {
            "Nâu": "/Images/hoodie1.png",
            "Đen": "/Images/hoodie1den.png"
            },

        "rating": 4.7,
        "reviews": 15,
        "sold": 120,
        "featured": True
    },

    {
        "name": "Áo Thun Nam Local Brand",
        "price": 199000,
        "old_price": 259000,
        "category": "Áo thun",
        "image": "/Images/aothun1.png",
        "images": ["/Images/aothun1.png"],
        "description": "Áo thun cotton mềm mịn.",
        "stock": 50,
        "sizes": ["S", "M", "L"],
        "colors": ["Xám", "Trắng"],
        "color_images": {"Xám": "/Images/aothun1.png",
                         "Trắng": "/Images/aothun1trang.png"
                         },
        "rating": 4.5,
        "reviews": 18,
        "sold": 220,
        "featured": True
    },

    {
        "name": "Quần Jeans Nam Slimfit",
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
        "name": "Áo Sơ Mi Nữ Công Sở",
        "price": 299000,
        "old_price": 399000,
        "category": "Áo sơ mi",
        "image": "/Images/somi1.png",
        "images": ["/Images/somi1.png"],
        "description": "Áo sơ mi thanh lịch cho dân văn phòng.",
        "stock": 35,
        "sizes": ["M", "L", "XL"],
        "colors": ["Trắng", "Xanh"],
        "color_images": {"Trắng": "/Images/somi1trang.png",
                         "Xanh": "/Images/somi1.png"
                         },
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
        "name": "Cardigan Nữ Hàn Quốc",
        "price": 430000,
        "old_price": 520000,
        "category": "Cardigan",
        "image": "/Images/cardigan1.png",
        "images": ["/Images/cardigan1.png"],
        "description": "Cardigan phong cách Hàn Quốc.",
        "stock": 18,
        "sizes": ["M", "L"],
        "colors": ["Trắng", "Đen"],
        "color_images": {"Trắng": "/Images/cardigan1.png",
                         "Đen": "/Images/cardigan1den.png"
                         },
        "rating": 4.8,
        "reviews": 11,
        "sold": 70,
        "featured": True
    },

    {
        "name": "Blazer Nữ Basic",
        "price": 720000,
        "old_price": 850000,
        "category": "Blazer",
        "image": "/Images/blazer1.png",
        "images": ["/Images/blazer1.png"],
        "description": "Blazer nữ sang trọng.",
        "stock": 12,
        "sizes": ["S", "M", "L"],
        "colors": ["Be", "Đen"],
        "color_images": {"Be": "/Images/blazer1.png",
                         "Đen": "/Images/blazer1den.png"
                         },
        "rating": 4.6,
        "reviews": 10,
        "sold": 45,
        "featured": True
    },

    {
        "name": "Nón Lưỡi Trai Basic Unisex",
        "price": 120000,
        "old_price": 180000,
        "category": "Nón",
        "image": "/Images/non1.png",
        "images": ["/Images/non1.png"],
        "description": "Nón basic dễ phối đồ.",
        "stock": 40,
        "sizes": ["FreeSize"],
        "colors": ["Đen", "Trắng"],
        "color_images": {"Đen": "/Images/non1.png",
                         "Trắng": "/Images/non1trang.png"
                         },
        "rating": 4.3,
        "reviews": 14,
        "sold": 150,
        "featured": True
    },

    {
        "name": "Giày Sneaker Trắng Unisex",
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
        "color_images": {"Đen": "/Images/jogger1.png", 
                         "Xám": "/Images/jogger1xam.png"
                         },
        "rating": 4.5,
        "reviews": 16,
        "sold": 130,
        "featured": True
    },
    {
    "name": "Áo Thun Nam Oversize Streetwear",
    "price": 239000,
    "old_price": 299000,
    "category": "Áo thun",
    "image": "/Images/Streetwear.png",
    "images": ["/Images/Streetwear.png"],
    "description": "Áo thun oversize phong cách streetwear trẻ trung.",
    "stock": 40,
    "sizes": ["M","L","XL"],
    "colors": ["Đen","Trắng"],
    "color_images": {
        "Đen": "/Images/Streetwear.png",
        "Trắng": "/Images/Streetweartrang.png"
    },
    "rating": 4.7,
    "reviews": 12,
    "sold": 165,
    "featured": True
    },

    {
        "name": "Áo Polo Nam Basic",
        "price": 279000,
        "old_price": 349000,
        "category": "Áo thun",
        "image": "/Images/aothun3.png",
        "images": ["/Images/aothun3.png"],
        "description": "Áo polo lịch sự phù hợp đi làm.",
        "stock": 35,
        "sizes": ["S","M","L","XL"],
        "colors": ["Xanh Navy","Trắng"],
        "color_images": {
            "Xanh Navy": "/Images/aothun3.png",
            "Trắng": "/Images/aothun3trang.png"
        },
        "rating": 4.5,
        "reviews": 18,
        "sold": 180,
        "featured": False
    },

    {
        "name": "Áo Thun Nam Graphic Print",
        "price": 259000,
        "old_price": 319000,
        "category": "Áo thun",
        "image": "/Images/aothun4.png",
        "images": ["/Images/aothun4.png"],
        "description": "Áo thun in họa tiết phong cách trẻ.",
        "stock": 50,
        "sizes": ["M","L","XL"],
        "colors": ["Xám","Đen"],
        "color_images": {
            "Xám": "/Images/aothun4.png",
            "Đen": "/Images/aothun4den.png"
        },
        "rating": 4.6,
        "reviews": 20,
        "sold": 210,
        "featured": False
    },
    {
        "name": "Áo Khoác Nam Bomber",
        "price": 499000,
        "old_price": 599000,
        "category": "Áo khoác",
        "image": "/Images/bomber1.png",
        "images": ["/Images/bomber1.png"],
        "description": "Bomber cá tính phong cách Hàn Quốc.",
        "stock": 20,
        "sizes": ["M","L","XL"],
        "colors": ["Đen"],
        "color_images": {
            "Đen": "/Images/bomber1.png"
        },
        "rating": 4.8,
        "reviews": 9,
        "sold": 95,
        "featured": True
    },

    {
        "name": "Áo Khoác Nam Denim",
        "price": 559000,
        "old_price": 690000,
        "category": "Áo khoác",
        "image": "/Images/denim1.png",
        "images": ["/Images/denim1.png"],
        "description": "Áo khoác jean denim thời trang.",
        "stock": 18,
        "sizes": ["M","L","XL"],
        "colors": ["Xanh"],
        "color_images": {
            "Xanh": "/Images/denim1.png"
        },
        "rating": 4.6,
        "reviews": 11,
        "sold": 77,
        "featured": False
    },

    {
        "name": "Áo Khoác Nam Varsity",
        "price": 639000,
        "old_price": 799000,
        "category": "Áo khoác",
        "image": "/Images/varsity1.png",
        "images": ["/Images/varsity1.png"],
        "description": "Áo khoác varsity trẻ trung năng động.",
        "stock": 22,
        "sizes": ["M","L","XL"],
        "colors": ["Đen Trắng"],
        "color_images": {
            "Đen Trắng": "/Images/varsity1.png"
        },
        "rating": 4.8,
        "reviews": 13,
        "sold": 104,
        "featured": True
    },
    {
        "name": "Quần Kaki Nam Slimfit",
        "price": 389000,
        "old_price": 459000,
        "category": "Quần",
        "image": "/Images/kaki1.png",
        "images": ["/Images/kaki1.png"],
        "description": "Quần kaki slimfit lịch sự.",
        "stock": 25,
        "sizes": ["29","30","31","32"],
        "colors": ["Kem"],
        "color_images": {
            "Kem": "/Images/kaki1.png"
        },
        "rating": 4.5,
        "reviews": 10,
        "sold": 120,
        "featured": False
    },
    {
        "name": "Áo Sơ Mi Nữ Oxford",
        "price": 329000,
        "old_price": 399000,
        "category": "Áo sơ mi",
        "image": "/Images/oxford1.png",
        "images": ["/Images/oxford1.png"],
        "description": "Sơ mi Oxford cao cấp.",
        "stock": 30,
        "sizes": ["M","L","XL"],
        "colors": ["Trắng"],
        "color_images": {
            "Trắng": "/Images/oxford1.png"
        },
        "rating": 4.7,
        "reviews": 12,
        "sold": 130,
        "featured": False
    },

    {
        "name": "Áo Sơ Mi Nam Caro",
        "price": 299000,
        "old_price": 379000,
        "category": "Áo sơ mi",
        "image": "/Images/caro1.png",
        "images": ["/Images/caro1.png"],
        "description": "Sơ mi caro phong cách trẻ.",
        "stock": 28,
        "sizes": ["M","L"],
        "colors": ["Đỏ"],
        "color_images": {
            "Đỏ": "/Images/caro1.png"
        },
        "rating": 4.5,
        "reviews": 9,
        "sold": 88,
        "featured": False
    },

    {
        "name": "Áo Sơ Mi Nữ Linen",
        "price": 359000,
        "old_price": 449000,
        "category": "Áo sơ mi",
        "image": "/Images/linen1.png",
        "images": ["/Images/linen1.png"],
        "description": "Sơ mi linen thoáng mát.",
        "stock": 25,
        "sizes": ["S","M","L"],
        "colors": ["Be"],
        "color_images": {
            "Be": "/Images/linen1.png"
        },
        "rating": 4.8,
        "reviews": 11,
        "sold": 92,
        "featured": True
    },
    {
        "name": "Giày Running Sport Unisex",
        "price": 790000,
        "old_price": 990000,
        "category": "Giày",
        "image": "/Images/giay2.png",
        "images": ["/Images/giay2.png"],
        "description": "Giày chạy bộ thể thao chuyên dụng.",
        "stock": 20,
        "sizes": ["39","40","41","42"],
        "colors": ["Đen"],
        "color_images": {
            "Đen": "/Images/giay2.png"
        },
        "rating": 4.9,
        "reviews": 22,
        "sold": 170,
        "featured": True
    },

    {
        "name": "Giày Chunky Sneaker Unisex",
        "price": 850000,
        "old_price": 990000,
        "category": "Giày",
        "image": "/Images/giay3.png",
        "images": ["/Images/giay3.png"],
        "description": "Chunky sneaker phong cách Hàn Quốc.",
        "stock": 18,
        "sizes": ["38","39","40","41"],
        "colors": ["Trắng"],
        "color_images": {
            "Trắng": "/Images/giay3.png"
        },
        "rating": 4.8,
        "reviews": 17,
        "sold": 132,
        "featured": True
    },

    {
        "name": "Giày Slip On Unisex",
        "price": 499000,
        "old_price": 599000,
        "category": "Giày",
        "image": "/Images/giay4.png",
        "images": ["/Images/giay4.png"],
        "description": "Giày slip on tiện lợi.",
        "stock": 25,
        "sizes": ["39","40","41"],
        "colors": ["Đen"],
        "color_images": {
            "Đen": "/Images/giay4.png"
        },
        "rating": 4.4,
        "reviews": 8,
        "sold": 75,
        "featured": False
    },

    {
        "name": "Giày Thể Thao Nam",
        "price": 720000,
        "old_price": 850000,
        "category": "Giày",
        "image": "/Images/giay5.png",
        "images": ["/Images/giay5.png"],
        "description": "Giày thể thao nam cao cấp.",
        "stock": 20,
        "sizes": ["40","41","42"],
        "colors": ["Xám"],
        "color_images": {
            "Xám": "/Images/giay5.png"
        },
        "rating": 4.8,
        "reviews": 19,
        "sold": 145,
        "featured": True
    },
    {
    "name": "Váy Công Sở Nữ",
    "price": 390000,
    "old_price": 490000,
    "category": "Váy",
    "image": "/Images/vay3.png",
    "images": ["/Images/vay3.png"],
    "description": "Váy công sở thanh lịch dành cho nữ.",
    "stock": 25,
    "sizes": ["S","M","L","XL"],
    "colors": ["Đen","Kem"],
    "color_images": {"Đen":"/Images/vay3.png"},
    "rating": 4.7,
    "reviews": 28,
    "sold": 180,
    "featured": True,
    },
    {
        "name": "Váy Nữ Hoa Vintage",
        "price": 450000,
        "old_price": 580000,
        "category": "Váy",
        "image": "/Images/vay4.png",
        "images": ["/Images/vay4.png"],
        "description": "Phong cách vintage nhẹ nhàng.",
        "stock": 20,
        "sizes": ["S","M","L"],
        "colors": ["Hồng"],
        "color_images": {"Hồng":"/Images/vay4.png"},
        "rating": 4.8,
        "reviews": 35,
        "sold": 220,
        "featured": True
    },
    {
        "name": "Váy Nữ Dự Tiệc Cao Cấp",
        "price": 690000,
        "old_price": 850000,
        "category": "Váy",
        "image": "/Images/vay5.png",
        "images": ["/Images/vay5.png"],
        "description": "Thiết kế sang trọng cho các buổi tiệc.",
        "stock": 15,
        "sizes": ["S","M","L"],
        "colors": ["Đỏ","Đen"],
        "color_images": {"Đỏ":"/Images/vay5.png"},
        "rating": 4.9,
        "reviews": 41,
        "sold": 165,
        "featured": True
    },
    {
        "name": "Áo Len Nam Cổ Lọ",
        "price": 520000,
        "old_price": 650000,
        "category": "Áo len",
        "image": "/Images/aolen2.png",
        "images": ["/Images/aolen2.png"],
        "description": "Giữ ấm mùa đông cực tốt.",
        "stock": 22,
        "sizes": ["M","L","XL"],
        "colors": ["Đen","Xám"],
        "color_images": {"Đen":"/Images/aolen2.png"},
        "rating": 4.8,
        "reviews": 22,
        "sold": 140,
        "featured": True
    },
    {
        "name": "Áo Len Nam Hàn Quốc",
        "price": 499000,
        "old_price": 620000,
        "category": "Áo len",
        "image": "/Images/aolen3.png",
        "images": ["/Images/aolen3.png"],
        "description": "Phong cách trẻ trung hiện đại.",
        "stock": 30,
        "sizes": ["M","L","XL"],
        "colors": ["Kem","Nâu"],
        "color_images": {"Kem":"/Images/aolen3.png"},
        "rating": 4.7,
        "reviews": 19,
        "sold": 160,
        "featured": True
    },
    {
        "name": "Áo Len Nam Dệt Kim",
        "price": 469000,
        "old_price": 590000,
        "category": "Áo len",
        "image": "/Images/aolen4.png",
        "images": ["/Images/aolen4.png"],
        "description": "Chất liệu mềm mại thoải mái.",
        "stock": 28,
        "sizes": ["M","L","XL"],
        "colors": ["Trắng"],
        "color_images": {"Trắng":"/Images/aolen4.png"},
        "rating": 4.6,
        "reviews": 18,
        "sold": 130,
        "featured": False
    },
    {
        "name": "Áo Len Nam Form Rộng",
        "price": 559000,
        "old_price": 690000,
        "category": "Áo len",
        "image": "/Images/aolen5.png",
        "images": ["/Images/aolen5.png"],
        "description": "Phong cách oversize năng động.",
        "stock": 16,
        "sizes": ["L","XL"],
        "colors": ["Xám"],
        "color_images": {"Xám":"/Images/aolen5.png"},
        "rating": 4.8,
        "reviews": 25,
        "sold": 120,
        "featured": True
    },
    {
        "name": "Áo Body Nữ Tay Dài",
        "price": 299000,
        "old_price": 380000,
        "category": "Áo body",
        "image": "/Images/body2.png",
        "images": ["/Images/body2.png"],
        "description": "Ôm dáng nhẹ nhàng.",
        "stock": 25,
        "sizes": ["S","M","L"],
        "colors": ["Đen"],
        "color_images": {"Đen":"/Images/body2.png"},
        "rating": 4.7,
        "reviews": 17,
        "sold": 140,
        "featured": True
    },
    {
        "name": "Áo Body Nữ Basic",
        "price": 269000,
        "old_price": 340000,
        "category": "Áo body",
        "image": "/Images/body3.png",
        "images": ["/Images/body3.png"],
        "description": "Thiết kế đơn giản dễ phối đồ.",
        "stock": 32,
        "sizes": ["S","M","L"],
        "colors": ["Trắng"],
        "color_images": {"Trắng":"/Images/body3.png"},
        "rating": 4.6,
        "reviews": 13,
        "sold": 155,
        "featured": False
    },
    {
        "name": "Áo Body Nữ Cổ Vuông",
        "price": 329000,
        "old_price": 420000,
        "category": "Áo body",
        "image": "/Images/body4.png",
        "images": ["/Images/body4.png"],
        "description": "Phong cách nữ tính hiện đại.",
        "stock": 20,
        "sizes": ["S","M","L"],
        "colors": ["Hồng"],
        "color_images": {"Hồng":"/Images/body4.png"},
        "rating": 4.8,
        "reviews": 22,
        "sold": 180,
        "featured": True
    },
    {
        "name": "Áo Body Nữ Croptop",
        "price": 289000,
        "old_price": 350000,
        "category": "Áo body",
        "image": "/Images/body5.png",
        "images": ["/Images/body5.png"],
        "description": "Croptop body cá tính.",
        "stock": 18,
        "sizes": ["S","M"],
        "colors": ["Đen"],
        "color_images": {"Đen":"/Images/body5.png"},
        "rating": 4.9,
        "reviews": 20,
        "sold": 165,
        "featured": True
    },
    {
    "name": "Cardigan Nữ Len Mỏng",
    "price": 399000,
    "old_price": 520000,
    "category": "Cardigan",
    "image": "/Images/cardigan2.png",
    "images": ["/Images/cardigan2.png"],
    "description": "Cardigan len mỏng nhẹ phù hợp thời tiết se lạnh.",
    "stock": 25,
    "sizes": ["S","M","L"],
    "colors": ["Kem","Xám"],
    "color_images": {"Kem":"/Images/cardigan2.png"},
    "rating": 4.8,
    "reviews": 21,
    "sold": 170,
    "featured": True
},
{
    "name": "Cardigan Nữ Oversize",
    "price": 459000,
    "old_price": 590000,
    "category": "Cardigan",
    "image": "/Images/cardigan3.png",
    "images": ["/Images/cardigan3.png"],
    "description": "Form rộng trẻ trung phong cách Hàn Quốc.",
    "stock": 20,
    "sizes": ["M","L","XL"],
    "colors": ["Nâu"],
    "color_images": {"Nâu":"/Images/cardigan3.png"},
    "rating": 4.7,
    "reviews": 18,
    "sold": 150,
    "featured": True
},
{
    "name": "Cardigan Nữ Dệt Kim",
    "price": 499000,
    "old_price": 650000,
    "category": "Cardigan",
    "image": "/Images/cardigan4.png",
    "images": ["/Images/cardigan4.png"],
    "description": "Chất liệu dệt kim mềm mại cao cấp.",
    "stock": 18,
    "sizes": ["M","L"],
    "colors": ["Be"],
    "color_images": {"Be":"/Images/cardigan4.png"},
    "rating": 4.9,
    "reviews": 27,
    "sold": 135,
    "featured": True
},
{
    "name": "Cardigan Nữ Basic",
    "price": 379000,
    "old_price": 480000,
    "category": "Cardigan",
    "image": "/Images/cardigan5.png",
    "images": ["/Images/cardigan5.png"],
    "description": "Thiết kế đơn giản dễ phối đồ.",
    "stock": 22,
    "sizes": ["S","M","L"],
    "colors": ["Trắng"],
    "color_images": {"Trắng":"/Images/cardigan5.png"},
    "rating": 4.6,
    "reviews": 15,
    "sold": 120,
    "featured": False
},
{
    "name": "Blazer Nữ Hàn Quốc",
    "price": 790000,
    "old_price": 990000,
    "category": "Blazer",
    "image": "/Images/blazer2.png",
    "images": ["/Images/blazer2.png"],
    "description": "Phong cách trẻ trung hiện đại.",
    "stock": 18,
    "sizes": ["M","L"],
    "colors": ["Kem"],
    "color_images": {"Kem":"/Images/blazer2.png"},
    "rating": 4.8,
    "reviews": 23,
    "sold": 145,
    "featured": True
},
{
    "name": "Blazer Nữ Form Rộng",
    "price": 850000,
    "old_price": 1050000,
    "category": "Blazer",
    "image": "/Images/blazer3.png",
    "images": ["/Images/blazer3.png"],
    "description": "Thiết kế oversize thời thượng.",
    "stock": 20,
    "sizes": ["L","XL"],
    "colors": ["Xám"],
    "color_images": {"Xám":"/Images/blazer3.png"},
    "rating": 4.7,
    "reviews": 20,
    "sold": 120,
    "featured": True
},

{
    "name": "Blazer Nữ Công Sở",
    "price": 820000,
    "old_price": 980000,
    "category": "Blazer",
    "image": "/Images/blazer4.png",
    "images": ["/Images/blazer4.png"],
    "description": "Tôn dáng và sang trọng.",
    "stock": 17,
    "sizes": ["S","M","L"],
    "colors": ["Trắng"],
    "color_images": {"Trắng":"/Images/blazer4.png"},
    "rating": 4.8,
    "reviews": 22,
    "sold": 138,
    "featured": True
},
{
    "name": "Blazer Nữ Premium",
    "price": 990000,
    "old_price": 1290000,
    "category": "Blazer",
    "image": "/Images/blazer5.png",
    "images": ["/Images/blazer5.png"],
    "description": "Dòng cao cấp chất liệu nhập khẩu.",
    "stock": 10,
    "sizes": ["M","L","XL"],
    "colors": ["Đen"],
    "color_images": {"Đen":"/Images/blazer5.png"},
    "rating": 5.0,
    "reviews": 35,
    "sold": 90,
    "featured": True
},
{
    "name": "Nón Bucket Basic Unisex",
    "price": 180000,
    "old_price": 250000,
    "category": "Nón",
    "image": "/Images/non2.png",
    "images": ["/Images/non2.png"],
    "description": "Bucket thời trang cá tính.",
    "stock": 30,
    "sizes": ["Free Size"],
    "colors": ["Đen"],
    "color_images": {"Đen":"/Images/non2.png"},
    "rating": 4.6,
    "reviews": 12,
    "sold": 160,
    "featured": False
},
{
    "name": "Nón Snapback Unisex",
    "price": 220000,
    "old_price": 290000,
    "category": "Nón",
    "image": "/Images/non3.png",
    "images": ["/Images/non3.png"],
    "description": "Phong cách đường phố năng động.",
    "stock": 28,
    "sizes": ["Free Size"],
    "colors": ["Xám"],
    "color_images": {"Xám":"/Images/non3.png"},
    "rating": 4.7,
    "reviews": 17,
    "sold": 180,
    "featured": True
},
{
    "name": "Nón Thể Thao Unisex",
    "price": 190000,
    "old_price": 250000,
    "category": "Nón",
    "image": "/Images/non4.png",
    "images": ["/Images/non4.png"],
    "description": "Thấm hút mồ hôi tốt.",
    "stock": 35,
    "sizes": ["Free Size"],
    "colors": ["Trắng"],
    "color_images": {"Trắng":"/Images/non4.png"},
    "rating": 4.8,
    "reviews": 20,
    "sold": 230,
    "featured": True
},
{
    "name": "Nón Lưỡi Trai Cao Cấp Unisex",
    "price": 250000,
    "old_price": 320000,
    "category": "Nón",
    "image": "/Images/non5.png",
    "images": ["/Images/non5.png"],
    "description": "Thiết kế hiện đại cao cấp.",
    "stock": 18,
    "sizes": ["Free Size"],
    "colors": ["Navy"],
    "color_images": {"Navy":"/Images/non5.png"},
    "rating": 4.9,
    "reviews": 22,
    "sold": 145,
    "featured": True
},
{
    "name": "Quần Jeans Nữ Skinny",
    "price": 489000,
    "old_price": 599000,
    "category": "Quần",
    "image": "/Images/quan_nu_1.png",
    "images": ["/Images/quan_nu_1.png"],
    "description": "Quần jeans nữ skinny ôm dáng.",
    "stock": 30,
    "sizes": ["S","M","L"],
    "colors": ["Xanh"],
    "color_images": {"Xanh": "/Images/quan_nu_1.png"},
    "rating": 4.8,
    "reviews": 18,
    "sold": 160,
    "featured": True
},

{
    "name": "Quần Baggy Nữ",
    "price": 429000,
    "old_price": 529000,
    "category": "Quần",
    "image": "/Images/quan_nu_2.png",
    "images": ["/Images/quan_nu_2.png"],
    "description": "Quần baggy nữ trẻ trung.",
    "stock": 25,
    "sizes": ["S","M","L"],
    "colors": ["Đen"],
    "color_images": {"Đen": "/Images/quan_nu_2.png"},
    "rating": 4.7,
    "reviews": 15,
    "sold": 400,
    "featured": True
},

{
    "name": "Quần Tây Nữ Công Sở",
    "price": 459000,
    "old_price": 559000,
    "category": "Quần",
    "image": "/Images/quan_nu_3.png",
    "images": ["/Images/quan_nu_3.png"],
    "description": "Quần tây nữ công sở thanh lịch.",
    "stock": 20,
    "sizes": ["S","M","L"],
    "colors": ["Đen"],
    "color_images": {"Đen": "/Images/quan_nu_3.png"},
    "rating": 4.9,
    "reviews": 20,
    "sold": 175,
    "featured": True
},

{
    "name": "Quần Ống Rộng Nữ",
    "price": 399000,
    "old_price": 499000,
    "category": "Quần",
    "image": "/Images/quan_nu_4.png",
    "images": ["/Images/quan_nu_4.png"],
    "description": "Quần ống rộng nữ thời trang.",
    "stock": 28,
    "sizes": ["S","M","L"],
    "colors": ["Kem"],
    "color_images": {"Kem": "/Images/quan_nu_4.png"},
    "rating": 4.8,
    "reviews": 17,
    "sold": 350,
    "featured": True
},

{
    "name": "Quần Short Nữ",
    "price": 259000,
    "old_price": 329000,
    "category": "Quần",
    "image": "/Images/quan_nu_5.png",
    "images": ["/Images/quan_nu_5.png"],
    "description": "Quần short nữ năng động.",
    "stock": 35,
    "sizes": ["S","M","L"],
    "colors": ["Xanh"],
    "color_images": {"Xanh": "/Images/quan_nu_5.png"},
    "rating": 4.6,
    "reviews": 13,
    "sold": 290,
    "featured": True
},

{
    "name": "Quần Culottes Nữ",
    "price": 379000,
    "old_price": 469000,
    "category": "Quần",
    "image": "/Images/quan_nu_6.png",
    "images": ["/Images/quan_nu_6.png"],
    "description": "Quần culottes nữ hiện đại.",
    "stock": 18,
    "sizes": ["S","M","L"],
    "colors": ["Be"],
    "color_images": {"Be": "/Images/quan_nu_6.png"},
    "rating": 4.7,
    "reviews": 11,
    "sold": 110,
    "featured": True
},
    ]

    new_products = [
        # --- 25 MALE PRODUCTS ---
        {"name": "Áo Thun Nam Trơn Cổ Tròn", "price": 150000, "old_price": 220000, "category": "Áo thun", "image": "/Images/thuntrang.png", "images": ["/Images/thuntrang.png", "/Images/thunden.png"], "description": "Áo thun nam 100% cotton trơn thoáng mát, co giãn tốt.", "stock": 50, "sizes": ["S", "M", "L", "XL"], "colors": ["Trắng", "Đen"], "color_images": {"Trắng": "/Images/thuntrang.png", "Đen": "/Images/thunden.png"}, "rating": 4.5, "reviews": 12, "sold": 120, "featured": False},
        {"name": "Áo Thun Nam Cổ Tim Trơn", "price": 160000, "old_price": 230000, "category": "Áo thun", "image": "/Images/thunden.png", "images": ["/Images/thunden.png"], "description": "Áo thun nam cổ tim trẻ trung năng động.", "stock": 40, "sizes": ["S", "M", "L", "XL"], "colors": ["Đen"], "rating": 4.3, "reviews": 8, "sold": 95, "featured": False},
        {"name": "Áo Thun Nam Cotton Organic", "price": 190000, "old_price": 270000, "category": "Áo thun", "image": "/Images/aothun1.png", "images": ["/Images/aothun1.png"], "description": "Chất liệu cotton hữu cơ thân thiện với môi trường.", "stock": 35, "sizes": ["M", "L", "XL"], "colors": ["Xám"], "rating": 4.6, "reviews": 15, "sold": 110, "featured": False},
        {"name": "Áo Polo Nam Basic", "price": 279000, "old_price": 349000, "category": "Áo thun", "image": "/Images/aothun3.png", "images": ["/Images/aothun3.png"], "description": "Áo polo lịch sự phù hợp đi làm và đi chơi.", "stock": 35, "sizes": ["S", "M", "L", "XL"], "colors": ["Xanh Navy"], "rating": 4.5, "reviews": 18, "sold": 180, "featured": False},
        {"name": "Áo Polo Nam Sọc Ngang", "price": 289000, "old_price": 379000, "category": "Áo thun", "image": "/Images/aothun3trang.png", "images": ["/Images/aothun3trang.png"], "description": "Thiết kế kẻ sọc ngang trẻ trung, phong cách.", "stock": 30, "sizes": ["M", "L", "XL"], "colors": ["Trắng"], "rating": 4.4, "reviews": 9, "sold": 75, "featured": False},
        {"name": "Áo Polo Nam Công Sở Premium", "price": 350000, "old_price": 450000, "category": "Áo thun", "image": "/Images/aothun3.png", "images": ["/Images/aothun3.png"], "description": "Chất liệu cá sấu cao cấp, đứng form lịch sự.", "stock": 45, "sizes": ["S", "M", "L", "XL", "XXL"], "colors": ["Xanh Navy"], "rating": 4.8, "reviews": 24, "sold": 220, "featured": True},
        {"name": "Áo Sơ Mi Nam Vải Oxford Trắng", "price": 320000, "old_price": 420000, "category": "Áo sơ mi", "image": "/Images/oxford1.png", "images": ["/Images/oxford1.png"], "description": "Sơ mi Oxford dày dặn đứng dáng lịch sự.", "stock": 40, "sizes": ["S", "M", "L", "XL"], "colors": ["Trắng"], "rating": 4.7, "reviews": 14, "sold": 140, "featured": True},
        {"name": "Áo Sơ Mi Nam Vải Linen Xanh", "price": 340000, "old_price": 440000, "category": "Áo sơ mi", "image": "/Images/somixanh.png", "images": ["/Images/somixanh.png"], "description": "Sơ mi linen thoáng mát, phong cách lãng tử.", "stock": 25, "sizes": ["M", "L", "XL"], "colors": ["Xanh"], "rating": 4.5, "reviews": 11, "sold": 85, "featured": False},
        {"name": "Áo Sơ Mi Nam Kẻ Sọc Công Sở", "price": 330000, "old_price": 430000, "category": "Áo sơ mi", "image": "/Images/somi1.png", "images": ["/Images/somi1.png"], "description": "Sơ mi kẻ sọc nhã nhặn tôn dáng lịch lãm.", "stock": 30, "sizes": ["S", "M", "L", "XL"], "colors": ["Xanh"], "rating": 4.6, "reviews": 13, "sold": 105, "featured": False},
        {"name": "Áo Sơ Mi Nam Cổ Tàu Casual", "price": 299000, "old_price": 399000, "category": "Áo sơ mi", "image": "/Images/sominau.png", "images": ["/Images/sominau.png"], "description": "Sơ mi cổ tàu thoải mái năng động.", "stock": 35, "sizes": ["S", "M", "L", "XL"], "colors": ["Nâu"], "rating": 4.4, "reviews": 7, "sold": 90, "featured": False},
        {"name": "Áo Khoác Nam Denim Classic", "price": 550000, "old_price": 690000, "category": "Áo khoác", "image": "/Images/denim1.png", "images": ["/Images/denim1.png"], "description": "Áo khoác jean denim phong trần nam tính.", "stock": 20, "sizes": ["M", "L", "XL"], "colors": ["Xanh"], "rating": 4.6, "reviews": 16, "sold": 115, "featured": True},
        {"name": "Áo Khoác Gió Nam Chống Nước", "price": 450000, "old_price": 580000, "category": "Áo khoác", "image": "/Images/bomber1.png", "images": ["/Images/bomber1.png"], "description": "Áo khoác gió nhẹ cản gió và chống nước nhẹ.", "stock": 30, "sizes": ["M", "L", "XL"], "colors": ["Đen"], "rating": 4.5, "reviews": 12, "sold": 130, "featured": False},
        {"name": "Áo Khoác Nam Bomber Nhung Tăm", "price": 499000, "old_price": 650000, "category": "Áo khoác", "image": "/Images/bomber1.png", "images": ["/Images/bomber1.png"], "description": "Áo khoác bomber nhung tăm ấm áp thời thượng.", "stock": 25, "sizes": ["M", "L", "XL"], "colors": ["Đen"], "rating": 4.7, "reviews": 10, "sold": 88, "featured": False},
        {"name": "Quần Jeans Nam Slimfit Đen", "price": 549000, "old_price": 680000, "category": "Quần", "image": "/Images/jean1.png", "images": ["/Images/jean1.png"], "description": "Quần jeans nam form ôm nhẹ tôn dáng thời trang.", "stock": 35, "sizes": ["29", "30", "31", "32"], "colors": ["Đen"], "rating": 4.6, "reviews": 19, "sold": 195, "featured": True},
        {"name": "Quần Jeans Nam Ống Đứng Regular", "price": 529000, "old_price": 650000, "category": "Quần", "image": "/Images/jeanxanhdam.png", "images": ["/Images/jeanxanhdam.png"], "description": "Quần jean dáng đứng thoải mái truyền thống.", "stock": 40, "sizes": ["30", "31", "32", "33"], "colors": ["Xanh đậm"], "rating": 4.5, "reviews": 15, "sold": 150, "featured": False},
        {"name": "Quần Jeans Nam Rách Gối Streetwear", "price": 599000, "old_price": 750000, "category": "Quần", "image": "/Images/jeanxanhnhat.png", "images": ["/Images/jeanxanhnhat.png"], "description": "Quần jeans rách gối bụi bặm phong cách đường phố.", "stock": 20, "sizes": ["29", "30", "31", "32"], "colors": ["Xanh nhạt"], "rating": 4.7, "reviews": 11, "sold": 80, "featured": False},
        {"name": "Quần Kaki Nam Dáng Suông", "price": 389000, "old_price": 490000, "category": "Quần", "image": "/Images/kaki1.png", "images": ["/Images/kaki1.png"], "description": "Quần kaki thô thoáng lịch lãm dáng suông thoải mái.", "stock": 30, "sizes": ["29", "30", "31", "32"], "colors": ["Kem"], "rating": 4.4, "reviews": 14, "sold": 125, "featured": False},
        {"name": "Quần Kaki Nam Short Casual", "price": 249000, "old_price": 320000, "category": "Quần", "image": "/Images/shortden.png", "images": ["/Images/shortden.png"], "description": "Quần short kaki năng động dạo phố.", "stock": 50, "sizes": ["M", "L", "XL"], "colors": ["Đen"], "rating": 4.5, "reviews": 18, "sold": 210, "featured": False},
        {"name": "Quần Tây Nam Lịch Lãm Công Sở", "price": 489000, "old_price": 599000, "category": "Quần", "image": "/Images/quan_nu_3.png", "images": ["/Images/quan_nu_3.png"], "description": "Quần tây công sở nam vải cao cấp chống nhăn.", "stock": 35, "sizes": ["29", "30", "31", "32", "33"], "colors": ["Đen"], "rating": 4.8, "reviews": 21, "sold": 160, "featured": True},
        {"name": "Quần Jogger Nam Thể Thao Nỉ", "price": 320000, "old_price": 420000, "category": "Quần", "image": "/Images/jogger1xam.png", "images": ["/Images/jogger1xam.png"], "description": "Quần jogger nỉ co giãn tốt giữ ấm cho các buổi tập.", "stock": 40, "sizes": ["M", "L", "XL"], "colors": ["Xám"], "rating": 4.5, "reviews": 17, "sold": 175, "featured": True},
        {"name": "Quần Jogger Nam Kaki Túi Hộp", "price": 350000, "old_price": 450000, "category": "Quần", "image": "/Images/jogger1.png", "images": ["/Images/jogger1.png"], "description": "Jogger kaki túi hộp cực ngầu bụi bặm.", "stock": 30, "sizes": ["M", "L", "XL"], "colors": ["Đen"], "rating": 4.6, "reviews": 13, "sold": 130, "featured": True},
        {"name": "Áo Thun Nam Oversize Cực Chất", "price": 220000, "old_price": 290000, "category": "Áo thun", "image": "/Images/Streetwear.png", "images": ["/Images/Streetwear.png"], "description": "Áo thun form rộng thoải mái nam tính streetwear.", "stock": 45, "sizes": ["M", "L", "XL"], "colors": ["Đen"], "rating": 4.7, "reviews": 22, "sold": 250, "featured": True},
        {"name": "Áo Len Nam Cổ Tròn Cashmere", "price": 650000, "old_price": 850000, "category": "Áo len", "image": "/Images/lenxam.png", "images": ["/Images/lenxam.png"], "description": "Áo len chất liệu cashmere siêu mềm ấm áp sang trọng.", "stock": 20, "sizes": ["S", "M", "L"], "colors": ["Xám"], "rating": 4.9, "reviews": 16, "sold": 75, "featured": False},
        {"name": "Áo Len Nam Cổ Lọ Ấm Áp", "price": 520000, "old_price": 650000, "category": "Áo len", "image": "/Images/aolen2.png", "images": ["/Images/aolen2.png"], "description": "Áo len cổ lọ nam giữ nhiệt cực tốt.", "stock": 25, "sizes": ["M", "L", "XL"], "colors": ["Đen"], "rating": 4.7, "reviews": 12, "sold": 140, "featured": True},
        {"name": "Bộ Vest Nam Cao Cấp Sang Trọng", "price": 1500000, "old_price": 2000000, "category": "Blazer", "image": "/Images/blazer1den.png", "images": ["/Images/blazer1den.png"], "description": "Bộ complet vest nam cao cấp phong cách lịch lãm quý ông.", "stock": 10, "sizes": ["M", "L", "XL"], "colors": ["Đen"], "rating": 4.9, "reviews": 5, "sold": 30, "featured": True},

        # --- 25 FEMALE PRODUCTS ---
        {"name": "Áo Thun Nữ Croptop Cổ Tim", "price": 120000, "old_price": 180000, "category": "Áo thun", "image": "/Images/vay1.png", "images": ["/Images/vay1.png"], "description": "Áo croptop cổ tim thun tăm cực xinh.", "stock": 45, "sizes": ["S", "M"], "colors": ["Trắng"], "rating": 4.5, "reviews": 14, "sold": 180, "featured": False},
        {"name": "Áo Thun Nữ Form Rộng Giấu Quần", "price": 160000, "old_price": 240000, "category": "Áo thun", "image": "/Images/thuntrang.png", "images": ["/Images/thuntrang.png"], "description": "Thun nữ form rộng giấu quần cá tính năng động.", "stock": 50, "sizes": ["M", "L"], "colors": ["Trắng"], "rating": 4.4, "reviews": 18, "sold": 210, "featured": False},
        {"name": "Áo Sơ Mi Nữ Oxford Trắng", "price": 329000, "old_price": 399000, "category": "Áo sơ mi", "image": "/Images/oxford1.png", "images": ["/Images/oxford1.png"], "description": "Sơ mi Oxford nữ thanh lịch phong cách học đường.", "stock": 35, "sizes": ["S", "M", "L"], "colors": ["Trắng"], "rating": 4.7, "reviews": 25, "sold": 280, "featured": True},
        {"name": "Áo Sơ Mi Nữ Linen Kem", "price": 359000, "old_price": 449000, "category": "Áo sơ mi", "image": "/Images/linen1.png", "images": ["/Images/linen1.png"], "description": "Sơ mi chất liệu linen thoáng mát màu kem vintage.", "stock": 30, "sizes": ["S", "M", "L"], "colors": ["Be"], "rating": 4.8, "reviews": 21, "sold": 190, "featured": True},
        {"name": "Áo Sơ Mi Nữ Voan Lụa Công Sở", "price": 380000, "old_price": 480000, "category": "Áo sơ mi", "image": "/Images/somi1.png", "images": ["/Images/somi1.png"], "description": "Sơ mi voan lụa mềm mại thướt tha công sở nữ.", "stock": 25, "sizes": ["S", "M", "L", "XL"], "colors": ["Trắng"], "rating": 4.6, "reviews": 11, "sold": 95, "featured": False},
        {"name": "Áo Sơ Mi Nữ Cổ Đức Cách Điệu", "price": 310000, "old_price": 399000, "category": "Áo sơ mi", "image": "/Images/somitrang.png", "images": ["/Images/somitrang.png"], "description": "Sơ mi nữ cổ đức có thêu họa tiết cách điệu.", "stock": 35, "sizes": ["S", "M", "L"], "colors": ["Trắng"], "rating": 4.5, "reviews": 16, "sold": 120, "featured": False},
        {"name": "Blazer Nữ Công Sở Premium", "price": 820000, "old_price": 980000, "category": "Blazer", "image": "/Images/blazer4.png", "images": ["/Images/blazer4.png"], "description": "Áo khoác blazer nữ 2 lớp sang trọng công sở.", "stock": 20, "sizes": ["S", "M", "L"], "colors": ["Trắng"], "rating": 4.9, "reviews": 34, "sold": 310, "featured": True},
        {"name": "Blazer Nữ Dáng Ngắn Thời Thượng", "price": 790000, "old_price": 950000, "category": "Blazer", "image": "/Images/blazer1.png", "images": ["/Images/blazer1.png"], "description": "Blazer dáng lửng trẻ trung thời trang cá tính.", "stock": 15, "sizes": ["S", "M"], "colors": ["Be"], "rating": 4.7, "reviews": 19, "sold": 115, "featured": False},
        {"name": "Blazer Nữ Kẻ Caro Phong Cách Hàn", "price": 850000, "old_price": 1050000, "category": "Blazer", "image": "/Images/blazer3.png", "images": ["/Images/blazer3.png"], "description": "Blazer họa tiết kẻ nhỏ thanh lịch style Hàn Quốc.", "stock": 18, "sizes": ["S", "M", "L"], "colors": ["Xám"], "rating": 4.8, "reviews": 23, "sold": 150, "featured": False},
        {"name": "Quần Tây Nữ Ống Suông", "price": 459000, "old_price": 559000, "category": "Quần", "image": "/Images/quan_nu_3.png", "images": ["/Images/quan_nu_3.png"], "description": "Quần tây nữ dáng suông cạp cao tôn dáng cực đỉnh.", "stock": 25, "sizes": ["S", "M", "L"], "colors": ["Đen"], "rating": 4.9, "reviews": 45, "sold": 420, "featured": True},
        {"name": "Quần Baggy Nữ Hàn Quốc", "price": 429000, "old_price": 529000, "category": "Quần", "image": "/Images/quan_nu_2.png", "images": ["/Images/quan_nu_2.png"], "description": "Quần baggy năng động trẻ trung chất liệu tuyết mưa cao cấp.", "stock": 30, "sizes": ["S", "M", "L", "XL"], "colors": ["Đen"], "rating": 4.7, "reviews": 52, "sold": 490, "featured": True},
        {"name": "Quần Jeans Nữ Skinny Cạp Cao", "price": 489000, "old_price": 599000, "category": "Quần", "image": "/Images/quan_nu_1.png", "images": ["/Images/quan_nu_1.png"], "description": "Quần jeans skinny ôm sát co giãn thoải mái.", "stock": 30, "sizes": ["S", "M", "L"], "colors": ["Xanh"], "rating": 4.8, "reviews": 28, "sold": 220, "featured": False},
        {"name": "Quần Jeans Nữ Ống Rộng Culottes", "price": 529000, "old_price": 650000, "category": "Quần", "image": "/Images/quan_nu_4.png", "images": ["/Images/quan_nu_4.png"], "description": "Quần jeans ống rộng sành điệu chất denim dày dặn.", "stock": 25, "sizes": ["S", "M", "L"], "colors": ["Kem"], "rating": 4.6, "reviews": 19, "sold": 160, "featured": False},
        {"name": "Quần Short Nữ Jeans Retro", "price": 289000, "old_price": 380000, "category": "Quần", "image": "/Images/quan_nu_5.png", "images": ["/Images/quan_nu_5.png"], "description": "Short bò retro cạp cao xước cá tính.", "stock": 40, "sizes": ["S", "M", "L"], "colors": ["Xanh"], "rating": 4.5, "reviews": 14, "sold": 130, "featured": False},
        {"name": "Váy Tennis Nữ Xếp Ly Trắng", "price": 280000, "old_price": 350000, "category": "Váy", "image": "/Images/vay1.png", "images": ["/Images/vay1.png"], "description": "Váy ngắn xếp ly năng động có quần bảo hộ bên trong.", "stock": 35, "sizes": ["S", "M"], "colors": ["Trắng"], "rating": 4.8, "reviews": 31, "sold": 290, "featured": False},
        {"name": "Váy Nữ Hoa Nhí Dáng A", "price": 390000, "old_price": 490000, "category": "Váy", "image": "/Images/vay4.png", "images": ["/Images/vay4.png"], "description": "Váy xòe dáng chữ A họa tiết hoa nhí xinh xắn.", "stock": 25, "sizes": ["S", "M", "L"], "colors": ["Hồng"], "rating": 4.6, "reviews": 17, "sold": 140, "featured": False},
        {"name": "Váy Nữ Dự Tiệc Trễ Vai Sang Chảnh", "price": 690000, "old_price": 850000, "category": "Váy", "image": "/Images/vay5.png", "images": ["/Images/vay5.png"], "description": "Đầm dự tiệc trễ vai lộng lẫy ôm dáng quyến rũ.", "stock": 15, "sizes": ["S", "M", "L"], "colors": ["Đỏ"], "rating": 4.9, "reviews": 22, "sold": 115, "featured": True},
        {"name": "Váy Nữ Maxi Đi Biển Dịu Dàng", "price": 550000, "old_price": 690000, "category": "Váy", "image": "/Images/vaybe.png", "images": ["/Images/vaybe.png"], "description": "Đầm maxi tơ lụa thướt tha chụp ảnh siêu xinh.", "stock": 20, "sizes": ["S", "M", "L"], "colors": ["Be"], "rating": 4.8, "reviews": 15, "sold": 105, "featured": False},
        {"name": "Váy Nữ Suông Linen Thoải Mái", "price": 420000, "old_price": 520000, "category": "Váy", "image": "/Images/vayxanh.png", "images": ["/Images/vayxanh.png"], "description": "Đầm suông vải linen nhẹ nhàng thanh nhã.", "stock": 25, "sizes": ["S", "M", "L"], "colors": ["Xanh"], "rating": 4.5, "reviews": 12, "sold": 80, "featured": False},
        {"name": "Chân Váy Nữ Midi Xếp Ly", "price": 320000, "old_price": 420000, "category": "Váy", "image": "/Images/vay3.png", "images": ["/Images/vay3.png"], "description": "Chân váy xếp ly dài thanh nhã dễ phối đồ.", "stock": 30, "sizes": ["S", "M", "L"], "colors": ["Đen"], "rating": 4.7, "reviews": 19, "sold": 160, "featured": False},
        {"name": "Chân Váy Nữ Chữ A Da Lộn", "price": 299000, "old_price": 399000, "category": "Váy", "image": "/Images/vaybe.png", "images": ["/Images/vaybe.png"], "description": "Chân váy chữ A chất liệu da lộn cực sang.", "stock": 30, "sizes": ["S", "M", "L"], "colors": ["Be"], "rating": 4.6, "reviews": 10, "sold": 90, "featured": False},
        {"name": "Cardigan Nữ Len Dệt Kim Kem", "price": 499000, "old_price": 650000, "category": "Cardigan", "image": "/Images/cardigan4.png", "images": ["/Images/cardigan4.png"], "description": "Khoác len cardigan mềm mại dịu dàng vintage.", "stock": 25, "sizes": ["S", "M", "L"], "colors": ["Be"], "rating": 4.8, "reviews": 33, "sold": 270, "featured": True},
        {"name": "Cardigan Nữ Form Rộng Thêu Hoa", "price": 480000, "old_price": 590000, "category": "Cardigan", "image": "/Images/cardigan3.png", "images": ["/Images/cardigan3.png"], "description": "Cardigan len thêu hoa xinh xắn đáng yêu.", "stock": 20, "sizes": ["M", "L"], "colors": ["Nâu"], "rating": 4.7, "reviews": 14, "sold": 110, "featured": False},
        {"name": "Áo Body Nữ Basic Cổ Lọ", "price": 269000, "old_price": 340000, "category": "Áo body", "image": "/Images/body3.png", "images": ["/Images/body3.png"], "description": "Áo len tăm body cổ cao ôm sát giữ ấm và tôn dáng cực chuẩn.", "stock": 40, "sizes": ["S", "M", "L"], "colors": ["Trắng"], "rating": 4.6, "reviews": 23, "sold": 220, "featured": False},
        {"name": "Áo Body Nữ Tay Dài Ôm Sát", "price": 299000, "old_price": 380000, "category": "Áo body", "image": "/Images/body2.png", "images": ["/Images/body2.png"], "description": "Áo thun body nữ tay dài co giãn ôm dáng quyến rũ.", "stock": 30, "sizes": ["S", "M", "L"], "colors": ["Đen"], "rating": 4.8, "reviews": 27, "sold": 260, "featured": True},

        # --- 20 UNISEX PRODUCTS ---
        {"name": "Hoodie Unisex Local Brand Cực Chất", "price": 399000, "old_price": 499000, "category": "Áo khoác", "image": "/Images/hoodie1.png", "images": ["/Images/hoodie1.png"], "description": "Hoodie local brand chất nỉ bông cực dày ấm áp.", "stock": 35, "sizes": ["M", "L", "XL"], "colors": ["Nâu"], "rating": 4.9, "reviews": 46, "sold": 410, "featured": True},
        {"name": "Hoodie Unisex Nỉ Bông Có Mũ", "price": 380000, "old_price": 480000, "category": "Áo khoác", "image": "/Images/hoodiexam.png", "images": ["/Images/hoodiexam.png"], "description": "Hoodie nỉ bông trơn đơn giản cá tính.", "stock": 40, "sizes": ["M", "L", "XL"], "colors": ["Xám"], "rating": 4.7, "reviews": 18, "sold": 150, "featured": False},
        {"name": "Áo Khoác Gió Unisex Thể Thao", "price": 350000, "old_price": 450000, "category": "Áo khoác", "image": "/Images/bomber1.png", "images": ["/Images/bomber1.png"], "description": "Khoác gió nhẹ 2 lớp chống gió bụi thể thao.", "stock": 45, "sizes": ["M", "L", "XL"], "colors": ["Đen"], "rating": 4.6, "reviews": 12, "sold": 130, "featured": False},
        {"name": "Áo Khoác Bomber Unisex Da Lộn", "price": 599000, "old_price": 750000, "category": "Áo khoác", "image": "/Images/bomber1.png", "images": ["/Images/bomber1.png"], "description": "Bomber da lộn chất lừ nam nữ đều mặc đẹp.", "stock": 20, "sizes": ["M", "L", "XL"], "colors": ["Đen"], "rating": 4.8, "reviews": 15, "sold": 90, "featured": False},
        {"name": "Áo Khoác Varsity Unisex Streetwear", "price": 639000, "old_price": 799000, "category": "Áo khoác", "image": "/Images/varsity1.png", "images": ["/Images/varsity1.png"], "description": "Áo khoác varsity tay da thêu chữ ngầu chất chơi.", "stock": 25, "sizes": ["M", "L", "XL"], "colors": ["Đen Trắng"], "rating": 4.9, "reviews": 29, "sold": 185, "featured": True},
        {"name": "Áo Thun Unisex Oversize Cotton", "price": 199000, "old_price": 279000, "category": "Áo thun", "image": "/Images/aothun1.png", "images": ["/Images/aothun1.png"], "description": "Áo thun oversize 100% cotton dày mịn.", "stock": 50, "sizes": ["S", "M", "L", "XL"], "colors": ["Xám"], "rating": 4.6, "reviews": 32, "sold": 310, "featured": False},
        {"name": "Áo Thun Unisex Loang Màu Tiedye", "price": 210000, "old_price": 299000, "category": "Áo thun", "image": "/Images/Streetwear.png", "images": ["/Images/Streetwear.png"], "description": "Áo thun tie-dye loang màu phá cách thời trang.", "stock": 30, "sizes": ["M", "L", "XL"], "colors": ["Đen"], "rating": 4.5, "reviews": 14, "sold": 110, "featured": False},
        {"name": "Áo Thun Unisex In Chữ Streetwear", "price": 189000, "old_price": 250000, "category": "Áo thun", "image": "/Images/Streetwear.png", "images": ["/Images/Streetwear.png"], "description": "Áo thun tay lỡ in chữ nổi cực chất.", "stock": 40, "sizes": ["M", "L", "XL"], "colors": ["Đen"], "rating": 4.6, "reviews": 20, "sold": 160, "featured": False},
        {"name": "Áo Sweater Unisex Trơn Basic", "price": 320000, "old_price": 420000, "category": "Áo khoác", "image": "/Images/hoodienau.png", "images": ["/Images/hoodienau.png"], "description": "Sweater trơn cổ tròn đơn giản dễ mix đồ.", "stock": 35, "sizes": ["M", "L", "XL"], "colors": ["Nâu"], "rating": 4.7, "reviews": 24, "sold": 220, "featured": True},
        {"name": "Áo Sweater Unisex In Hình Cá Tính", "price": 350000, "old_price": 450000, "category": "Áo khoác", "image": "/Images/hoodiexam.png", "images": ["/Images/hoodiexam.png"], "description": "Sweater in hình thêu cá tính nổi bật đường phố.", "stock": 30, "sizes": ["M", "L", "XL"], "colors": ["Xám"], "rating": 4.8, "reviews": 19, "sold": 135, "featured": False},
        {"name": "Quần Jogger Unisex Nỉ Basic", "price": 280000, "old_price": 360000, "category": "Quần", "image": "/Images/jogger1xam.png", "images": ["/Images/jogger1xam.png"], "description": "Quần jogger nỉ basic thích hợp cho cả nam và nữ.", "stock": 45, "sizes": ["M", "L", "XL"], "colors": ["Xám"], "rating": 4.6, "reviews": 38, "sold": 340, "featured": True},
        {"name": "Quần Jogger Unisex Kaki Túi Hộp", "price": 320000, "old_price": 410000, "category": "Quần", "image": "/Images/jogger1.png", "images": ["/Images/jogger1.png"], "description": "Jogger kaki túi hộp phong cách utility trẻ trung.", "stock": 35, "sizes": ["M", "L", "XL"], "colors": ["Đen"], "rating": 4.7, "reviews": 17, "sold": 150, "featured": False},
        {"name": "Áo Khoác Denim Unisex Form Rộng", "price": 550000, "old_price": 690000, "category": "Áo khoác", "image": "/Images/denim1.png", "images": ["/Images/denim1.png"], "description": "Khoác bò denim form rộng retro chất chơi.", "stock": 25, "sizes": ["M", "L", "XL"], "colors": ["Xanh"], "rating": 4.8, "reviews": 15, "sold": 98, "featured": False},
        {"name": "Áo Thun Tay Lỡ Unisex Form Rộng", "price": 199000, "old_price": 259000, "category": "Áo thun", "image": "/Images/aothun1trang.png", "images": ["/Images/aothun1trang.png"], "description": "Áo thun tay lỡ form rộng năng động mát mẻ.", "stock": 50, "sizes": ["M", "L", "XL"], "colors": ["Trắng"], "rating": 4.5, "reviews": 23, "sold": 190, "featured": False},
        {"name": "Quần Short Unisex Nỉ Thể Thao", "price": 189000, "old_price": 250000, "category": "Quần", "image": "/Images/shortden.png", "images": ["/Images/shortden.png"], "description": "Short nỉ thun thoải mái hoạt động thể thao dạo mát.", "stock": 50, "sizes": ["M", "L", "XL"], "colors": ["Đen"], "rating": 4.6, "reviews": 21, "sold": 165, "featured": False},
        {"name": "Áo Hoodie Unisex Zip Tiện Lợi", "price": 420000, "old_price": 520000, "category": "Áo khoác", "image": "/Images/hoodie1den.png", "images": ["/Images/hoodie1den.png"], "description": "Hoodie khóa kéo zip tiện dụng trẻ trung.", "stock": 30, "sizes": ["M", "L", "XL"], "colors": ["Đen"], "rating": 4.7, "reviews": 16, "sold": 120, "featured": False},
        {"name": "Áo Sweater Unisex Cổ Tròn Nỉ", "price": 310000, "old_price": 399000, "category": "Áo khoác", "image": "/Images/hoodienau.png", "images": ["/Images/hoodienau.png"], "description": "Sweater nỉ bông cổ tròn màu sắc pastel đẹp.", "stock": 35, "sizes": ["M", "L", "XL"], "colors": ["Nâu"], "rating": 4.6, "reviews": 11, "sold": 115, "featured": False},
        {"name": "Quần Short Unisex Dù Gió", "price": 150000, "old_price": 210000, "category": "Quần", "image": "/Images/shortxanh.png", "images": ["/Images/shortxanh.png"], "description": "Short dù gió siêu nhẹ chống thấm nước nhẹ mát.", "stock": 60, "sizes": ["M", "L", "XL"], "colors": ["Xanh"], "rating": 4.4, "reviews": 9, "sold": 140, "featured": False},
        {"name": "Áo Khoác Blazer Unisex Form Rộng", "price": 750000, "old_price": 890000, "category": "Blazer", "image": "/Images/blazer3.png", "images": ["/Images/blazer3.png"], "description": "Blazer dáng rộng unisex hiện đại thanh lịch cá tính.", "stock": 20, "sizes": ["M", "L", "XL"], "colors": ["Xám"], "rating": 4.7, "reviews": 13, "sold": 70, "featured": False},
        {"name": "Áo Thun Polo Unisex Oversize", "price": 259000, "old_price": 320000, "category": "Áo thun", "image": "/Images/aothun3.png", "images": ["/Images/aothun3.png"], "description": "Polo oversize co giãn tốt thoáng khí năng động.", "stock": 40, "sizes": ["M", "L", "XL"], "colors": ["Xanh Navy"], "rating": 4.6, "reviews": 19, "sold": 145, "featured": False},

        # --- 15 SHOES ---
        {"name": "Giày Sneaker Trắng Unisex Streetwear", "price": 650000, "old_price": 790000, "category": "Giày", "image": "/Images/giay1.png", "images": ["/Images/giay1.png"], "description": "Sneaker trắng da mềm unisex dễ phối đồ đi học đi chơi.", "stock": 30, "sizes": ["38", "39", "40", "41", "42"], "colors": ["Trắng"], "rating": 4.9, "reviews": 56, "sold": 540, "featured": True},
        {"name": "Giày Sneaker Da Lộn Unisex", "price": 720000, "old_price": 890000, "category": "Giày", "image": "/Images/giay3.png", "images": ["/Images/giay3.png"], "description": "Sneaker chất da lộn thời thượng phong cách vintage.", "stock": 25, "sizes": ["38", "39", "40", "41", "42"], "colors": ["Trắng"], "rating": 4.7, "reviews": 18, "sold": 125, "featured": False},
        {"name": "Giày Chạy Bộ Nam Running Sport", "price": 790000, "old_price": 990000, "category": "Giày", "image": "/Images/giay2.png", "images": ["/Images/giay2.png"], "description": "Giày chạy thể thao nam đệm êm giảm chấn bảo vệ gối.", "stock": 25, "sizes": ["40", "41", "42", "43"], "colors": ["Đen"], "rating": 4.8, "reviews": 23, "sold": 180, "featured": True},
        {"name": "Giày Chạy Bộ Nữ Siêu Nhẹ", "price": 750000, "old_price": 950000, "category": "Giày", "image": "/Images/giay2.png", "images": ["/Images/giay2.png"], "description": "Giày chạy bộ chuyên dụng siêu nhẹ êm ái thoáng mát.", "stock": 20, "sizes": ["36", "37", "38", "39"], "colors": ["Đen"], "rating": 4.7, "reviews": 15, "sold": 110, "featured": False},
        {"name": "Giày Thể Thao Unisex Chunky", "price": 850000, "old_price": 990000, "category": "Giày", "image": "/Images/giay3.png", "images": ["/Images/giay3.png"], "description": "Chunky sneaker hack chiều cao phong cách Hàn Quốc.", "stock": 20, "sizes": ["37", "38", "39", "40", "41"], "colors": ["Trắng"], "rating": 4.8, "reviews": 34, "sold": 210, "featured": False},
        {"name": "Giày Tây Nam Oxford Da Bò", "price": 1200000, "old_price": 1600000, "category": "Giày", "image": "/Images/giay5.png", "images": ["/Images/giay5.png"], "description": "Giày tây Oxford da bò thật 100% sang trọng lịch lãm.", "stock": 15, "sizes": ["39", "40", "41", "42"], "colors": ["Xám"], "rating": 4.9, "reviews": 12, "sold": 85, "featured": False},
        {"name": "Giày Tây Nam Derby Lịch Lãm", "price": 990000, "old_price": 1300000, "category": "Giày", "image": "/Images/giay5.png", "images": ["/Images/giay5.png"], "description": "Derby hiện đại trẻ trung phong cách doanh nhân.", "stock": 20, "sizes": ["39", "40", "41", "42"], "colors": ["Xám"], "rating": 4.8, "reviews": 16, "sold": 105, "featured": True},
        {"name": "Giày Slip On Unisex Vải Canvas", "price": 399000, "old_price": 499000, "category": "Giày", "image": "/Images/giay4.png", "images": ["/Images/giay4.png"], "description": "Slip-on lười vải canvas tiện dụng dễ xỏ.", "stock": 40, "sizes": ["37", "38", "39", "40", "41", "42"], "colors": ["Đen"], "rating": 4.5, "reviews": 22, "sold": 190, "featured": False},
        {"name": "Giày Boot Da Nữ Cổ Cao Cá Tính", "price": 890000, "old_price": 1100000, "category": "Giày", "image": "/Images/giay3.png", "images": ["/Images/giay3.png"], "description": "Chelsea boots nữ chất da bóng cổ lửng sành điệu.", "stock": 15, "sizes": ["36", "37", "38", "39"], "colors": ["Trắng"], "rating": 4.8, "reviews": 14, "sold": 80, "featured": False},
        {"name": "Giày Boot Da Nam Chelsea Lịch Lãm", "price": 1100000, "old_price": 1400000, "category": "Giày", "image": "/Images/giay5.png", "images": ["/Images/giay5.png"], "description": "Chelsea boot nam da bò trơn bóng tôn dáng cao cổ lịch lãm.", "stock": 15, "sizes": ["40", "41", "42", "43"], "colors": ["Xám"], "rating": 4.9, "reviews": 11, "sold": 65, "featured": False},
        {"name": "Sandal Unisex Dây Chéo Học Sinh", "price": 250000, "old_price": 350000, "category": "Giày", "image": "/Images/giay4.png", "images": ["/Images/giay4.png"], "description": "Sandal quai chéo nhẹ nhàng mát mẻ đi học tiện lợi.", "stock": 50, "sizes": ["36", "37", "38", "39", "40", "41"], "colors": ["Đen"], "rating": 4.6, "reviews": 28, "sold": 240, "featured": False},
        {"name": "Dép Unisex Quai Ngang Êm Chân", "price": 150000, "old_price": 220000, "category": "Giày", "image": "/Images/giay4.png", "images": ["/Images/giay4.png"], "description": "Dép quai ngang đúc nguyên khối chống trơn trượt êm chân.", "stock": 60, "sizes": ["36", "37", "38", "39", "40", "41", "42"], "colors": ["Đen"], "rating": 4.5, "reviews": 31, "sold": 350, "featured": False},
        {"name": "Giày Cao Gót Nữ Đế Nhọn Công Sở", "price": 490000, "old_price": 650000, "category": "Giày", "image": "/Images/giay1.png", "images": ["/Images/giay1.png"], "description": "Giày cao gót nữ cao 7cm tôn dáng quý phái văn phòng.", "stock": 25, "sizes": ["35", "36", "37", "38", "39"], "colors": ["Trắng"], "rating": 4.8, "reviews": 19, "sold": 130, "featured": True},
        {"name": "Giày Búp Bê Nữ Da Mềm Mại", "price": 350000, "old_price": 450000, "category": "Giày", "image": "/Images/giay1.png", "images": ["/Images/giay1.png"], "description": "Giày búp bê bệt nhẹ da dê mềm cực kỳ êm chân.", "stock": 30, "sizes": ["35", "36", "37", "38", "39"], "colors": ["Trắng"], "rating": 4.6, "reviews": 10, "sold": 95, "featured": False},
        {"name": "Giày Sneaker Cổ Cao Unisex", "price": 690000, "old_price": 850000, "category": "Giày", "image": "/Images/giay3.png", "images": ["/Images/giay3.png"], "description": "Sneaker vải bố cao cổ retro trẻ trung.", "stock": 25, "sizes": ["37", "38", "39", "40", "41", "42"], "colors": ["Trắng"], "rating": 4.7, "reviews": 17, "sold": 115, "featured": False},

        # --- 15 ACCESSORIES (NÓN) ---
        {"name": "Nón Bucket Unisex Vải Kaki Trơn", "price": 150000, "old_price": 220000, "category": "Nón", "image": "/Images/non2.png", "images": ["/Images/non2.png"], "description": "Nón tai bèo bucket vải kaki 2 mặt sành điệu.", "stock": 40, "sizes": ["Free Size"], "colors": ["Đen"], "rating": 4.8, "reviews": 31, "sold": 380, "featured": True},
        {"name": "Nón Bucket Unisex Họa Tiết Loang", "price": 180000, "old_price": 250000, "category": "Nón", "image": "/Images/non2.png", "images": ["/Images/non2.png"], "description": "Bucket loang màu tiedye cực hot trend đường phố.", "stock": 30, "sizes": ["Free Size"], "colors": ["Đen"], "rating": 4.6, "reviews": 11, "sold": 85, "featured": False},
        {"name": "Nón Lưỡi Trai Unisex Thêu Chữ", "price": 120000, "old_price": 180000, "category": "Nón", "image": "/Images/non1trang.png", "images": ["/Images/non1trang.png"], "description": "Nón cap thêu chữ nổi phong cách retro.", "stock": 50, "sizes": ["Free Size"], "colors": ["Trắng"], "rating": 4.7, "reviews": 23, "sold": 220, "featured": False},
        {"name": "Nón Lưỡi Trai Unisex Basic Đen", "price": 99000, "old_price": 150000, "category": "Nón", "image": "/Images/non1.png", "images": ["/Images/non1.png"], "description": "Nón lưỡi trai trơn màu đen basic dễ phối đồ.", "stock": 60, "sizes": ["Free Size"], "colors": ["Đen"], "rating": 4.5, "reviews": 34, "sold": 410, "featured": False},
        {"name": "Nón Snapback Unisex Streetwear", "price": 220000, "old_price": 290000, "category": "Nón", "image": "/Images/non3.png", "images": ["/Images/non3.png"], "description": "Snapback hiphop cá tính thêu chữ nổi bật.", "stock": 25, "sizes": ["Free Size"], "colors": ["Xám"], "rating": 4.8, "reviews": 16, "sold": 115, "featured": True},
        {"name": "Thắt Lưng Da Nam Khóa Tự Động", "price": 350000, "old_price": 490000, "category": "Nón", "image": "/Images/non1.png", "images": ["/Images/non1.png"], "description": "Dây nịt da bò khóa lăn tự động tiện lợi công sở nam.", "stock": 35, "sizes": ["Free Size"], "colors": ["Đen"], "rating": 4.8, "reviews": 19, "sold": 150, "featured": False},
        {"name": "Thắt Lưng Da Nữ Khóa Tròn Cổ Điển", "price": 250000, "old_price": 350000, "category": "Nón", "image": "/Images/non1trang.png", "images": ["/Images/non1trang.png"], "description": "Thắt lưng da bản nhỏ khóa kim tròn cổ điển váy quần nữ.", "stock": 40, "sizes": ["Free Size"], "colors": ["Trắng"], "rating": 4.6, "reviews": 8, "sold": 75, "featured": False},
        {"name": "Túi Tote Vải Unisex Tiện Lợi", "price": 120000, "old_price": 180000, "category": "Nón", "image": "/Images/non4.png", "images": ["/Images/non4.png"], "description": "Túi vải tote canvas in hình học sinh đựng vừa laptop A4.", "stock": 60, "sizes": ["Free Size"], "colors": ["Trắng"], "rating": 4.7, "reviews": 29, "sold": 280, "featured": False},
        {"name": "Túi Bao Tử Unisex Chống Nước", "price": 220000, "old_price": 320000, "category": "Nón", "image": "/Images/non5.png", "images": ["/Images/non5.png"], "description": "Túi đeo chéo đeo ngực bao tử gọn nhẹ chống nước.", "stock": 30, "sizes": ["Free Size"], "colors": ["Navy"], "rating": 4.8, "reviews": 14, "sold": 130, "featured": False},
        {"name": "Balo Unisex Thời Trang Chống Nước", "price": 450000, "old_price": 590000, "category": "Nón", "image": "/Images/non4.png", "images": ["/Images/non4.png"], "description": "Balo đi học đi làm vải oxford chống nước siêu bền nhiều ngăn.", "stock": 25, "sizes": ["Free Size"], "colors": ["Trắng"], "rating": 4.9, "reviews": 31, "sold": 260, "featured": True},
        {"name": "Mắt Kính Unisex Chống Tia UV", "price": 290000, "old_price": 390000, "category": "Nón", "image": "/Images/non1.png", "images": ["/Images/non1.png"], "description": "Kính râm gọng kim loại chống tia UV bảo vệ mắt thời trang.", "stock": 30, "sizes": ["Free Size"], "colors": ["Đen"], "rating": 4.7, "reviews": 12, "sold": 95, "featured": False},
        {"name": "Mũ Len Unisex Mùa Đông Ấm Áp", "price": 150000, "old_price": 220000, "category": "Nón", "image": "/Images/non3.png", "images": ["/Images/non3.png"], "description": "Mũ beanie len dệt kim giữ ấm tai mùa đông.", "stock": 35, "sizes": ["Free Size"], "colors": ["Xám"], "rating": 4.8, "reviews": 18, "sold": 145, "featured": True},
        {"name": "Vớ Unisex Cotton Cổ Cao Sọc", "price": 49000, "old_price": 75000, "category": "Nón", "image": "/Images/non4.png", "images": ["/Images/non4.png"], "description": "Tất cao cổ sọc ngang phong cách thể thao êm chân.", "stock": 100, "sizes": ["Free Size"], "colors": ["Trắng"], "rating": 4.6, "reviews": 42, "sold": 480, "featured": False},
        {"name": "Ví Da Unisex Đựng Thẻ Tiện Lợi", "price": 190000, "old_price": 270000, "category": "Nón", "image": "/Images/non5.png", "images": ["/Images/non5.png"], "description": "Ví đựng thẻ cardholder da thật nhỏ gọn.", "stock": 40, "sizes": ["Free Size"], "colors": ["Navy"], "rating": 4.7, "reviews": 15, "sold": 125, "featured": False},
        {"name": "Nón Thể Thao Unisex", "price": 160000, "old_price": 230000, "category": "Nón", "image": "/Images/non4.png", "images": ["/Images/non4.png"], "description": "Nón thể thao unisex nửa đầu thoáng khí chạy bộ tennis.", "stock": 45, "sizes": ["Free Size"], "colors": ["Trắng"], "rating": 4.8, "reviews": 21, "sold": 190, "featured": True}
    ]
    products_data.extend(new_products)

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
    product_ao_thun = Product.query.filter_by(name="Áo Thun Nam Basic").first()
    product_hoodie = Product.query.filter_by(name="Áo Hoodie Unisex").first()
    product_jeans = Product.query.filter_by(name="Quần Jeans Nam").first()
    product_somi = Product.query.filter_by(name="Áo Sơ Mi Nữ Công Sở").first()
    
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
                {"product_id": product_ao_thun.id, "name": "Áo Thun Nam Basic", "price": 199000, "quantity": 2, "size": "M", "color": "Trắng", "image": "/Images/thuntrang.png"},
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
                {"product_id": product_ao_thun.id, "name": "Áo Thun Nam Basic", "price": 199000, "quantity": 1, "size": "L", "color": "Đen", "image": "/Images/thunden.png"}
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
                {"product_id": product_ao_thun.id, "name": "Áo Thun Nam Basic", "price": 199000, "quantity": 1, "size": "XL", "color": "Nâu", "image": "/Images/thunau.png"},
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
                {"product_id": product_somi.id, "name": "Áo Sơ Mi Nữ Công Sở", "price": 279000, "quantity": 2, "size": "M", "color": "Trắng", "image": "/Images/somitrang.png"}
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
                {"product_id": product_hoodie.id, "name": "Áo Hoodie Unisex", "price": 399000, "quantity": 1, "size": "L", "color": "Xám", "image": "/Images/hoodiexam.png"}
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
