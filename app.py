import sqlite3
from flask import Flask, flash, redirect, render_template, request, session, url_for

app = Flask(__name__)
app.secret_key = "super_secret_amazon_key"  # Encrypts user cookie sessions


def get_db_connection():
    conn = sqlite3.connect("ecommerce.db")
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    # Create database tables for users and items
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL, password TEXT NOT NULL)"
    )
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, price REAL NOT NULL, description TEXT, image_url TEXT)"
    )

    # Put mock stock items into the store database if it's empty
    cursor.execute("SELECT COUNT(*) FROM products")
    if cursor.fetchone()[0] == 0:
        mock_products = [
            (
                "Wireless Headphones",
                199.99,
                "Active noise canceling.",
                "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500",
            ),
            (
                "Mechanical Keyboard",
                89.50,
                "RGB backlit tactile gaming keys.",
                "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=500",
            ),
            (
                "Smart Watch",
                149.00,
                "Track fitness and notifications.",
                "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500",
            ),
        ]
        cursor.executemany(
            "INSERT INTO products (name, price, description, image_url) VALUES (?, ?, ?, ?)",
            mock_products,
        )
    conn.commit()
    conn.close()


init_db()


# 1. Homepage (Product Feed)
@app.route("/")
def index():
    conn = get_db_connection()
    products = conn.execute("SELECT * FROM products").fetchall()
    conn.close()
    return render_template("index.html", products=products)


# 2. Login & Sign Up
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        action = request.form["action"]
        conn = get_db_connection()
        cursor = conn.cursor()

        if action == "register":
            try:
                cursor.execute(
                    "INSERT INTO users (username, password) VALUES (?, ?)",
                    (username, password),
                )
                conn.commit()
                flash("Registered! Please sign in.", "success")
            except sqlite3.IntegrityError:
                flash("Username already exists.", "danger")
        elif action == "login":
            user = cursor.execute(
                "SELECT * FROM users WHERE username = ? AND password = ?",
                (username, password),
            ).fetchone()
            if user:
                session["user_id"] = user["id"]
                session["username"] = user["username"]
                return redirect(url_for("index"))
            else:
                flash("Invalid username or password.", "danger")
        conn.close()
    return render_template("login.html")


# 3. Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


# 4. Add items to Cart
@app.route("/add_to_cart/<int:product_id>")
def add_to_cart(product_id):
    if "cart" not in session:
        session["cart"] = []
    cart = session["cart"]
    cart.append(product_id)
    session["cart"] = cart
    flash("Item added to cart!", "success")
    return redirect(url_for("index"))


# 5. Display Cart
@app.route("/cart")
def view_cart():
    cart_ids = session.get("cart", [])
    if not cart_ids:
        return render_template("cart.html", products=[], total=0)
    conn = get_db_connection()
    placeholders = ",".join("?" for _ in cart_ids)
    products = conn.execute(
        f"SELECT * FROM products WHERE id IN ({placeholders})", cart_ids
    ).fetchall()
    conn.close()
    product_map = {p["id"]: p for p in products}
    cart_items = [product_map[pid] for pid in cart_ids if pid in product_map]
    total = sum(item["price"] for item in cart_items)
    return render_template("cart.html", products=cart_items, total=round(total, 2))

@app.route('/admin')
def admin_page():
    try:
        conn = get_db_connection()
        all_users = conn.execute("SELECT * FROM users").fetchall()
        conn.close()
    except:
        all_users = []
    return render_template('admin.html', users=all_users)

def init_products():
    try:
        conn = get_db_connection()
        count = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        if count == 0:
            sample_products = [
                ("Wireless Headphones", 2499.00, "High-quality bass wireless over-ear headphones.", "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500"),
                ("Smart Watch", 3999.00, "Fitness tracker with heart rate monitor and AMOLED display.", "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500"),
                ("Bluetooth Speaker", 1499.00, "Portable waterproof speaker with 12h playtime.", "https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?w=500"),
                ("Gaming Mouse", 999.00, "Ergonomic RGB gaming mouse with adjustable DPI.", "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=500"),
                ("Mechanical Keyboard", 2999.00, "Tactile blue-switch mechanical keyboard with backlighting.", "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=500"),
                ("Classic Black T-Shirt", 499.00, "100% premium cotton everyday wear plain black tee.", "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?w=500"),
                ("Denim Jacket", 1899.00, "Vintage blue washed slim-fit denim jacket.", "https://images.unsplash.com/photo-1576995853123-5a10305d93c0?w=500"),
                ("Running Shoes", 2499.00, "Lightweight breathable sports sneakers for running.", "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=500"),
                ("White Sneakers", 1299.00, "Minimalist casual white leather lace-up sneakers.", "https://images.unsplash.com/photo-1600185365483-26d7a4cc7519?w=500"),
                ("Leather Wallet", 699.00, "Genuine bi-fold leather wallet with RFID blocking.", "https://images.unsplash.com/photo-1627123424574-724758594e93?w=500"),
                ("Travel Backpack", 1599.00, "Water-resistant laptop backpack with USB charging port.", "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=500"),
                ("Classic Sunglasses", 799.00, "Polarized retro aviator sunglasses with UV protection.", "https://images.unsplash.com/photo-1511499767150-a48a237f0083?w=500"),
                ("Stainless Steel Bottle", 599.00, "Vacuum insulated double-walled hot and cold water flask.", "https://images.unsplash.com/photo-1602143407151-7111542de6e8?w=500"),
                ("Minimalist Watch", 1999.00, "Elegant analog wristwatch with a sleek leather strap.", "https://images.unsplash.com/photo-1522312346375-d1a52e2b99b3?w=500"),
                ("Duffle Bag", 1199.00, "Spacious sports duffle bag with a separate shoe compartment.", "https://images.unsplash.com/photo-1544816155-12df9643f363?w=500"),
                ("Desk Mat / Mousepad", 449.00, "Extended large anti-slip rubber base stitched-edge desk pad.", "https://images.unsplash.com/photo-1616440347437-b1c73416efc2?w=500"),
                ("Notebook & Pen Set", 349.00, "A5 hardcover ruled journal notebook with a premium gel pen.", "https://images.unsplash.com/photo-1531346878377-a5be20888e57?w=500"),
                ("Ceramic Coffee Mug", 299.00, "Matte finish minimalist ceramic mug for tea and coffee.", "https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?w=500"),
                ("Table Lamp", 999.00, "Adjustable wooden swing-arm desk lamp for studying.", "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=500"),
                ("Scented Candle", 399.00, "Relaxing lavender aromatherapy wax candle in a glass jar.", "https://images.unsplash.com/photo-1603006905003-be475563bc59?w=500")
            ]
            conn.executemany("INSERT INTO products (name, price, description, image_url) VALUES (?, ?, ?, ?)", sample_products)
            conn.commit()
        conn.close()
    except Exception as e:
        print("Database population notice:", e)

if __name__ == "__main__":
    import os

port = int(os.environ.get("PORT", 5000))      
app.run(host="0.0.0.0", port=port)
