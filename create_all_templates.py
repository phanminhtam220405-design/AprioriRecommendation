"""
Script tạo TẤT CẢ templates cho Flask Fashion Store
Chạy: python create_all_templates.py
Sau đó chạy: python flask_clothing_store.py
"""
import os

# Tạo thư mục
os.makedirs('templates', exist_ok=True)
os.makedirs('templates/admin', exist_ok=True)

templates = {
    'templates/base.html': '''<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Fashion Store{% endblock %}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        .dropdown:hover .dropdown-menu { display: block; }
        .product-card { transition: all 0.3s ease; }
        .product-card:hover { transform: translateY(-5px); box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1); }
    </style>
</head>
<body class="bg-gray-50">
    <nav class="bg-white shadow-lg sticky top-0 z-50">
        <div class="container mx-auto px-4">
            <div class="flex justify-between items-center h-16">
                <a href="{{ url_for('home') }}" class="text-2xl font-bold text-indigo-600">FashionStore</a>
                
                <div class="hidden md:flex flex-1 max-w-md mx-8">
                    <form action="{{ url_for('products') }}" method="get" class="w-full">
                        <div class="relative">
                            <input type="text" name="q" placeholder="Tìm kiếm sản phẩm..." 
                                   class="w-full border border-gray-300 rounded-lg px-4 py-2 pr-10 focus:outline-none focus:ring-2 focus:ring-indigo-500">
                            <button type="submit" class="absolute right-2 top-2 text-gray-400 hover:text-indigo-600">
                                <i class="fas fa-search"></i>
                            </button>
                        </div>
                    </form>
                </div>

                <div class="flex items-center space-x-6">
                    <a href="{{ url_for('products') }}" class="text-gray-700 hover:text-indigo-600">Sản phẩm</a>
                    
                    {% if session.user %}
                    <a href="{{ url_for('wishlist') }}" class="relative">
                        <i class="fas fa-heart text-gray-700 text-xl"></i>
                        {% if wishlist_count() > 0 %}
                        <span class="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-5 h-5 text-xs flex items-center justify-center">{{ wishlist_count() }}</span>
                        {% endif %}
                    </a>
                    
                    <a href="{{ url_for('cart') }}" class="relative">
                        <i class="fas fa-shopping-cart text-gray-700 text-xl"></i>
                        {% if cart_count() > 0 %}
                        <span class="absolute -top-2 -right-2 bg-indigo-600 text-white rounded-full w-5 h-5 text-xs flex items-center justify-center">{{ cart_count() }}</span>
                        {% endif %}
                    </a>

                    <div class="dropdown relative">
                        <button class="flex items-center space-x-2 text-gray-700 hover:text-indigo-600">
                            <i class="fas fa-user"></i>
                            <span>{{ session.user.name }}</span>
                            <i class="fas fa-chevron-down text-xs"></i>
                        </button>
                        <div class="dropdown-menu absolute hidden bg-white shadow-lg rounded-lg mt-2 right-0 w-48 py-2">
                            <a href="{{ url_for('profile') }}" class="block px-4 py-2 hover:bg-gray-100">Tài khoản</a>
                            <a href="{{ url_for('my_orders') }}" class="block px-4 py-2 hover:bg-gray-100">Đơn hàng</a>
                            {% if session.user.role == 'admin' %}
                            <a href="{{ url_for('admin_dashboard') }}" class="block px-4 py-2 hover:bg-gray-100 text-indigo-600">Quản trị</a>
                            {% endif %}
                            <hr class="my-2">
                            <a href="{{ url_for('logout') }}" class="block px-4 py-2 hover:bg-gray-100 text-red-600">Đăng xuất</a>
                        </div>
                    </div>
                    {% else %}
                    <a href="{{ url_for('login') }}" class="bg-indigo-600 text-white px-6 py-2 rounded-lg hover:bg-indigo-700">Đăng nhập</a>
                    {% endif %}
                </div>
            </div>
        </div>
    </nav>

    {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
            <div class="container mx-auto px-4 mt-4">
                {% for category, message in messages %}
                    <div class="p-4 rounded-lg {% if category == 'error' %}bg-red-100 text-red-800{% else %}bg-green-100 text-green-800{% endif %} mb-2">
                        {{ message }}
                    </div>
                {% endfor %}
            </div>
        {% endif %}
    {% endwith %}

    <main>
        {% block content %}{% endblock %}
    </main>

    <footer class="bg-gray-800 text-white mt-16 py-8">
        <div class="container mx-auto px-4 text-center">
            <p>&copy; 2024 Fashion Store. All rights reserved.</p>
        </div>
    </footer>

    <script>
        function addToWishlist(pid) {
            fetch('/add-to-wishlist', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({pid: pid})
            }).then(r => r.json()).then(data => {
                if (data.success) {
                    alert('Đã thêm vào yêu thích');
                    location.reload();
                } else {
                    alert(data.message || 'Có lỗi xảy ra');
                }
            });
        }
    </script>
</body>
</html>''',

    'templates/home.html': '''{% extends "base.html" %}

{% block content %}
<div class="bg-gradient-to-r from-indigo-600 to-purple-600 text-white py-20">
    <div class="container mx-auto px-4 text-center">
        <h1 class="text-5xl font-bold mb-4">Bộ Sưu Tập Mùa Đông 2024</h1>
        <p class="text-xl mb-8">Ưu đãi đặc biệt lên đến 50%</p>
        <a href="{{ url_for('products') }}" class="bg-white text-indigo-600 px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 inline-block">
            Mua sắm ngay
        </a>
    </div>
</div>

<div class="container mx-auto px-4 py-16">
    <h2 class="text-3xl font-bold mb-8">Sản phẩm nổi bật</h2>
    <div class="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-6">
        {% for product in products %}
        <div class="bg-white rounded-lg shadow-md overflow-hidden product-card">
            <div class="relative">
                {% if product.old_price > product.price %}
                <span class="absolute top-2 left-2 bg-red-500 text-white px-2 py-1 rounded text-sm z-10">
                    -{{ ((product.old_price - product.price) / product.old_price * 100)|int }}%
                </span>
                {% endif %}
                <a href="{{ url_for('product_detail', pid=product.id) }}">
                    <img src="{{ product.image }}" alt="{{ product.name }}" class="w-full h-64 object-cover">
                </a>
            </div>
            <div class="p-4">
                <h3 class="font-semibold mb-2">{{ product.name }}</h3>
                <div class="flex items-center justify-between mb-3">
                    <span class="text-xl font-bold text-indigo-600">{{ format_price(product.price) }}</span>
                    {% if product.old_price > product.price %}
                    <span class="text-sm text-gray-400 line-through">{{ format_price(product.old_price) }}</span>
                    {% endif %}
                </div>
                <a href="{{ url_for('product_detail', pid=product.id) }}" 
                   class="block w-full bg-indigo-600 text-white text-center py-2 rounded-lg hover:bg-indigo-700">
                    Xem chi tiết
                </a>
            </div>
        </div>
        {% endfor %}
    </div>
</div>
{% endblock %}''',

    'templates/products.html': '''{% extends "base.html" %}

{% block content %}
<div class="container mx-auto px-4 py-8">
    <h1 class="text-3xl font-bold mb-8">Sản phẩm</h1>
    
    <div class="flex flex-wrap gap-2 mb-8">
        <a href="{{ url_for('products') }}" 
           class="px-4 py-2 rounded-lg {% if not category %}bg-indigo-600 text-white{% else %}bg-gray-200{% endif %}">
            Tất cả
        </a>
        {% for cat in get_categories() %}
        <a href="{{ url_for('products') }}?category={{ cat }}" 
           class="px-4 py-2 rounded-lg {% if category == cat %}bg-indigo-600 text-white{% else %}bg-gray-200{% endif %}">
            {{ cat }}
        </a>
        {% endfor %}
    </div>

    {% if products %}
    <div class="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-6">
        {% for product in products %}
        <div class="bg-white rounded-lg shadow-md overflow-hidden product-card">
            <div class="relative">
                {% if product.old_price > product.price %}
                <span class="absolute top-2 left-2 bg-red-500 text-white px-2 py-1 rounded text-sm z-10">Sale</span>
                {% endif %}
                {% if session.user %}
                <button onclick="addToWishlist('{{ product.id }}')" 
                        class="absolute top-2 right-2 bg-white rounded-full w-10 h-10 flex items-center justify-center shadow z-10">
                    <i class="far fa-heart"></i>
                </button>
                {% endif %}
                <a href="{{ url_for('product_detail', pid=product.id) }}">
                    <img src="{{ product.image }}" alt="{{ product.name }}" class="w-full h-64 object-cover">
                </a>
            </div>
            <div class="p-4">
                <h3 class="font-semibold mb-2">{{ product.name }}</h3>
                <div class="flex items-center justify-between mb-3">
                    <span class="text-xl font-bold text-indigo-600">{{ format_price(product.price) }}</span>
                    {% if product.old_price > product.price %}
                    <span class="text-sm text-gray-400 line-through">{{ format_price(product.old_price) }}</span>
                    {% endif %}
                </div>
                <a href="{{ url_for('product_detail', pid=product.id) }}" 
                   class="block w-full bg-indigo-600 text-white text-center py-2 rounded-lg hover:bg-indigo-700">
                    Xem chi tiết
                </a>
            </div>
        </div>
        {% endfor %}
    </div>
    {% else %}
    <div class="text-center py-16">
        <p class="text-gray-500 text-xl">Không tìm thấy sản phẩm</p>
    </div>
    {% endif %}
</div>
{% endblock %}''',

    'templates/product_detail.html': '''{% extends "base.html" %}

{% block content %}
<div class="container mx-auto px-4 py-8">
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div>
            <img src="{{ product.image }}" alt="{{ product.name }}" class="w-full rounded-lg">
        </div>
        <div>
            <h1 class="text-3xl font-bold mb-4">{{ product.name }}</h1>
            <div class="flex items-center mb-4">
                <span class="text-3xl font-bold text-indigo-600">{{ format_price(product.price) }}</span>
                {% if product.old_price > product.price %}
                <span class="text-xl text-gray-400 line-through ml-4">{{ format_price(product.old_price) }}</span>
                {% endif %}
            </div>
            <p class="text-gray-700 mb-6">{{ product.description }}</p>
            
            <form method="post" action="{{ url_for('add_to_cart') }}" class="space-y-4">
                <input type="hidden" name="pid" value="{{ product.id }}">
                
                <div>
                    <label class="block mb-2 font-semibold">Màu sắc:</label>
                    <select name="color" class="border rounded-lg px-4 py-2">
                        {% for color in product.colors %}
                        <option>{{ color }}</option>
                        {% endfor %}
                    </select>
                </div>
                
                <div>
                    <label class="block mb-2 font-semibold">Kích thước:</label>
                    <select name="size" class="border rounded-lg px-4 py-2">
                        {% for size in product.sizes %}
                        <option>{{ size }}</option>
                        {% endfor %}
                    </select>
                </div>
                
                <div>
                    <label class="block mb-2 font-semibold">Số lượng:</label>
                    <input type="number" name="qty" value="1" min="1" max="{{ product.stock }}" 
                           class="border rounded-lg px-4 py-2 w-24">
                    <span class="ml-2 text-gray-600">Còn {{ product.stock }} sản phẩm</span>
                </div>
                
                <button type="submit" class="bg-indigo-600 text-white px-8 py-3 rounded-lg hover:bg-indigo-700 w-full">
                    <i class="fas fa-cart-plus mr-2"></i>Thêm vào giỏ hàng
                </button>
            </form>
        </div>
    </div>
</div>
{% endblock %}''',

    'templates/cart.html': '''{% extends "base.html" %}

{% block content %}
<div class="container mx-auto px-4 py-8">
    <h1 class="text-3xl font-bold mb-8">Giỏ hàng của bạn</h1>
    
    {% if cart %}
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div class="lg:col-span-2">
            {% for item in cart %}
            <div class="bg-white rounded-lg shadow p-6 mb-4 flex items-center">
                <img src="{{ item.image }}" alt="{{ item.name }}" class="w-20 h-20 object-cover rounded">
                <div class="flex-1 ml-4">
                    <h3 class="font-semibold">{{ item.name }}</h3>
                    <p class="text-sm text-gray-600">{{ item.color }} / {{ item.size }}</p>
                    <p class="font-bold text-indigo-600">{{ format_price(item.price) }}</p>
                </div>
                <div class="flex items-center space-x-2">
                    <span class="px-3">{{ item.qty }}</span>
                    <form method="post" action="{{ url_for('remove_from_cart') }}">
                        <input type="hidden" name="pid" value="{{ item.id }}">
                        <button class="text-red-500 hover:text-red-700">
                            <i class="fas fa-trash"></i>
                        </button>
                    </form>
                </div>
            </div>
            {% endfor %}
        </div>
        
        <div>
            <div class="bg-white rounded-lg shadow p-6 sticky top-24">
                <h3 class="text-xl font-bold mb-4">Tóm tắt đơn hàng</h3>
                <div class="space-y-2 mb-6">
                    <div class="flex justify-between">
                        <span>Tạm tính:</span>
                        <span>{{ format_price(subtotal) }}</span>
                    </div>
                    <div class="flex justify-between">
                        <span>Phí vận chuyển:</span>
                        <span>{{ format_price(shipping) }}</span>
                    </div>
                    <hr>
                    <div class="flex justify-between font-bold text-lg">
                        <span>Tổng:</span>
                        <span>{{ format_price(total) }}</span>
                    </div>
                </div>
                <a href="{{ url_for('checkout') }}" 
                   class="block w-full bg-indigo-600 text-white text-center py-3 rounded-lg hover:bg-indigo-700">
                    Thanh toán
                </a>
            </div>
        </div>
    </div>
    {% else %}
    <div class="text-center py-16">
        <i class="fas fa-shopping-cart text-6xl text-gray-300 mb-4"></i>
        <h2 class="text-2xl font-semibold text-gray-600 mb-4">Giỏ hàng trống</h2>
        <a href="{{ url_for('products') }}" class="bg-indigo-600 text-white px-8 py-3 rounded-lg hover:bg-indigo-700 inline-block">
            Mua sắm ngay
        </a>
    </div>
    {% endif %}
</div>
{% endblock %}''',

    'templates/checkout.html': '''{% extends "base.html" %}

{% block content %}
<div class="container mx-auto px-4 py-8">
    <h1 class="text-3xl font-bold mb-8">Thanh toán</h1>
    <form method="post" class="max-w-2xl mx-auto bg-white rounded-lg shadow p-8">
        <h3 class="text-xl font-bold mb-4">Thông tin giao hàng</h3>
        <div class="space-y-4">
            <input type="text" name="name" value="{{ user_info.name }}" placeholder="Họ tên" required 
                   class="w-full border rounded-lg px-4 py-2">
            <input type="tel" name="phone" value="{{ user_info.phone }}" placeholder="Số điện thoại" required 
                   class="w-full border rounded-lg px-4 py-2">
            <textarea name="address" placeholder="Địa chỉ" required 
                      class="w-full border rounded-lg px-4 py-2">{{ user_info.address }}</textarea>
            <button type="submit" class="w-full bg-indigo-600 text-white py-3 rounded-lg hover:bg-indigo-700">
                Hoàn tất đơn hàng
            </button>
        </div>
    </form>
</div>
{% endblock %}''',

    'templates/order_detail.html': '''{% extends "base.html" %}

{% block content %}
<div class="container mx-auto px-4 py-8">
    <div class="max-w-4xl mx-auto bg-white rounded-lg shadow p-8">
        <h1 class="text-2xl font-bold mb-4">Đơn hàng #{{ order.id[:8] }}</h1>
        <p class="text-gray-600 mb-6">Ngày đặt: {{ order.created_at }}</p>
        
        <div class="mb-6">
            <h3 class="font-bold mb-2">Thông tin giao hàng:</h3>
            <p>{{ order.shipping_info.name }}</p>
            <p>{{ order.shipping_info.phone }}</p>
            <p>{{ order.shipping_info.address }}</p>
        </div>
        
        <div class="mb-6">
            <h3 class="font-bold mb-2">Sản phẩm:</h3>
            {% for item in order.items %}
            <div class="flex items-center border-b py-4">
                <img src="{{ item.image }}" class="w-16 h-16 object-cover rounded">
                <div class="flex-1 ml-4">
                    <p class="font-semibold">{{ item.name }}</p>
                    <p class="text-sm text-gray-600">{{ item.color }} / {{ item.size }} x {{ item.qty }}</p>
                </div>
                <p class="font-bold">{{ format_price(item.price * item.qty) }}</p>
            </div>
            {% endfor %}
        </div>
        
        <div class="text-right">
            <p>Tạm tính: {{ format_price(order.subtotal) }}</p>
            <p>Phí vận chuyển: {{ format_price(order.shipping) }}</p>
            <p class="text-xl font-bold mt-2">Tổng: {{ format_price(order.total) }}</p>
        </div>
        
        <div class="mt-6">
            <a href="{{ url_for('my_orders') }}" class="bg-gray-600 text-white px-6 py-2 rounded-lg hover:bg-gray-700">
                ← Quay lại đơn hàng
            </a>
        </div>
    </div>
</div>
{% endblock %}''',

    'templates/my_orders.html': '''{% extends "base.html" %}

{% block content %}
<div class="container mx-auto px-4 py-8">
    <h1 class="text-3xl font-bold mb-8">Đơn hàng của tôi</h1>
    
    {% if orders %}
    <div class="space-y-4">
        {% for order in orders %}
        <div class="bg-white rounded-lg shadow p-6">
            <div class="flex justify-between items-center mb-4">
                <div>
                    <h3 class="font-bold">Đơn hàng #{{ order.id[:8] }}</h3>
                    <p class="text-sm text-gray-600">{{ order.created_at }}</p>
                </div>
                <div>
                    <span class="px-3 py-1 rounded-full text-sm bg-yellow-100 text-yellow-800">{{ order.status }}</span>
                    <span class="font-bold text-lg ml-4">{{ format_price(order.total) }}</span>
                </div>
            </div>
            <a href="{{ url_for('order_detail', order_id=order.id) }}" 
               class="text-indigo-600 hover:text-indigo-700">Xem chi tiết →</a>
        </div>
        {% endfor %}
    </div>
    {% else %}
    <div class="text-center py-16">
        <p class="text-gray-500 mb-4">Chưa có đơn hàng nào</p>
        <a href="{{ url_for('products') }}" class="bg-indigo-600 text-white px-8 py-3 rounded-lg hover:bg-indigo-700 inline-block">
            Mua sắm ngay
        </a>
    </div>
    {% endif %}
</div>
{% endblock %}''',

    'templates/wishlist.html': '''{% extends "base.html" %}

{% block content %}
<div class="container mx-auto px-4 py-8">
    <h1 class="text-3xl font-bold mb-8">Sản phẩm yêu thích</h1>
    
    {% if wishlist_products %}
    <div class="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-6">
        {% for product in wishlist_products %}
        <div class="bg-white rounded-lg shadow-md overflow-hidden product-card">
            <div class="relative">
                <button onclick="removeFromWishlist('{{ product.id }}')" 
                        class="absolute top-2 right-2 bg-white rounded-full w-10 h-10 flex items-center justify-center shadow z-10">
                    <i class="fas fa-heart text-red-500"></i>
                </button>
                <a href="{{ url_for('product_detail', pid=product.id) }}">
                    <img src="{{ product.image }}" alt="{{ product.name }}" class="w-full h-64 object-cover">
                </a>
            </div>
            <div class="p-4">
                <h3 class="font-semibold mb-2">{{ product.name }}</h3>
                <p class="text-xl font-bold text-indigo-600 mb-3">{{ format_price(product.price) }}</p>
                <a href="{{ url_for('product_detail', pid=product.id) }}" 
                   class="block w-full bg-indigo-600 text-white text-center py-2 rounded-lg hover:bg-indigo-700">
                    Xem chi tiết
                </a>
            </div>
        </div>
        {% endfor %}
    </div>
    {% else %}
    <div class="text-center py-16">
        <i class="fas fa-heart text-6xl text-gray-300 mb-4"></i>
        <p class="text-gray-500 mb-4">Chưa có sản phẩm yêu thích</p>
        <a href="{{ url_for('products') }}" class="bg-indigo-600 text-white px-8 py-3 rounded-lg hover:bg-indigo-700 inline-block">
            Mua sắm ngay
        </a>
    </div>
    {% endif %}
</div>
<script>
function removeFromWishlist(pid) {
    fetch('/remove-from-wishlist', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({pid: pid})
    }).then(r => r.json()).then(data => {
        if (data.success) {
            location.reload();
        }
    });
}
</script>
{% endblock %}''',

    'templates/profile.html': '''{% extends "base.html" %}

{% block content %}
<div class="container mx-auto px-4 py-8">
    <h1 class="text-3xl font-bold mb-8">Thông tin tài khoản</h1>
    
    <div class="max-w-2xl mx-auto bg-white rounded-lg shadow p-8">
        <form method="post" class="space-y-4">
            <div>
                <label class="block mb-2 font-semibold">Họ và tên:</label>
                <input type="text" name="name" value="{{ user.name }}" required
                       class="w-full border rounded-lg px-4 py-2">
            </div>
            <div>
                <label class="block mb-2 font-semibold">Email:</label>
                <input type="email" value="{{ session.user.email }}" disabled
                       class="w-full border rounded-lg px-4 py-2 bg-gray-100">
            </div>
            <div>
                <label class="block mb-2 font-semibold">Số điện thoại:</label>
                <input type="tel" name="phone" value="{{ user.phone }}"
                       class="w-full border rounded-lg px-4 py-2">
            </div>
            <div>
                <label class="block mb-2 font-semibold">Địa chỉ:</label>
                <textarea name="address" class="w-full border rounded-lg px-4 py-2">{{ user.address }}</textarea>
            </div>
            <button type="submit" class="bg-indigo-600 text-white px-8 py-3 rounded-lg hover:bg-indigo-700">
                Cập nhật
            </button>
        </form>
    </div>
</div>
{% endblock %}''',

    'templates/login.html': '''{% extends "base.html" %}

{% block content %}
<div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4">
    <div class="max-w-md w-full">
        <h2 class="text-3xl font-bold text-center mb-8">Đăng nhập</h2>
        <div class="bg-white rounded-lg shadow p-8">
            <form method="post" class="space-y-4">
                <div>
                    <label class="block mb-2">Email:</label>
                    <input type="email" name="email" required
                           class="w-full border rounded-lg px-4 py-2">
                </div>
                <div>
                    <label class="block mb-2">Mật khẩu:</label>
                    <input type="password" name="password" required
                           class="w-full border rounded-lg px-4 py-2">
                </div>
                <button type="submit" class="w-full bg-indigo-600 text-white py-3 rounded-lg hover:bg-indigo-700">
                    Đăng nhập
                </button>
            </form>
            <div class="mt-6 text-center">
                <p class="text-sm text-gray-600 mb-2">Chưa có tài khoản?</p>
                <a href="{{ url_for('register') }}" class="text-indigo-600 hover:text-indigo-700">Đăng ký ngay</a>
            </div>
            <div class="mt-4 p-4 bg-gray-100 rounded">
                <p class="text-sm text-gray-600 text-center">
                    <strong>Tài khoản demo:</strong><br>
                    Admin: admin@example.com / admin123
                </p>
            </div>
        </div>
    </div>
</div>
{% endblock %}''',

    'templates/register.html': '''{% extends "base.html" %}

{% block content %}
<div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4">
    <div class="max-w-md w-full">
        <h2 class="text-3xl font-bold text-center mb-8">Đăng ký</h2>
        <div class="bg-white rounded-lg shadow p-8">
            <form method="post" class="space-y-4">
                <div>
                    <label class="block mb-2">Họ và tên:</label>
                    <input type="text" name="name" required
                           class="w-full border rounded-lg px-4 py-2">
                </div>
                <div>
                    <label class="block mb-2">Email:</label>
                    <input type="email" name="email" required
                           class="w-full border rounded-lg px-4 py-2">
                </div>
                <div>
                    <label class="block mb-2">Số điện thoại:</label>
                    <input type="tel" name="phone"
                           class="w-full border rounded-lg px-4 py-2">
                </div>
                <div>
                    <label class="block mb-2">Mật khẩu:</label>
                    <input type="password" name="password" required
                           class="w-full border rounded-lg px-4 py-2">
                </div>
                <div>
                    <label class="block mb-2">Xác nhận mật khẩu:</label>
                    <input type="password" name="confirm_password" required
                           class="w-full border rounded-lg px-4 py-2">
                </div>
                <button type="submit" class="w-full bg-indigo-600 text-white py-3 rounded-lg hover:bg-indigo-700">
                    Đăng ký
                </button>
            </form>
            <div class="mt-6 text-center">
                <p class="text-sm text-gray-600">Đã có tài khoản?</p>
                <a href="{{ url_for('login') }}" class="text-indigo-600 hover:text-indigo-700">Đăng nhập</a>
            </div>
        </div>
    </div>
</div>
{% endblock %}''',

    'templates/admin/dashboard.html': '''{% extends "base.html" %}

{% block title %}Quản trị - Fashion Store{% endblock %}

{% block content %}
<div class="container mx-auto px-4 py-8">
    <h1 class="text-3xl font-bold mb-8">Dashboard Quản trị</h1>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div class="bg-white rounded-2xl shadow-sm p-6">
            <div class="flex items-center">
                <div class="w-12 h-12 bg-indigo-100 rounded-lg flex items-center justify-center mr-4">
                    <i class="fas fa-shopping-cart text-indigo-600 text-xl"></i>
                </div>
                <div>
                    <p class="text-sm text-gray-600">Tổng đơn hàng</p>
                    <p class="text-2xl font-bold">{{ total_orders }}</p>
                </div>
            </div>
        </div>

        <div class="bg-white rounded-2xl shadow-sm p-6">
            <div class="flex items-center">
                <div class="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mr-4">
                    <i class="fas fa-box text-green-600 text-xl"></i>
                </div>
                <div>
                    <p class="text-sm text-gray-600">Sản phẩm</p>
                    <p class="text-2xl font-bold">{{ total_products }}</p>
                </div>
            </div>
        </div>

        <div class="bg-white rounded-2xl shadow-sm p-6">
            <div class="flex items-center">
                <div class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mr-4">
                    <i class="fas fa-users text-blue-600 text-xl"></i>
                </div>
                <div>
                    <p class="text-sm text-gray-600">Khách hàng</p>
                    <p class="text-2xl font-bold">{{ total_users }}</p>
                </div>
            </div>
        </div>

        <div class="bg-white rounded-2xl shadow-sm p-6">
            <div class="flex items-center">
                <div class="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center mr-4">
                    <i class="fas fa-money-bill text-yellow-600 text-xl"></i>
                </div>
                <div>
                    <p class="text-sm text-gray-600">Doanh thu</p>
                    <p class="text-2xl font-bold">{{ format_price(revenue) }}</p>
                </div>
            </div>
        </div>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <a href="{{ url_for('admin_products') }}" class="bg-indigo-600 text-white rounded-lg shadow p-6 hover:bg-indigo-700">
            <i class="fas fa-box text-3xl mb-2"></i>
            <h3 class="text-xl font-bold">Quản lý sản phẩm</h3>
        </a>
        <a href="{{ url_for('admin_orders') }}" class="bg-green-600 text-white rounded-lg shadow p-6 hover:bg-green-700">
            <i class="fas fa-shopping-cart text-3xl mb-2"></i>
            <h3 class="text-xl font-bold">Quản lý đơn hàng</h3>
        </a>
        <a href="{{ url_for('admin_users') }}" class="bg-purple-600 text-white rounded-lg shadow p-6 hover:bg-purple-700">
            <i class="fas fa-users text-3xl mb-2"></i>
            <h3 class="text-xl font-bold">Quản lý khách hàng</h3>
        </a>
    </div>

    <div class="bg-white rounded-2xl shadow-sm p-6">
        <div class="flex justify-between items-center mb-6">
            <h3 class="text-xl font-bold">Đơn hàng gần đây</h3>
            <a href="{{ url_for('admin_orders') }}" class="text-indigo-600 hover:text-indigo-700 font-semibold">
                Xem tất cả →
            </a>
        </div>

        <div class="overflow-x-auto">
            <table class="w-full">
                <thead>
                    <tr class="border-b border-gray-200">
                        <th class="text-left py-3 px-4">Mã đơn</th>
                        <th class="text-left py-3 px-4">Khách hàng</th>
                        <th class="text-left py-3 px-4">Ngày đặt</th>
                        <th class="text-left py-3 px-4">Tổng tiền</th>
                        <th class="text-left py-3 px-4">Trạng thái</th>
                    </tr>
                </thead>
                <tbody>
                    {% for order in recent_orders %}
                    <tr class="border-b border-gray-200 hover:bg-gray-50">
                        <td class="py-3 px-4">#{{ order.id[:8] }}</td>
                        <td class="py-3 px-4">{{ order.user_email }}</td>
                        <td class="py-3 px-4">{{ order.created_at }}</td>
                        <td class="py-3 px-4">{{ format_price(order.total) }}</td>
                        <td class="py-3 px-4">
                            <span class="px-2 py-1 rounded-full text-xs font-medium 
                                {% if order.status == 'completed' %}bg-green-100 text-green-800
                                {% elif order.status == 'pending' %}bg-yellow-100 text-yellow-800
                                {% elif order.status == 'shipping' %}bg-blue-100 text-blue-800
                                {% else %}bg-gray-100 text-gray-800{% endif %}">
                                {{ order.status|title }}
                            </span>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</div>
{% endblock %}''',

    'templates/admin/orders.html': '''{% extends "base.html" %}

{% block title %}Quản lý đơn hàng - Fashion Store{% endblock %}

{% block content %}
<div class="container mx-auto px-4 py-8">
    <h1 class="text-3xl font-bold mb-8">Quản lý đơn hàng</h1>

    <div class="bg-white rounded-2xl shadow-sm">
        <div class="overflow-x-auto">
            <table class="w-full">
                <thead>
                    <tr class="border-b border-gray-200">
                        <th class="text-left py-4 px-6">Mã đơn</th>
                        <th class="text-left py-4 px-6">Khách hàng</th>
                        <th class="text-left py-4 px-6">Ngày đặt</th>
                        <th class="text-left py-4 px-6">Tổng tiền</th>
                        <th class="text-left py-4 px-6">Trạng thái</th>
                        <th class="text-left py-4 px-6">Thao tác</th>
                    </tr>
                </thead>
                <tbody>
                    {% for order in orders %}
                    <tr class="border-b border-gray-200 hover:bg-gray-50">
                        <td class="py-4 px-6">#{{ order.id[:8] }}</td>
                        <td class="py-4 px-6">{{ order.user_email }}</td>
                        <td class="py-4 px-6">{{ order.created_at }}</td>
                        <td class="py-4 px-6">{{ format_price(order.total) }}</td>
                        <td class="py-4 px-6">
                            <span class="px-2 py-1 rounded-full text-xs font-medium 
                                {% if order.status == 'completed' %}bg-green-100 text-green-800
                                {% elif order.status == 'pending' %}bg-yellow-100 text-yellow-800
                                {% elif order.status == 'shipping' %}bg-blue-100 text-blue-800
                                {% else %}bg-gray-100 text-gray-800{% endif %}">
                                {{ order.status|title }}
                            </span>
                        </td>
                        <td class="py-4 px-6">
                            <form method="post" action="{{ url_for('update_order_status') }}" class="flex space-x-2">
                                <input type="hidden" name="order_id" value="{{ order.id }}">
                                <select name="status" class="border border-gray-300 rounded px-2 py-1 text-sm">
                                    <option value="pending" {% if order.status == 'pending' %}selected{% endif %}>Chờ xử lý</option>
                                    <option value="shipping" {% if order.status == 'shipping' %}selected{% endif %}>Đang giao</option>
                                    <option value="completed" {% if order.status == 'completed' %}selected{% endif %}>Hoàn thành</option>
                                    <option value="cancelled" {% if order.status == 'cancelled' %}selected{% endif %}>Đã hủy</option>
                                </select>
                                <button type="submit" class="bg-indigo-600 text-white px-3 py-1 rounded text-sm hover:bg-indigo-700">
                                    Cập nhật
                                </button>
                            </form>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</div>
{% endblock %}''',

    'templates/admin/products.html': '''{% extends "base.html" %}

{% block title %}Quản lý sản phẩm - Fashion Store{% endblock %}

{% block content %}
<div class="container mx-auto px-4 py-8">
    <div class="flex justify-between items-center mb-8">
        <h1 class="text-3xl font-bold">Quản lý sản phẩm</h1>
        <a href="{{ url_for('admin_add_product') }}" class="bg-indigo-600 text-white px-6 py-2 rounded-lg hover:bg-indigo-700">
            <i class="fas fa-plus mr-2"></i>Thêm sản phẩm
        </a>
    </div>

    <div class="bg-white rounded-2xl shadow-sm">
        <div class="overflow-x-auto">
            <table class="w-full">
                <thead>
                    <tr class="border-b border-gray-200">
                        <th class="text-left py-4 px-6">Sản phẩm</th>
                        <th class="text-left py-4 px-6">Danh mục</th>
                        <th class="text-left py-4 px-6">Giá</th>
                        <th class="text-left py-4 px-6">Tồn kho</th>
                        <th class="text-left py-4 px-6">Đã bán</th>
                        <th class="text-left py-4 px-6">Thao tác</th>
                    </tr>
                </thead>
                <tbody>
                    {% for product in products %}
                    <tr class="border-b border-gray-200 hover:bg-gray-50">
                        <td class="py-4 px-6">
                            <div class="flex items-center">
                                <img src="{{ product.image }}" alt="{{ product.name }}" class="w-12 h-12 object-cover rounded-lg mr-3">
                                <div>
                                    <div class="font-semibold">{{ product.name }}</div>
                                    <div class="text-sm text-gray-600">{{ product.id[:8] }}</div>
                                </div>
                            </div>
                        </td>
                        <td class="py-4 px-6">{{ product.category }}</td>
                        <td class="py-4 px-6">{{ format_price(product.price) }}</td>
                        <td class="py-4 px-6">{{ product.stock }}</td>
                        <td class="py-4 px-6">{{ product.sold }}</td>
                        <td class="py-4 px-6">
                            <a href="{{ url_for('admin_edit_product', pid=product.id) }}" 
                               class="text-blue-600 hover:text-blue-800 mr-3">
                                <i class="fas fa-edit"></i>
                            </a>
                            <a href="{{ url_for('admin_delete_product', pid=product.id) }}" 
                               onclick="return confirm('Xác nhận xóa sản phẩm này?')"
                               class="text-red-600 hover:text-red-800">
                                <i class="fas fa-trash"></i>
                            </a>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</div>
{% endblock %}''',

    'templates/admin/add_product.html': '''{% extends "base.html" %}

{% block content %}
<div class="container mx-auto px-4 py-8">
    <h1 class="text-3xl font-bold mb-8">Thêm sản phẩm mới</h1>
    
    <form method="post" class="max-w-2xl bg-white rounded-lg shadow p-8">
        <div class="space-y-4">
            <div>
                <label class="block mb-2 font-semibold">Tên sản phẩm:</label>
                <input type="text" name="name" required class="w-full border rounded-lg px-4 py-2">
            </div>
            <div class="grid grid-cols-2 gap-4">
                <div>
                    <label class="block mb-2 font-semibold">Giá bán:</label>
                    <input type="number" name="price" required class="w-full border rounded-lg px-4 py-2">
                </div>
                <div>
                    <label class="block mb-2 font-semibold">Giá gốc:</label>
                    <input type="number" name="old_price" class="w-full border rounded-lg px-4 py-2">
                </div>
            </div>
            <div>
                <label class="block mb-2 font-semibold">Danh mục:</label>
                <input type="text" name="category" required class="w-full border rounded-lg px-4 py-2">
            </div>
            <div>
                <label class="block mb-2 font-semibold">URL hình ảnh:</label>
                <input type="text" name="image" class="w-full border rounded-lg px-4 py-2">
            </div>
            <div>
                <label class="block mb-2 font-semibold">Mô tả:</label>
                <textarea name="description" rows="3" class="w-full border rounded-lg px-4 py-2"></textarea>
            </div>
            <div>
                <label class="block mb-2 font-semibold">Kho:</label>
                <input type="number" name="stock" required class="w-full border rounded-lg px-4 py-2">
            </div>
            <div>
                <label class="block mb-2 font-semibold">Sizes (phân cách bởi dấu phẩy):</label>
                <input type="text" name="sizes" placeholder="S,M,L,XL" class="w-full border rounded-lg px-4 py-2">
            </div>
            <div>
                <label class="block mb-2 font-semibold">Màu sắc (phân cách bởi dấu phẩy):</label>
                <input type="text" name="colors" placeholder="Trắng,Đen,Xám" class="w-full border rounded-lg px-4 py-2">
            </div>
            <div>
                <label class="flex items-center">
                    <input type="checkbox" name="featured" class="mr-2">
                    <span>Sản phẩm nổi bật</span>
                </label>
            </div>
            <div class="flex space-x-4">
                <button type="submit" class="bg-indigo-600 text-white px-8 py-3 rounded-lg hover:bg-indigo-700">
                    Thêm sản phẩm
                </button>
                <a href="{{ url_for('admin_products') }}" class="bg-gray-600 text-white px-8 py-3 rounded-lg hover:bg-gray-700">
                    Hủy
                </a>
            </div>
        </div>
    </form>
</div>
{% endblock %}''',

    'templates/admin/edit_product.html': '''{% extends "base.html" %}

{% block content %}
<div class="container mx-auto px-4 py-8">
    <h1 class="text-3xl font-bold mb-8">Chỉnh sửa sản phẩm</h1>
    
    <form method="post" class="max-w-2xl bg-white rounded-lg shadow p-8">
        <div class="space-y-4">
            <div>
                <label class="block mb-2 font-semibold">Tên sản phẩm:</label>
                <input type="text" name="name" value="{{ product.name }}" required class="w-full border rounded-lg px-4 py-2">
            </div>
            <div class="grid grid-cols-2 gap-4">
                <div>
                    <label class="block mb-2 font-semibold">Giá bán:</label>
                    <input type="number" name="price" value="{{ product.price }}" required class="w-full border rounded-lg px-4 py-2">
                </div>
                <div>
                    <label class="block mb-2 font-semibold">Giá gốc:</label>
                    <input type="number" name="old_price" value="{{ product.old_price }}" class="w-full border rounded-lg px-4 py-2">
                </div>
            </div>
            <div>
                <label class="block mb-2 font-semibold">Danh mục:</label>
                <input type="text" name="category" value="{{ product.category }}" required class="w-full border rounded-lg px-4 py-2">
            </div>
            <div>
                <label class="block mb-2 font-semibold">URL hình ảnh:</label>
                <input type="text" name="image" value="{{ product.image }}" class="w-full border rounded-lg px-4 py-2">
            </div>
            <div>
                <label class="block mb-2 font-semibold">Mô tả:</label>
                <textarea name="description" rows="3" class="w-full border rounded-lg px-4 py-2">{{ product.description }}</textarea>
            </div>
            <div>
                <label class="block mb-2 font-semibold">Kho:</label>
                <input type="number" name="stock" value="{{ product.stock }}" required class="w-full border rounded-lg px-4 py-2">
            </div>
            <div>
                <label class="block mb-2 font-semibold">Sizes (phân cách bởi dấu phẩy):</label>
                <input type="text" name="sizes" value="{{ product.sizes|join(',') }}" class="w-full border rounded-lg px-4 py-2">
            </div>
            <div>
                <label class="block mb-2 font-semibold">Màu sắc (phân cách bởi dấu phẩy):</label>
                <input type="text" name="colors" value="{{ product.colors|join(',') }}" class="w-full border rounded-lg px-4 py-2">
            </div>
            <div>
                <label class="flex items-center">
                    <input type="checkbox" name="featured" {% if product.featured %}checked{% endif %} class="mr-2">
                    <span>Sản phẩm nổi bật</span>
                </label>
            </div>
            <div class="flex space-x-4">
                <button type="submit" class="bg-indigo-600 text-white px-8 py-3 rounded-lg hover:bg-indigo-700">
                    Cập nhật
                </button>
                <a href="{{ url_for('admin_products') }}" class="bg-gray-600 text-white px-8 py-3 rounded-lg hover:bg-gray-700">
                    Hủy
                </a>
            </div>
        </div>
    </form>
</div>
{% endblock %}''',

    'templates/admin/users.html': '''{% extends "base.html" %}

{% block content %}
<div class="container mx-auto px-4 py-8">
    <h1 class="text-3xl font-bold mb-8">Quản lý khách hàng</h1>
    
    <div class="bg-white rounded-lg shadow overflow-hidden">
        <table class="w-full">
            <thead class="bg-gray-50">
                <tr>
                    <th class="text-left p-4">Email</th>
                    <th class="text-left p-4">Tên</th>
                    <th class="text-left p-4">SĐT</th>
                    <th class="text-left p-4">Vai trò</th>
                    <th class="text-left p-4">Đơn hàng</th>
                    <th class="text-left p-4">Thao tác</th>
                </tr>
            </thead>
            <tbody>
                {% for email, user in users.items() %}
                <tr class="border-b">
                    <td class="p-4">{{ email }}</td>
                    <td class="p-4">{{ user.name }}</td>
                    <td class="p-4">{{ user.phone }}</td>
                    <td class="p-4">
                        <span class="px-2 py-1 rounded text-sm {% if user.role == 'admin' %}bg-purple-100 text-purple-800{% else %}bg-gray-100 text-gray-800{% endif %}">
                            {{ user.role }}
                        </span>
                    </td>
                    <td class="p-4">{{ user.orders|length }}</td>
                    <td class="p-4">
                        {% if email != session.user.email %}
                        <a href="{{ url_for('admin_delete_user', email=email) }}" 
                           onclick="return confirm('Xác nhận xóa khách hàng này?')"
                           class="text-red-600 hover:text-red-800">
                            <i class="fas fa-trash"></i>
                        </a>
                        {% endif %}
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
{% endblock %}'''
}

# Tạo tất cả các file
for filepath, content in templates.items():
    print(f"Đang tạo {filepath}...")
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

print("\n" + "="*60)
print("✅ HOÀN TẤT! Đã tạo tất cả templates")
print("="*60)
print("\n📝 Các file đã tạo:")
for filepath in templates.keys():
    print(f"  ✓ {filepath}")
print("\n🚀 Bây giờ chạy lệnh:")
print("  python flask_clothing_store_complete.py")
print("="*60)