from backend.models.db_connect import get_connection

def show_db_connection():
    conn = get_connection()
    try:
        print("Connected to app.db successfully.")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row["name"] for row in cursor.fetchall()]
        print("Tables:", tables)
    finally:
        conn.close()
        print("Connection closed.")

# Show data from database 
def show_data():
    conn = get_connection()
    cursor = conn.cursor()

    print("\n=== USERS ===")
    cursor.execute("SELECT * FROM users")
    for row in cursor.fetchall():
        print(dict(row))

    print("\n=== CUSTOMERS ===")
    cursor.execute("SELECT * FROM customers")
    for row in cursor.fetchall():
        print(dict(row))

    print("\n=== ACCESS_LOGS ===")
    cursor.execute("SELECT * FROM access_logs")
    logs = cursor.fetchall()

    for log in logs:
        print(dict(log))

    conn.close()

if __name__ == "__main__":
    show_db_connection()
    show_data()