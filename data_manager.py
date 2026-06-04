import json
import os
from datetime import datetime

DATA_FILE = 'store_data.json'

def load_data():
    """Load dữ liệu từ file JSON"""
    default_data = {
        "products": [
            {
                "id": "1",
                "name": "Áo thun Basic Unisex",
                "price": 199000,
                "old_price": 299000,
                "category": "Áo thun",
                "image": "https://picsum.photos/seed/tee1/600/600",
                "images": ["https://picsum.photos/seed/tee1/600/600", "https://picsum.photos/seed/tee1a/600/600"],
                "description": "Áo thun cotton mềm, phù hợp mọi lứa tuổi. Chất liệu thấm hút mồ hôi tốt.",
                "stock": 50,
                "sizes": ["S", "M", "L", "XL"],
                "colors": ["Trắng", "Đen", "Xám"],
                "rating": 4.5,
                "reviews": 128,
                "sold": 340,
                "featured": True
            }
        ],
        "users": {
            "admin@example.com": {
                "password": "admin123", 
                "role": "admin", 
                "name": "Admin",
                "phone": "0901234567",
                "address": "123 Nguyễn Huệ, Q1, TP.HCM",
                "wishlist": [],
                "orders": [],
                "created_at": datetime.now().isoformat()
            }
        },
        "orders": [],
        "reviews": [],
        "vouchers": [
            {"code": "GIAM50K", "discount": 50000, "min_order": 500000, "type": "fixed", "active": True},
            {"code": "SALE20", "discount": 20, "min_order": 300000, "type": "percent", "active": True}
        ]
    }
    
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return default_data
    return default_data

def save_data(data):
    """Lưu dữ liệu vào file JSON"""
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except:
        return False

def get_all_data():
    """Lấy toàn bộ dữ liệu"""
    return load_data()

def update_data(new_data):
    """Cập nhật dữ liệu"""
    return save_data(new_data)