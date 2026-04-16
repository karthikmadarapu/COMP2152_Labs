# ============================================================
#  WEEK 10 LAB — Q1: PASSWORD VAULT
#  COMP2152 — Karthik Madarapu
# ============================================================

import sqlite3


DB_NAME = "vault.db"


# --- Helpers (provided) ---
def setup_database():
    """Create the vault table if it doesn't exist."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS vault (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        website TEXT,
        username TEXT,
        password TEXT
    )""")
    conn.commit()
    conn.close()


def display_credentials(credentials):
    """Pretty-print a list of credential rows."""
    if not credentials:
        print("  (no results)")
        return
    for row in credentials:
        print(f"  {row[1]:<14} | {row[2]:<12} | {row[3]}")


# TODO: Complete add_credential(website, username, password)
#   Connect to DB_NAME.
#   INSERT a row into vault with: website, username, password.
#   Commit and close the connection.
def add_credential(website, username, password):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO vault (website, username, password) VALUES (?, ?, ?)",
        (website, username, password)
    )
    conn.commit()
    conn.close()


# TODO: Complete get_all_credentials()
#   Connect to DB_NAME.
#   SELECT all rows from vault, ordered by website ASC.
#   Fetch all rows, close the connection, and return the list.
def get_all_credentials():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM vault ORDER BY website ASC")
    rows = cursor.fetchall()
    conn.close()
    return rows 

# TODO: Complete find_credential(website)
#   Connect to DB_NAME.
#   SELECT all rows from vault WHERE website matches the parameter.
#   Fetch all rows, close the connection, and return the list.
def find_credential(website):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM vault WHERE website = ?", (website,))
    rows = cursor.fetchall()
    conn.close()
    return rows


# --- Main (provided) ---
if __name__ == "__main__":
    print("=" * 60)
    print("  PASSWORD VAULT")
    print("=" * 60)

    setup_database()

    print("\n--- Adding Credentials ---")
    credentials = [
        ("github.com",  "admin",        "s3cur3P@ss"),
        ("google.com",  "maziar@gmail",  "MyP@ssw0rd"),
        ("netflix.com", "maziar",        "N3tfl1x!"),
        ("github.com",  "work_user",    "W0rkP@ss!"),
    ]
    for site, user, pw in credentials:
        add_credential(site, user, pw)
        print(f"  Saved: {site}" + (f" ({user.split('_')[0]})" if "_" in user else ""))

    print("\n--- All Credentials ---")
    display_credentials(get_all_credentials())

    print("\n--- Search for 'github.com' ---")
    display_credentials(find_credential("github.com"))

    print("\n--- Search for 'spotify.com' ---")
    display_credentials(find_credential("spotify.com"))

    print("\n" + "=" * 60)

    # ============================================================
#  WEEK 10 LAB — Q2: LOGIN ATTEMPT TRACKER
#  COMP2152 — Karthik Madarapu
# ============================================================

import sqlite3
import datetime


DB_NAME = "login_tracker.db"


# --- Helpers (provided) ---
def setup_database():
    """Create the login_attempts table if it doesn't exist."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS login_attempts")
    cursor.execute("""CREATE TABLE login_attempts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        success INTEGER,
        attempt_date TEXT
    )""")
    conn.commit()
    conn.close()


def display_attempts(attempts):
    """Pretty-print a list of attempt rows."""
    if not attempts:
        print("  (no results)")
        return
    for row in attempts:
        status = "success" if row[2] else "FAILED"
        print(f"  {row[1]:<8} | {status:<7} | {row[3]}")


# TODO: Complete record_attempt(username, success)
#   Connect to DB_NAME.
#   INSERT a row into login_attempts with:
#     username, success (True or False), and str(datetime.datetime.now())
#   Commit and close the connection.
def record_attempt(username, success):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO login_attempts (username, success, attempt_date) VALUES (?, ?, ?)",
        (username, success, str(datetime.datetime.now()))
                   )
    conn.commit()
    conn.close()


# TODO: Complete get_failed_attempts(username)
#   Connect to DB_NAME.
#   SELECT all rows from login_attempts
#     WHERE username matches AND success = 0
#   Fetch all rows, close the connection, and return the list.
def get_failed_attempts(username):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM login_attempts WHERE username = ? AND success = 0",
                   (username,)
                   )
    rows = cursor.fetchall()
    conn.close()
    return rows


# TODO: Complete count_failures_per_user()
#   Connect to DB_NAME.
#   Execute: SELECT username, COUNT(*) FROM login_attempts
#            WHERE success = 0 GROUP BY username
#   Fetch all rows, close the connection, and return the list.
def count_failures_per_user():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT username, COUNT(*) FROM login_attempts WHERE success = 0 GROUP BY username")
    rows = cursor.fetchall()
    conn.close()
    return rows

# TODO: Complete delete_old_attempts(username)
#   Connect to DB_NAME.
#   DELETE all rows from login_attempts WHERE username matches.
#   Commit and close the connection.
#   Return cursor.rowcount (the number of rows deleted).
def delete_old_attempts(username):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM login_attempts WHERE username = ?", (username,))
    deleted = cursor.rowcount
    conn.commit()
    conn.close()
    return deleted


# --- Main (provided) ---
if __name__ == "__main__":
    print("=" * 60)
    print("  LOGIN ATTEMPT TRACKER")
    print("=" * 60)

    setup_database()

    print("\n--- Recording Login Attempts ---")
    attempts = [
        ("admin", True),
        ("admin", False),
        ("admin", False),
        ("admin", False),
        ("guest", True),
        ("guest", False),
        ("root",  False),
        ("root",  False),
        ("root",  False),
        ("root",  False),
    ]
    for user, success in attempts:
        record_attempt(user, success)
        status = "success" if success else "FAILED"
        print(f"  Recorded: {user} ({status})")

    print("\n--- Failed Attempts for 'admin' ---")
    display_attempts(get_failed_attempts("admin"))

    print("\n--- Failure Counts ---")
    counts = count_failures_per_user()
    if counts:
        for user, count in counts:
            msg = f"  {user:<10}  {count} failed attempts"
            if count >= 4:
                msg += f"  \u26a0 {user} has {count} failed attempts \u2014 possible brute-force!"
            print(msg)
    else:
        print("  (no failures)")

    print("\n--- Reset 'root' account (delete all attempts) ---")
    deleted = delete_old_attempts("root")
    if deleted:
        print(f"  Deleted {deleted} records for root")
    else:
        print("  (nothing to delete)")

    print("\n--- Failure Counts (after reset) ---")
    counts = count_failures_per_user()
    if counts:
        for user, count in counts:
            print(f"  {user:<10}  {count} failed attempts")
    else:
        print("  (no failures)")

    print("\n" + "=" * 60)

    # ============================================================
#  WEEK 10 LAB — Q3: SECURITY AUDIT LOG + UNIT TESTS
#  COMP2152 — Karthik Madarapu
# ============================================================

import sqlite3
import unittest


DB_NAME = "audit.db"


# --- Helpers (provided) — seeds the database with sample data ---
def seed_database():
    """Create and populate the audit_log table with sample security events."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS audit_log")
    cursor.execute("""CREATE TABLE audit_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        user TEXT,
        action TEXT,
        severity TEXT,
        details TEXT
    )""")
    sample_data = [
        ("2026-03-16 08:00:00", "admin",   "LOGIN",           "LOW",    "Successful login from 192.168.1.10"),
        ("2026-03-16 08:05:00", "root",    "FAILED_LOGIN",    "HIGH",   "Failed SSH attempt from 10.0.0.99"),
        ("2026-03-16 08:10:00", "admin",   "FILE_ACCESS",     "LOW",    "Read /etc/config.yaml"),
        ("2026-03-16 08:15:00", "root",    "FAILED_LOGIN",    "HIGH",   "Failed SSH attempt from 10.0.0.99"),
        ("2026-03-16 08:20:00", "guest",   "FILE_MODIFY",     "MEDIUM", "Modified /tmp/upload.csv"),
        ("2026-03-16 08:25:00", "admin",   "PERMISSION_CHANGE","HIGH",  "Changed permissions on /etc/shadow"),
        ("2026-03-16 08:30:00", "guest",   "LOGOUT",          "LOW",    "Session ended normally"),
        ("2026-03-16 08:35:00", "backup",  "FILE_ACCESS",     "LOW",    "Read /var/backups/db.sql"),
        ("2026-03-16 08:40:00", "guest",   "FILE_MODIFY",     "MEDIUM", "Modified /tmp/data.json"),
        ("2026-03-16 08:45:00", "admin",   "LOGOUT",          "LOW",    "Session ended normally"),
    ]
    cursor.executemany(
        "INSERT INTO audit_log (timestamp, user, action, severity, details) VALUES (?, ?, ?, ?, ?)",
        sample_data
    )
    conn.commit()
    conn.close()


def display_events(events):
    """Pretty-print a list of audit events."""
    if not events:
        print("  (no events)")
        return
    for row in events:
        print(f"  [{row[1]}]  {row[4]:<6}  {row[2]:<8}  {row[3]:<18}  {row[5]}")


# TODO: Complete get_events_by_severity(severity)
#   Connect to DB_NAME.
#   SELECT all rows from audit_log WHERE severity matches the parameter.
#   Fetch all rows, close the connection, and return the list.
def get_events_by_severity(severity):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.execute("SELECT * FROM audit_log WHERE severity = ?", (severity,))
        return cursor.fetchall()


# TODO: Complete get_recent_events(limit)
#   Connect to DB_NAME.
#   SELECT all rows from audit_log ORDER BY timestamp DESC LIMIT ?
#   Use the limit parameter for the LIMIT value.
#   Fetch all rows, close the connection, and return the list.
def get_recent_events(limit):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.execute("SELECT * FROM audit_log ORDER BY timestamp DESC LIMIT ?", (limit,))
        return cursor.fetchall()


# TODO: Complete count_by_severity()
#   Connect to DB_NAME.
#   Execute: SELECT severity, COUNT(*) FROM audit_log
#            GROUP BY severity ORDER BY COUNT(*) DESC
#   Fetch all rows, close the connection, and return the list.
def count_by_severity():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.execute("SELECT severity, COUNT(*) FROM audit_log GROUP BY severity ORDER BY COUNT(*) DESC")
        return cursor.fetchall()



# TODO: Complete safe_query(query)
#   Connect to DB_NAME.
#   Try to execute the query using cursor.execute(query).
#   If successful, fetch all rows and return them.
#   If sqlite3.Error occurs, print f"Database error: {e}" and return [].
#   Always close the connection in a finally block.
def safe_query(query):
    conn = sqlite3.connect(DB_NAME)
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        return rows
    except sqlite3.Error as e:
        print(f" Database Error: {e}")
        return []
    finally:
        conn.close()



# ============================================================
#  UNIT TESTS — fill in the test methods
# ============================================================
class TestAuditLog(unittest.TestCase):

    def setUp(self):
        seed_database()

    def test_high_severity(self):
        events = get_events_by_severity("HIGH")
        self.assertEqual(len(events), 3)

    def test_recent_events(self):
        events = get_recent_events(5)
        self.assertEqual(len(events), 5)

    def test_count(self):
        counts = count_by_severity()
        self.assertIn(("HIGH", 3), counts)

    def test_safe_bad_query(self):
        result = safe_query("SELECT * FROM fake_table")
        self.assertEqual(result, [])

# --- Main (provided) ---
if __name__ == "__main__":
    print("=" * 60)
    print("  SECURITY AUDIT LOG")
    print("=" * 60)

    seed_database()

    print("\n--- HIGH Severity Events ---")
    display_events(get_events_by_severity("HIGH"))

    print("\n--- 5 Most Recent Events ---")
    display_events(get_recent_events(5))

    print("\n--- Event Counts by Severity ---")
    counts = count_by_severity()
    if counts:
        for severity, count in counts:
            print(f"  {severity:<8}  {count}")
    else:
        print("  (none)")

    print("\n--- Safe Query (valid) ---")
    results = safe_query("SELECT user, action FROM audit_log WHERE severity = 'HIGH'")
    if results:
        for row in results:
            print(f"  {row[0]:<8}  {row[1]}")

    print("\n--- Safe Query (invalid — should not crash) ---")
    results = safe_query("SELECT * FROM nonexistent_table")
    print(f"  Returned: {results}")

    print("\n--- Running Unit Tests ---")
    unittest.main(verbosity=2, exit=False)

    print("\n" + "=" * 60)