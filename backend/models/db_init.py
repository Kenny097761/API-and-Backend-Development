from backend.models.db_connect import get_connection

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            email VARCHAR(100) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL,
            status VARCHAR(20) NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            customer_id INTEGER PRIMARY KEY,
            first_name VARCHAR(50) NOT NULL,
            last_name VARCHAR(50) NOT NULL,
            phone VARCHAR(20),
            street_number VARCHAR(10),
            street_name VARCHAR(100),
            suburb VARCHAR(100),
            postcode VARCHAR(10),
            FOREIGN KEY (customer_id) REFERENCES users(user_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS staff (
            staff_id INTEGER PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            staff_code VARCHAR(50) UNIQUE,
            position VARCHAR(50),
            FOREIGN KEY (staff_id) REFERENCES users(user_id)
        )
    """)

    # ACCESS LOG TABLE 
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS access_logs (
            log_id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            login_time TEXT NOT NULL,
            logout_time TEXT,
            log_date TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS devices (
            device_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) NOT NULL,
            type VARCHAR(50) NOT NULL,
            unit_price FLOAT NOT NULL,
            stock INT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            status TEXT NOT NULL CHECK(status IN('saved','paid','cancelled')),
            total_price FLOAT NOT NULL,
            created_at DATETIME NOT NULL,
            FOREIGN KEY (customer_id) REFERENCES users(user_id)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS order_items(
            order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            device_id INTEGER NOT NULL,
            total_price FLOAT NOT NULL,
            quantity INTEGER NOT NULL CHECK(quantity>0),
            FOREIGN KEY(order_id) REFERENCES orders(order_id),
            FOREIGN KEY(device_id) REFERENCES devices(device_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS payment_methods (
            payment_method_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            type VARCHAR(20) NOT NULL,
            nickname VARCHAR(100) NOT NULL,
            cardholder_name VARCHAR(100),
            card_brand VARCHAR(50),
            card_last_four VARCHAR(4),
            expiry_date VARCHAR(5),
            account_name VARCHAR(100),
            bsb_last_three VARCHAR(3),
            account_last_four VARCHAR(4),
            paypal_email_masked VARCHAR(150),
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL UNIQUE,
            customer_id INTEGER NOT NULL,
            payment_method_id INTEGER NOT NULL,
            amount FLOAT NOT NULL,
            status VARCHAR(20) NOT NULL DEFAULT 'paid',
            paid_at DATETIME NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(order_id),
            FOREIGN KEY (customer_id) REFERENCES users(user_id),
            FOREIGN KEY (payment_method_id) REFERENCES payment_methods(payment_method_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS shipments (
            shipment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER UNIQUE,
            staff_id INTEGER,
            status VARCHAR(20) NOT NULL DEFAULT 'pending',
            street_number VARCHAR(10) NOT NULL,
            street_name VARCHAR(100) NOT NULL,
            suburb VARCHAR(100) NOT NULL,
            postcode VARCHAR(10) NOT NULL,
            created_at DATETIME NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(order_id),
            FOREIGN KEY (staff_id) REFERENCES users(user_id)
        )
    """)

    # --- Seed users + customers ---
    cursor.execute("SELECT * FROM users WHERE email = ?", ("alice@iotbay.com",))
    if cursor.fetchone() is None:
        cursor.execute(
            "INSERT INTO users (email, password, status) VALUES (?, ?, ?)",
            ("alice@iotbay.com", "password123", "active"),
        )
        alice_id = cursor.lastrowid
        cursor.execute(
            "INSERT INTO users (email, password, status) VALUES (?, ?, ?)",
            ("bob@iotbay.com", "password123", "active"),
        )
        bob_id = cursor.lastrowid
        cursor.execute(
            "INSERT INTO users (email, password, status) VALUES (?, ?, ?)",
            ("staff1@iotbay.com", "password123", "active"),
        )
        staff1_id = cursor.lastrowid
        cursor.execute(
            "INSERT INTO users (email, password, status) VALUES (?, ?, ?)",
            ("staff2@iotbay.com", "password123", "active"),
        )
        staff2_id = cursor.lastrowid

        cursor.execute("SELECT COUNT(*) FROM customers")
        if cursor.fetchone()[0] == 0:
            cursor.execute(
                """INSERT INTO customers
                   (customer_id, first_name, last_name, phone,
                    street_number, street_name, suburb, postcode)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (alice_id, "Alice", "Nguyen", "0400000001",
                 "12", "King St", "Newtown", "2042"),
            )
            cursor.execute(
                """INSERT INTO customers
                   (customer_id, first_name, last_name, phone,
                    street_number, street_name, suburb, postcode)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (bob_id, "Bob", "Smith", "0400000002",
                 "99", "Queen St", "Surry Hills", "2010"),
            )

        cursor.execute("SELECT COUNT(*) FROM staff")
        if cursor.fetchone()[0] == 0:
            cursor.execute(
                "INSERT INTO staff (staff_id, name, staff_code, position) VALUES (?, ?, ?, ?)",
                (staff1_id, "Diana Lee", "ST001", "Warehouse"),
            )
        cursor.execute(
                "INSERT INTO staff (staff_id, name, staff_code, position) VALUES (?, ?, ?, ?)",
                (staff2_id, "Evan Park", "ST002", "Warehouse"),
            )

        cursor.execute(
            "INSERT INTO devices (name, type, unit_price, stock) VALUES (?, ?, ?, ?)",
            ("Smart Sensor", "Sensor", 60.00, 10)
        )
        cursor.execute(
            "INSERT INTO devices (name, type, unit_price, stock) VALUES (?, ?, ?, ?)",
            ("IoT Camera", "Camera", 250.00, 5)
        )
        cursor.execute(
            "INSERT INTO devices (name, type, unit_price, stock) VALUES (?, ?, ?, ?)",
            ("GPS Tracker", "Tracker", 90.00, 15)
        )

        cursor.execute(
            "INSERT INTO orders (customer_id, status, total_price, created_at) VALUES (?, ?, ?, datetime('now'))",
            (alice_id, "saved", 199.99)
        )
        order1_id = cursor.lastrowid
        cursor.execute(
            "INSERT INTO orders (customer_id, status, total_price, created_at) VALUES (?, ?, ?, datetime('now'))",
            (alice_id, "paid", 250.00),
        )
        order2_id = cursor.lastrowid
        cursor.execute(
            "INSERT INTO orders (customer_id, status, total_price, created_at) VALUES (?, ?, ?, datetime('now'))",
            (alice_id, "saved", 75.00)
        )
        order3_id = cursor.lastrowid
        cursor.execute(
            "INSERT INTO orders (customer_id, status, total_price, created_at) VALUES (?, ?, ?, datetime('now'))",
            (bob_id, "paid", 120.00)
        )
        order4_id = cursor.lastrowid
        cursor.execute(
            "INSERT INTO orders (customer_id, status, total_price, created_at) VALUES (?, ?, ?, datetime('now'))",
            (alice_id, "paid", 350.00)
        )
        order5_id = cursor.lastrowid
        cursor.execute(
            "INSERT INTO orders (customer_id, status, total_price, created_at) VALUES (?, ?, ?, ?)",
            (bob_id, "cancelled", 89.99, "2025-03-10 10:00:00")
        )
        cursor.execute(
            "INSERT INTO orders (customer_id, status, total_price, created_at) VALUES (?, ?, ?, ?)",
            (bob_id, "paid", 45.00, "2025-03-15 09:15:00")
        )
        cursor.execute(
            "INSERT INTO orders (customer_id, status, total_price, created_at) VALUES (?, ?, ?, ?)",
            (alice_id, "paid", 67.50, "2025-03-22 16:30:00")
        )

        cursor.execute(
            "INSERT INTO order_items (order_id, device_id, quantity, total_price) VALUES (?, ?, ?, ?)",
            (order1_id, 1, 2, 120.00)
        )
        cursor.execute(
            "INSERT INTO order_items (order_id, device_id, quantity, total_price) VALUES (?, ?, ?, ?)",
            (order1_id, 3, 1, 90.00)
        )
        cursor.execute(
            "INSERT INTO order_items (order_id, device_id, quantity, total_price) VALUES (?, ?, ?, ?)",
            (order4_id, 1, 2, 120.00)
        )
        cursor.execute(
            "INSERT INTO order_items (order_id, device_id, quantity, total_price) VALUES (?, ?, ?, ?)",
            (order2_id, 3, 1, 250.00)
        )

    cursor.execute("SELECT COUNT(*) FROM payment_methods")
    if cursor.fetchone()[0] == 0:
        cursor.execute("SELECT user_id FROM users WHERE email = ?", ("alice@iotbay.com",))
        alice_id = cursor.fetchone()[0]
        cursor.execute("SELECT user_id FROM users WHERE email = ?", ("bob@iotbay.com",))
        bob_id = cursor.fetchone()[0]

        cursor.execute("""
            INSERT INTO payment_methods
            (user_id, type, nickname, cardholder_name, card_brand, card_last_four, expiry_date, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
        """, (alice_id, "card", "Alice Visa", "Alice Nguyen", "Visa", "4242", "12/27"))

        cursor.execute("""
            INSERT INTO payment_methods
            (user_id, type, nickname, cardholder_name, card_brand, card_last_four, expiry_date, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
        """, (alice_id, "card", "Alice Mastercard", "Alice Nguyen", "Mastercard", "5454", "08/28"))

        cursor.execute("""
            INSERT INTO payment_methods
            (user_id, type, nickname, paypal_email_masked, created_at)
            VALUES (?, ?, ?, ?, datetime('now'))
        """, (bob_id, "paypal", "Bob PayPal", "bo***@example.com"))

    cursor.execute("SELECT COUNT(*) FROM shipments")
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            """INSERT INTO shipments
                (order_id, staff_id, status,
                street_number, street_name, suburb, postcode, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))""",
            (order2_id, staff1_id, "pending",
                "12", "King St", "Newtown", "2042"),
        )
        cursor.execute(
            """INSERT INTO shipments
                (order_id, staff_id, status,
                street_number, street_name, suburb, postcode, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))""",
            (order5_id, staff2_id, "shipped",
                "12", "King St", "Newtown", "2042"),
        )

    #create admin user
    cursor.execute("""
        SELECT * FROM users
        WHERE email = ?
    """, ("admin@iotbay.com",))
    admin = cursor.fetchone()
    if admin is None:
        cursor.execute("""
            INSERT INTO users (email, password, status)
            VALUES (?, ?, ?)
        """, ("admin@iotbay.com", "admin123", "active"))
        admin_id = cursor.lastrowid
        cursor.execute("""
            INSERT INTO staff (staff_id, name, staff_code, position)
            VALUES (?, ?, ?, ?)
        """, (admin_id, "Admin User", "ADMIN001", "Administrator"))

    # create basic customer user
    cursor.execute("""
        SELECT * FROM users
        WHERE email = ?
    """, ("customer@iotbay.com",))
    basic_customer = cursor.fetchone()
    if basic_customer is None:
        cursor.execute("""
            INSERT INTO users (email, password, status)
            VALUES (?, ?, ?)
        """, ("customer@iotbay.com", "customer123", "active"))
        customer_id = cursor.lastrowid
        cursor.execute("""
            INSERT INTO customers (customer_id, first_name, last_name, phone, street_number, street_name, suburb, postcode)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (customer_id, "Test", "Customer", "0400000000", "1", "Test St", "Sydney", "2000"))
        cursor.execute("""
            INSERT INTO payment_methods
            (user_id, type, nickname, cardholder_name, card_brand, card_last_four, expiry_date, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
        """, (customer_id, "card", "Visa1", "Test Customer", "Visa", "1111", "12/30"))

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
