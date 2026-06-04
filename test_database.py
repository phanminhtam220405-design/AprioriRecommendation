"""
Test script to verify SQLite database setup
"""
from flask_clothing_store import app
from database import db, Product, User, Order, Voucher
import os

def test_database():
    """Test database initialization and data"""
    with app.app_context():
        print("=" * 50)
        print("Database Test Results")
        print("=" * 50)
        
        # Check if database file exists
        db_path = 'instance/clothing_store.db'
        if os.path.exists(db_path):
            print(f"✅ Database file created: {db_path}")
        else:
            print(f"❌ Database file not found: {db_path}")
            return
        
        # Test Products
        products_count = Product.query.count()
        print(f"✅ Products in database: {products_count}")
        if products_count > 0:
            sample_product = Product.query.first()
            print(f"   Sample: {sample_product.name} - {sample_product.price:,}đ")
        
        # Test Users
        users_count = User.query.count()
        print(f"✅ Users in database: {users_count}")
        if users_count > 0:
            admin = User.query.filter_by(role='admin').first()
            if admin:
                print(f"   Admin user: {admin.email}")
        
        # Test Vouchers
        vouchers_count = Voucher.query.count()
        print(f"✅ Vouchers in database: {vouchers_count}")
        if vouchers_count > 0:
            sample_voucher = Voucher.query.first()
            print(f"   Sample: {sample_voucher.code} - {sample_voucher.discount}")
        
        # Test Orders
        orders_count = Order.query.count()
        print(f"✅ Orders in database: {orders_count}")
        
        print("=" * 50)
        print("✅ All database tests passed!")
        print("=" * 50)
        print("\nYou can now run the application:")
        print("  python flask_clothing_store.py")
        print("\nLogin credentials:")
        print("  Email: admin@example.com")
        print("  Password: admin123")
        print("=" * 50)

if __name__ == '__main__':
    test_database()
