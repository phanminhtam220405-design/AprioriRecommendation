import os
import json
import csv
import random
from datetime import datetime, timedelta
from flask_clothing_store import app
from database import db, Product, User, Order

def generate_data():
    with app.app_context():
        # Clean terminal output (avoiding non-ASCII)
        print("Starting data generation...")
        
        # 1. Clear existing orders and mock users (keep admin and staff)
        print("Clearing old orders and mock users...")
        db.session.query(Order).delete()
        db.session.query(User).filter(User.role == 'user').delete()
        db.session.commit()
        
        # 2. Get all products from database and group them by category
        products = Product.query.all()
        products_by_cat = {}
        for p in products:
            if p.category not in products_by_cat:
                products_by_cat[p.category] = []
            products_by_cat[p.category].append(p)
            
        print(f"Loaded {len(products)} products across {len(products_by_cat)} categories.")
            
        # 3. Create 100 mock users
        print("Creating 100 mock users...")
        mock_users = []
        first_names = ["Anh", "Binh", "Cuong", "Dung", "Giang", "Huong", "Hai", "Khanh", "Lan", "Minh", "Nam", "Oanh", "Phong", "Quynh", "Son", "Trang", "Tuan", "Vy", "Yen"]
        last_names = ["Nguyen", "Tran", "Le", "Pham", "Hoang", "Huynh", "Phan", "Vu", "Vo", "Dang", "Bui", "Do", "Ho", "Ngo"]
        
        for i in range(1, 101):
            email = f"customer{i:03d}@example.com"
            name = f"{random.choice(last_names)} {random.choice(first_names)}"
            phone = f"09{random.randint(10000000, 99999999)}"
            address = f"{random.randint(1, 999)} Duong Le Loi, Quan {random.randint(1, 12)}, TP. Ho Chi Minh"
            
            user = User(
                email=email,
                password="password123",
                role="user",
                name=name,
                phone=phone,
                address=address,
                wishlist="[]",
                created_at=datetime.now() - timedelta(days=random.randint(30, 365))
            )
            db.session.add(user)
            mock_users.append(email)
            
        db.session.commit()
        print("Successfully created 100 mock users.")
        
        # 4. Prepare for CSV and Order generation
        csv_file = 'data/du_lieu_apriori.csv'
        os.makedirs('data', exist_ok=True)
        
        # Open CSV to write
        csv_rows = []
        
        # Total orders to generate
        total_orders = 4500
        start_date = datetime(2025, 1, 1)
        
        # Define generation probabilities
        categories = list(products_by_cat.keys())
        
        # High-probability combos to generate strong Apriori association rules
        print(f"Generating {total_orders} mock orders...")
        
        order_objects = []
        current_csv_line_count = 0
        
        for idx in range(1, total_orders + 1):
            invoice_id = f"HD{idx:05d}"
            user_email = random.choice(mock_users)
            order_date = start_date + timedelta(seconds=random.randint(0, int(timedelta(days=500).total_seconds())))
            order_date_str = order_date.strftime("%d/%m/%Y")
            
            # Select items for this order
            order_items = []
            selected_categories = []
            
            # 1. Select the first category
            first_cat = random.choice(categories)
            selected_categories.append(first_cat)
            
            # 2. Check if we trigger any combo rules (using exact database category names)
            if first_cat == "Áo thun" and random.random() < 0.80:
                selected_categories.append("Quần")
            elif first_cat == "Áo sơ mi" and random.random() < 0.75:
                selected_categories.append("Quần")
            elif first_cat == "Váy" and random.random() < 0.65:
                selected_categories.append("Giày")
            elif first_cat == "Áo khoác" and random.random() < 0.70:
                selected_categories.append("Quần")
            elif first_cat == "Cardigan" and random.random() < 0.60:
                selected_categories.append("Váy")
            elif first_cat == "Blazer" and random.random() < 0.55:
                selected_categories.append("Áo sơ mi")
            elif first_cat == "Áo body" and random.random() < 0.65:
                selected_categories.append("Váy")
            elif first_cat == "Áo len" and random.random() < 0.50:
                selected_categories.append("Áo khoác")
            elif first_cat == "Nón" and random.random() < 0.45:
                selected_categories.append("Áo thun")
            
            # 3. Sometimes add a completely random extra item
            if random.random() < 0.15:
                extra_cat = random.choice(categories)
                if extra_cat not in selected_categories:
                    selected_categories.append(extra_cat)
                    
            # 4. Build product details for selected categories
            subtotal = 0
            cart_json_items = []
            
            for cat in selected_categories:
                prod = random.choice(products_by_cat[cat])
                
                sizes = json.loads(prod.sizes) if prod.sizes else ["M"]
                colors = json.loads(prod.colors) if prod.colors else ["Đen"]
                
                size = random.choice(sizes)
                color = random.choice(colors)
                qty = random.randint(1, 2)
                price = prod.price
                
                item_total = price * qty
                subtotal += item_total
                
                cart_json_items.append({
                    "id": prod.id,
                    "name": prod.name,
                    "category": prod.category,
                    "price": price,
                    "qty": qty,
                    "size": size,
                    "color": color
                })
                
                csv_rows.append([
                    invoice_id,
                    prod.id,
                    prod.name,
                    prod.category,
                    size,
                    color,
                    qty,
                    price,
                    order_date_str
                ])
                current_csv_line_count += 1
                
            # 5. Save order details
            shipping = 0 if subtotal >= 500000 else 30000
            total = subtotal + shipping
            
            shipping_info = {
                "name": f"Recipient for {invoice_id}",
                "phone": "09" + str(random.randint(10000000, 99999999)),
                "address": "Mock Delivery Address",
                "notes": "Generated sample order"
            }
            
            order = Order(
                id=invoice_id,
                user_email=user_email,
                items=json.dumps(cart_json_items, ensure_ascii=False),
                shipping_info=json.dumps(shipping_info, ensure_ascii=False),
                subtotal=subtotal,
                shipping=shipping,
                voucher_discount=0,
                total=total,
                payment_method="cod",
                payment_status="paid",
                status="completed",
                notes="Generated sample order",
                created_at=order_date.isoformat()
            )
            order_objects.append(order)
            
            if len(order_objects) >= 500:
                db.session.bulk_save_objects(order_objects)
                db.session.commit()
                order_objects = []
                print(f"Progress: Generated {idx} orders...")
                
        # Final commit for database
        if order_objects:
            db.session.bulk_save_objects(order_objects)
            db.session.commit()
            
        print(f"Saved {total_orders} orders to SQLite database.")
        
        # 5. Write all generated data to CSV
        print(f"Writing {current_csv_line_count} rows to {csv_file}...")
        with open(csv_file, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'InvoiceID', 'ProductID', 'ProductName', 'Category', 
                'Size', 'Color', 'Quantity', 'Price', 'OrderDate'
            ])
            writer.writerows(csv_rows)
            
        print("Successfully generated data!")
        print(f"CSV line count: {current_csv_line_count + 1}")
        print(f"SQLite Order count: {Order.query.count()}")

if __name__ == '__main__':
    generate_data()
