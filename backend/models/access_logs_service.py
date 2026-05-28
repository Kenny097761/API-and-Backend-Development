from datetime import datetime
from backend.models.db_connect import get_connection

def create_login_log(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        now = datetime.now()
        login_time = now.strftime("%Y-%m-%d %H:%M:%S")
        log_date = now.strftime("%Y-%m-%d")

        cursor.execute("""
            INSERT INTO access_logs (user_id, login_time, log_date)
            VALUES (?, ?, ?)
        """, (user_id, login_time, log_date))

        conn.commit()

        return cursor.lastrowid

    except Exception as e:
        conn.rollback()
        raise e

    finally:
        conn.close()

def update_logout_log(log_id):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        logout_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("""
            UPDATE access_logs
            SET logout_time = ?
            WHERE log_id = ?
        """, (logout_time, log_id))

        conn.commit()

    except Exception as e:
        conn.rollback()
        raise e

    finally:
        conn.close()