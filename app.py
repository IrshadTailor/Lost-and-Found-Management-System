from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3

app = Flask(__name__)
app.secret_key = "your_secret_key"  # required for session & flash

# Database connection

def get_db_connection():
    conn = sqlite3.connect("lost_found.db")
    conn.row_factory = sqlite3.Row
    return conn

# Helper: Create notification

def create_notification(username, item_id, message):
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO notifications (username, item_id, message) VALUES (?, ?, ?)",
        (username, item_id, message)
    )
    conn.commit()
    conn.close()

# Initialize database tables

def init_db():
    conn = get_db_connection()

    # Users table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        );
    ''')

    # Items table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT NOT NULL,
            description TEXT,
            location TEXT,
            date TEXT,
            status TEXT NOT NULL,  -- "lost" or "found"
            reported_by TEXT,
            contact TEXT
        );
    ''')

    # Notifications table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            item_id INTEGER,
            message TEXT,
            read INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')

    conn.commit()
    conn.close()

# Home Page
@app.route("/")
def index():
    conn = get_db_connection()
    items = conn.execute("SELECT * FROM items ORDER BY id DESC").fetchall()
    conn.close()
    return render_template("index.html", items=items)

# Registration
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()

        if not username or not password:
            flash("Username and password are required!")
            return redirect(url_for("register"))

        conn = get_db_connection()
        try:
            conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            flash("Registration successful! You can now login.")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Username already exists! Choose another.")
            return redirect(url_for("register"))
        finally:
            conn.close()

    return render_template("register.html")

# Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()

        conn = get_db_connection()
        user = conn.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        ).fetchone()
        conn.close()

        if user:
            session["username"] = user["username"]
            flash(f"Welcome {user['username']}! Login successful.")
            return redirect(url_for("index"))
        else:
            flash("Invalid username or password!")
            return redirect(url_for("login"))

    return render_template("login.html")

# Logout
@app.route("/logout")
def logout():
    session.pop("username", None)
    flash("You have been logged out.")
    return redirect(url_for("login"))

# Report Lost Item
# --------------------------
@app.route("/report/lost", methods=["GET", "POST"])
def report_lost():
    if "username" not in session:
        flash("Please login to report a lost item.")
        return redirect(url_for("login"))

    if request.method == "POST":
        item_name = request.form["item_name"].strip()
        description = request.form["description"].strip()
        location = request.form["location"].strip()
        date = request.form["date"].strip()
        contact = request.form["contact"].strip()

        conn = get_db_connection()
        conn.execute(
            "INSERT INTO items (item_name, description, location, date, status, reported_by, contact) VALUES (?, ?, ?, ?, 'lost', ?, ?)",
            (item_name, description, location, date, session["username"], contact)
        )
        conn.commit()

        # Generate notifications if someone FOUND similar item
        found_matches = conn.execute(
            "SELECT * FROM items WHERE status='found' AND item_name LIKE ?",
            ("%"+item_name+"%",)
        ).fetchall()

        for f in found_matches:
            create_notification(
                session["username"],
                f["id"],
                f"Someone reported a LOST item matching '{item_name}'."
            )

        conn.close()
        flash("Lost item reported successfully!")
        return redirect(url_for("index"))

    return render_template("report_lost.html")

# Report Found Item
@app.route("/report/found", methods=["GET", "POST"])
def report_found():
    if "username" not in session:
        flash("Please login to report a found item.")
        return redirect(url_for("login"))

    if request.method == "POST":
        item_name = request.form["item_name"].strip()
        description = request.form["description"].strip()
        location = request.form["location"].strip()
        date = request.form["date"].strip()
        contact = request.form["contact"].strip()

        conn = get_db_connection()
        conn.execute(
            "INSERT INTO items (item_name, description, location, date, status, reported_by, contact) VALUES (?, ?, ?, ?, 'found', ?, ?)",
            (item_name, description, location, date, session["username"], contact)
        )
        conn.commit()

        # Notify users who lost similar items
        lost_matches = conn.execute(
            "SELECT * FROM items WHERE status='lost' AND item_name LIKE ?",
            ("%"+item_name+"%",)
        ).fetchall()

        for l in lost_matches:
            create_notification(
                l["reported_by"],
                l["id"],
                f"A FOUND item may match your lost item '{item_name}'."
            )

        conn.close()
        flash("Found item reported successfully!")
        return redirect(url_for("index"))

    return render_template("report_found.html")

# Search Items
@app.route("/search", methods=["GET", "POST"])
def search():
    items = []
    keyword = ""

    if request.method == 'POST':
        keyword = request.form.get('query', '').strip()
    else:
        keyword = request.args.get('query', '').strip()

    if keyword:
        conn = get_db_connection()
        items = conn.execute(
            "SELECT * FROM items WHERE item_name LIKE ? OR description LIKE ? ORDER BY id DESC",
            ('%'+keyword+'%', '%'+keyword+'%')
        ).fetchall()
        conn.close()

        if not items:
            flash("No items found matching your search.")

    return render_template('search.html', items=items)

# Item Details
@app.route('/item/<int:item_id>')
def item_details(item_id):
    conn = get_db_connection()
    item = conn.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()
    conn.close()

    if not item:
        flash("Item not found!")
        return redirect(url_for("index"))

    return render_template('item_details.html', item=item)

# Notifications Page
@app.route("/notifications")
def notifications():
    if "username" not in session:
        flash("Please login to view notifications.")
        return redirect(url_for("login"))

    conn = get_db_connection()
    notifs = conn.execute(
        "SELECT * FROM notifications WHERE username=? ORDER BY id DESC",
        (session["username"],)
    ).fetchall()
    conn.close()

    return render_template("notifications.html", notifications=notifs)


if __name__ == "__main__":
    init_db()  # create tables if not exists
    app.run(debug=True)
