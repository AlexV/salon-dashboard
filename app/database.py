from __future__ import annotations

import sqlite3
from datetime import date

from flask import current_app, g


def get_db() -> sqlite3.Connection:
    if "db" not in g:
        path = current_app.config["DATABASE_PATH"]
        g.db = sqlite3.connect(path, detect_types=sqlite3.PARSE_DECLTYPES)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(exception: BaseException | None = None) -> None:
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db() -> None:
    db = get_db()
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            duration_minutes INTEGER NOT NULL CHECK (duration_minutes > 0),
            price_cents INTEGER NOT NULL CHECK (price_cents >= 0)
        );

        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT NOT NULL,
            service_id INTEGER NOT NULL,
            appointment_date TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'booked'
                CHECK (status IN ('booked', 'completed', 'cancelled', 'no_show')),
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (service_id) REFERENCES services(id)
        );

        CREATE INDEX IF NOT EXISTS idx_appt_date ON appointments(appointment_date);
        """
    )
    db.commit()


def seed_demo_data() -> None:
    db = get_db()
    existing = db.execute("SELECT COUNT(*) AS c FROM services").fetchone()
    if existing["c"] > 0:
        return

    services = [
        ("Corte de pelo", 30, 1800),
        ("Tinte completo", 90, 4500),
        ("Peinado y brushing", 45, 2500),
        ("Manicura", 40, 2000),
        ("Tratamiento capilar", 60, 3500),
    ]
    db.executemany(
        "INSERT INTO services (name, duration_minutes, price_cents) VALUES (?, ?, ?)",
        services,
    )

    today = date.today().isoformat()
    appointments = [
        ("Lucia Fernandez", 1, today, "completed"),
        ("Marcos Ruiz", 2, today, "booked"),
        ("Elena Gomez", 3, today, "completed"),
        ("Pedro Sanz", 1, today, "no_show"),
        ("Sara Diaz", 4, today, "booked"),
        ("Javier Moreno", 5, today, "completed"),
        ("Ana Torres", 2, today, "cancelled"),
        ("Diego Castro", 1, today, "completed"),
    ]
    for client, service_id, appt_date, status in appointments:
        db.execute(
            """
            INSERT INTO appointments (client_name, service_id, appointment_date, status)
            VALUES (?, ?, ?, ?)
            """,
            (client, service_id, appt_date, status),
        )
    db.commit()
