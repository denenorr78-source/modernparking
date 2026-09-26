import datetime as dt
import os
import shutil
import sqlite3
from pathlib import Path

from security import hash_password


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "parking_system.db"
BACKUP_DIR = BASE_DIR / "backups"

DEFAULT_RATES = {
    "CAR": 100,
    "BIKE": 50,
    "TRUCK": 150,
    "BUS": 200,
}


class Database:
    def __init__(self, db_path=DB_PATH):
        self.db_path = Path(db_path)
        BACKUP_DIR.mkdir(exist_ok=True)

    def connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA busy_timeout = 5000")
        return conn

    def initialize(self):
        if self.db_path.exists():
            with sqlite3.connect(self.db_path) as probe:
                user_row = probe.execute(
                    "SELECT sql FROM sqlite_master WHERE type='table' AND name='users'"
                ).fetchone()
                if user_row and "customer" not in (user_row[0] or "").lower():
                    backup_path = self.db_path.with_suffix(".legacy_backup.db")
                    if backup_path.exists():
                        backup_path.unlink()
                    shutil.copy2(self.db_path, backup_path)
                    self.db_path.unlink()

        with self.connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL CHECK(role IN ('admin', 'attendant', 'customer')),
                    full_name TEXT NOT NULL,
                    active INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL,
                    last_login TEXT
                );

                CREATE TABLE IF NOT EXISTS slots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    slot_code TEXT UNIQUE NOT NULL,
                    status TEXT NOT NULL DEFAULT 'available'
                        CHECK(status IN ('available', 'occupied'))
                );

                CREATE TABLE IF NOT EXISTS vehicles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    reg_no TEXT UNIQUE NOT NULL,
                    owner_name TEXT NOT NULL,
                    phone TEXT NOT NULL,
                    vehicle_type TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS parking_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    vehicle_id INTEGER NOT NULL,
                    slot_id INTEGER NOT NULL,
                    arrival TEXT NOT NULL,
                    departure TEXT,
                    billable_hours INTEGER,
                    status TEXT NOT NULL DEFAULT 'active'
                        CHECK(status IN ('active', 'completed')),
                    created_by INTEGER NOT NULL,
                    checked_out_by INTEGER,
                    FOREIGN KEY(vehicle_id) REFERENCES vehicles(id),
                    FOREIGN KEY(slot_id) REFERENCES slots(id),
                    FOREIGN KEY(created_by) REFERENCES users(id),
                    FOREIGN KEY(checked_out_by) REFERENCES users(id)
                );

                CREATE TABLE IF NOT EXISTS payments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER UNIQUE NOT NULL,
                    receipt_no TEXT UNIQUE NOT NULL,
                    amount INTEGER NOT NULL,
                    payment_method TEXT NOT NULL,
                    paid_at TEXT NOT NULL,
                    received_by INTEGER NOT NULL,
                    FOREIGN KEY(session_id) REFERENCES parking_sessions(id),
                    FOREIGN KEY(received_by) REFERENCES users(id)
                );

                CREATE TABLE IF NOT EXISTS activity_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    action TEXT NOT NULL,
                    details TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                );

                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );
                """
            )

            self._seed_settings(conn)
            self._seed_slots(conn)
            self._seed_admin(conn)

    def _seed_settings(self, conn):
        settings = {
            "CAR_RATE": "100",
            "BIKE_RATE": "50",
            "TRUCK_RATE": "150",
            "BUS_RATE": "200",
            "CURRENCY": "KSh",
            "PARKING_NAME": "MODERN PARKING SYSTEM",
        }

        for key, value in settings.items():
            conn.execute(
                "INSERT OR IGNORE INTO settings(key, value) VALUES (?, ?)",
                (key, value),
            )

    def _seed_slots(self, conn):
        count = conn.execute("SELECT COUNT(*) AS c FROM slots").fetchone()["c"]
        if count == 0:
            for number in range(1, 21):
                conn.execute(
                    "INSERT INTO slots(slot_code) VALUES (?)",
                    (f"A{number:02d}",),
                )

    def _seed_admin(self, conn):
        count = conn.execute("SELECT COUNT(*) AS c FROM users").fetchone()["c"]
        if count == 0:
            now = self.now()
            conn.execute(
                """
                INSERT INTO users
                (username, password_hash, role, full_name, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    "Dene",
                    hash_password("8346@Dene"),
                    "admin",
                    "System Admin",
                    now,
                ),
            )

    @staticmethod
    def now():
        return dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def get_setting(self, key, default=None):
        with self.connect() as conn:
            row = conn.execute(
                "SELECT value FROM settings WHERE key = ?", (key,)
            ).fetchone()
            return row["value"] if row else default

    def set_setting(self, key, value):
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO settings(key, value) VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value
                """,
                (key, str(value)),
            )

    def get_rates(self):
        return {
            "CAR": int(self.get_setting("CAR_RATE", 100)),
            "BIKE": int(self.get_setting("BIKE_RATE", 50)),
            "TRUCK": int(self.get_setting("TRUCK_RATE", 150)),
            "BUS": int(self.get_setting("BUS_RATE", 200)),
        }

    def authenticate(self, username):
        with self.connect() as conn:
            return conn.execute(
                "SELECT * FROM users WHERE username = ? AND active = 1",
                (username,),
            ).fetchone()

    def record_login(self, user_id):
        with self.connect() as conn:
            conn.execute(
                "UPDATE users SET last_login = ? WHERE id = ?",
                (self.now(), user_id),
            )

    def log(self, user_id, action, details):
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO activity_logs(user_id, action, details, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (user_id, action, details, self.now()),
            )

    def dashboard_stats(self):
        with self.connect() as conn:
            available = conn.execute(
                "SELECT COUNT(*) AS c FROM slots WHERE status='available'"
            ).fetchone()["c"]
            occupied = conn.execute(
                "SELECT COUNT(*) AS c FROM slots WHERE status='occupied'"
            ).fetchone()["c"]
            total = conn.execute(
                "SELECT COUNT(*) AS c FROM slots"
            ).fetchone()["c"]
            revenue = conn.execute(
                "SELECT COALESCE(SUM(amount), 0) AS total FROM payments"
            ).fetchone()["total"]

            return {
                "available": available,
                "occupied": occupied,
                "total": total,
                "revenue": revenue,
            }

    def slot_status(self):
        with self.connect() as conn:
            return conn.execute(
                "SELECT * FROM slots ORDER BY slot_code"
            ).fetchall()

    def park_vehicle(self, reg_no, owner, phone, vehicle_type, user_id):
        now = self.now()

        with self.connect() as conn:
            existing = conn.execute(
                "SELECT id FROM vehicles WHERE reg_no = ?", (reg_no,)
            ).fetchone()

            if existing:
                vehicle_id = existing["id"]
                active = conn.execute(
                    """
                    SELECT id FROM parking_sessions
                    WHERE vehicle_id = ? AND status = 'active'
                    """,
                    (vehicle_id,),
                ).fetchone()

                if active:
                    raise ValueError("This vehicle is already parked.")

                conn.execute(
                    """
                    UPDATE vehicles
                    SET owner_name = ?, phone = ?, vehicle_type = ?
                    WHERE id = ?
                    """,
                    (owner, phone, vehicle_type, vehicle_id),
                )
            else:
                cursor = conn.execute(
                    """
                    INSERT INTO vehicles
                    (reg_no, owner_name, phone, vehicle_type, created_at)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (reg_no, owner, phone, vehicle_type, now),
                )
                vehicle_id = cursor.lastrowid

            slot = conn.execute(
                """
                SELECT id, slot_code FROM slots
                WHERE status = 'available'
                ORDER BY slot_code
                LIMIT 1
                """
            ).fetchone()

            if not slot:
                raise ValueError("Parking is full.")

            cursor = conn.execute(
                """
                INSERT INTO parking_sessions
                (vehicle_id, slot_id, arrival, created_by)
                VALUES (?, ?, ?, ?)
                """,
                (vehicle_id, slot["id"], now, user_id),
            )

            conn.execute(
                "UPDATE slots SET status='occupied' WHERE id=?",
                (slot["id"],),
            )

            session_id = cursor.lastrowid

            conn.execute(
                """
                INSERT INTO activity_logs(user_id, action, details, created_at)
                VALUES (?, 'PARK', ?, ?)
                """,
                (user_id, f"{reg_no} parked in {slot['slot_code']}", now),
            )

            return session_id, slot["slot_code"], now

    def parked_vehicles(self):
        with self.connect() as conn:
            return conn.execute(
                """
                SELECT
                    ps.id AS session_id,
                    v.reg_no,
                    v.owner_name,
                    v.phone,
                    v.vehicle_type,
                    s.slot_code,
                    ps.arrival
                FROM parking_sessions ps
                JOIN vehicles v ON v.id = ps.vehicle_id
                JOIN slots s ON s.id = ps.slot_id
                WHERE ps.status = 'active'
                ORDER BY ps.arrival DESC
                """
            ).fetchall()

    def find_active_vehicle(self, reg_no):
        with self.connect() as conn:
            return conn.execute(
                """
                SELECT
                    ps.id AS session_id,
                    v.id AS vehicle_id,
                    v.reg_no,
                    v.owner_name,
                    v.phone,
                    v.vehicle_type,
                    s.slot_code,
                    ps.arrival,
                    ps.slot_id
                FROM parking_sessions ps
                JOIN vehicles v ON v.id = ps.vehicle_id
                JOIN slots s ON s.id = ps.slot_id
                WHERE v.reg_no = ? AND ps.status = 'active'
                """,
                (reg_no,),
            ).fetchone()

    def checkout(self, reg_no, user_id, payment_method):
        now_dt = dt.datetime.now()
        now = now_dt.strftime("%Y-%m-%d %H:%M:%S")

        with self.connect() as conn:
            row = conn.execute(
                """
                SELECT
                    ps.id AS session_id,
                    ps.vehicle_id,
                    ps.slot_id,
                    ps.arrival,
                    ps.departure,
                    ps.billable_hours,
                    ps.status,
                    ps.created_by,
                    ps.checked_out_by,
                    v.reg_no,
                    v.owner_name,
                    v.vehicle_type,
                    s.slot_code
                FROM parking_sessions ps
                JOIN vehicles v ON v.id = ps.vehicle_id
                JOIN slots s ON s.id = ps.slot_id
                WHERE v.reg_no = ? AND ps.status = 'active'
                """,
                (reg_no,),
            ).fetchone()

            if not row:
                raise ValueError("No active parking session found.")

            arrival = dt.datetime.strptime(
                row["arrival"], "%Y-%m-%d %H:%M:%S"
            )

            seconds = max(0, (now_dt - arrival).total_seconds())
            billable_hours = max(1, int((seconds + 3599) // 3600))

            rate = self.get_rates()[row["vehicle_type"]]
            amount = billable_hours * rate

            receipt_no = (
                f"RCP-{now_dt.strftime('%Y%m%d%H%M%S')}-"
                f"{row['session_id']:04d}"
            )

            conn.execute(
                """
                UPDATE parking_sessions
                SET departure=?, billable_hours=?,
                    status='completed', checked_out_by=?
                WHERE id=?
                """,
                (now, billable_hours, user_id, row["session_id"]),
            )

            conn.execute(
                "UPDATE slots SET status='available' WHERE id=?",
                (row["slot_id"],),
            )

            conn.execute(
                """
                INSERT INTO payments
                (session_id, receipt_no, amount, payment_method,
                 paid_at, received_by)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    row["session_id"],
                    receipt_no,
                    amount,
                    payment_method,
                    now,
                    user_id,
                ),
            )

            conn.execute(
                """
                INSERT INTO activity_logs(user_id, action, details, created_at)
                VALUES (?, 'CHECKOUT', ?, ?)
                """,
                (
                    user_id,
                    f"{row['reg_no']} checked out; {receipt_no}; "
                    f"{amount} KSh; {payment_method}",
                    now,
                ),
            )

            return {
                "receipt_no": receipt_no,
                "reg_no": row["reg_no"],
                "owner": row["owner_name"],
                "vehicle_type": row["vehicle_type"],
                "slot": row["slot_code"],
                "arrival": row["arrival"],
                "departure": now,
                "hours": billable_hours,
                "rate": rate,
                "amount": amount,
                "payment_method": payment_method,
            }

    def search(self, term):
        term = f"%{term}%"
        with self.connect() as conn:
            return conn.execute(
                """
                SELECT
                    v.reg_no,
                    v.owner_name,
                    v.phone,
                    v.vehicle_type,
                    CASE
                        WHEN ps.status='active' THEN 'PARKED'
                        ELSE 'NOT PARKED'
                    END AS status,
                    s.slot_code,
                    ps.arrival
                FROM vehicles v
                LEFT JOIN parking_sessions ps
                    ON ps.vehicle_id = v.id AND ps.status='active'
                LEFT JOIN slots s ON s.id = ps.slot_id
                WHERE v.reg_no LIKE ?
                   OR v.owner_name LIKE ?
                   OR v.phone LIKE ?
                ORDER BY v.reg_no
                LIMIT 50
                """,
                (term, term, term),
            ).fetchall()

    def payments(self, limit=200):
        with self.connect() as conn:
            return conn.execute(
                """
                SELECT
                    p.receipt_no,
                    v.reg_no,
                    v.owner_name,
                    v.vehicle_type,
                    ps.billable_hours,
                    p.amount,
                    p.payment_method,
                    p.paid_at,
                    u.username
                FROM payments p
                JOIN parking_sessions ps ON ps.id = p.session_id
                JOIN vehicles v ON v.id = ps.vehicle_id
                JOIN users u ON u.id = p.received_by
                ORDER BY p.id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

    def logs(self, limit=200):
        with self.connect() as conn:
            return conn.execute(
                """
                SELECT
                    l.created_at,
                    COALESCE(u.username, 'SYSTEM') AS username,
                    l.action,
                    l.details
                FROM activity_logs l
                LEFT JOIN users u ON u.id = l.user_id
                ORDER BY l.id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

    def users(self):
        with self.connect() as conn:
            return conn.execute(
                """
                SELECT id, username, full_name, role, active, created_at, last_login
                FROM users ORDER BY username
                """
            ).fetchall()

    def create_user(self, username, password, full_name, role, actor_id):
        if role not in ("admin", "attendant", "customer"):
            raise ValueError("Invalid user role.")

        with self.connect() as conn:
            try:
                cursor = conn.execute(
                    """
                    INSERT INTO users
                    (username, password_hash, role, full_name, created_at)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        username,
                        hash_password(password),
                        role,
                        full_name,
                        self.now(),
                    ),
                )
            except sqlite3.IntegrityError:
                raise ValueError("Username already exists.")

            conn.execute(
                """
                INSERT INTO activity_logs(user_id, action, details, created_at)
                VALUES (?, 'USER_CREATE', ?, ?)
                """,
                (actor_id, f"Created user {username} ({role})", self.now()),
            )
            return cursor.lastrowid

    def toggle_user(self, user_id, actor_id):
        with self.connect() as conn:
            row = conn.execute(
                "SELECT username, active FROM users WHERE id=?",
                (user_id,),
            ).fetchone()

            if not row:
                raise ValueError("User not found.")

            if row["username"] == "admin":
                raise ValueError("The default admin account cannot be disabled.")

            new_status = 0 if row["active"] else 1

            conn.execute(
                "UPDATE users SET active=? WHERE id=?",
                (new_status, user_id),
            )

            conn.execute(
                """
                INSERT INTO activity_logs(user_id, action, details, created_at)
                VALUES (?, 'USER_STATUS', ?, ?)
                """,
                (
                    actor_id,
                    f"{row['username']} active={bool(new_status)}",
                    self.now(),
                ),
            )

    def update_rates(self, rates, actor_id):
        with self.connect() as conn:
            for vehicle_type, amount in rates.items():
                key = f"{vehicle_type.upper()}_RATE"
                conn.execute(
                    """
                    INSERT INTO settings(key, value) VALUES (?, ?)
                    ON CONFLICT(key) DO UPDATE SET value=excluded.value
                    """,
                    (key, str(amount)),
                )

            conn.execute(
                """
                INSERT INTO activity_logs(user_id, action, details, created_at)
                VALUES (?, 'SETTINGS', ?, ?)
                """,
                (
                    actor_id,
                    "Updated parking rates",
                    self.now(),
                ),
            )

    def backup(self):
        timestamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
        destination = BACKUP_DIR / f"parking_system_{timestamp}.db"

        with self.connect() as conn:
            conn.execute("PRAGMA wal_checkpoint(FULL)")
            backup_conn = sqlite3.connect(destination)
            conn.backup(backup_conn)
            backup_conn.close()

        return destination

    def report(self, days=30):
        with self.connect() as conn:
            return conn.execute(
                """
                SELECT
                    COUNT(*) AS transactions,
                    COALESCE(SUM(amount), 0) AS revenue,
                    COALESCE(SUM(CASE WHEN payment_method='Cash'
                                      THEN amount ELSE 0 END), 0) AS cash,
                    COALESCE(SUM(CASE WHEN payment_method='M-Pesa'
                                      THEN amount ELSE 0 END), 0) AS mpesa,
                    COALESCE(SUM(CASE WHEN payment_method='Card'
                                      THEN amount ELSE 0 END), 0) AS card
                FROM payments
                WHERE paid_at >= datetime('now', ?)
                """,
                (f"-{int(days)} days",),
            ).fetchone()
