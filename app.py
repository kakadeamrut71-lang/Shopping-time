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


if __name__ == "__main__":
    import os

port = int(os.environ.get("PORT", 5000))      
app.run(host="0.0.0.0", port=port)
