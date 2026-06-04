from __future__ import annotations

import sqlite3
from datetime import date


def list_services(db: sqlite3.Connection) -> list[sqlite3.Row]:
    return db.execute(
        "SELECT id, name, duration_minutes, price_cents FROM services ORDER BY name"
    ).fetchall()


def list_appointments(
    db: sqlite3.Connection, target_date: str, limit: int = 100
) -> list[sqlite3.Row]:
    limit = max(1, min(limit, 500))
    return db.execute(
        """
        SELECT a.id, a.client_name, a.appointment_date, a.status,
               s.name AS service_name, s.price_cents
        FROM appointments a
        JOIN services s ON s.id = a.service_id
        WHERE a.appointment_date = ?
        ORDER BY a.created_at DESC
        LIMIT ?
        """,
        (target_date, limit),
    ).fetchall()


def status_breakdown(db: sqlite3.Connection, target_date: str) -> dict[str, int]:
    rows = db.execute(
        """
        SELECT status, COUNT(*) AS total
        FROM appointments
        WHERE appointment_date = ?
        GROUP BY status
        """,
        (target_date,),
    ).fetchall()
    return {row["status"]: row["total"] for row in rows}


def revenue_by_service(db: sqlite3.Connection, target_date: str) -> list[dict[str, object]]:
    rows = db.execute(
        """
        SELECT s.name AS service_name,
               COUNT(*) AS bookings,
               SUM(s.price_cents) AS revenue_cents
        FROM appointments a
        JOIN services s ON s.id = a.service_id
        WHERE a.appointment_date = ? AND a.status = 'completed'
        GROUP BY s.id
        ORDER BY revenue_cents DESC
        """,
        (target_date,),
    ).fetchall()
    return [
        {
            "service_name": row["service_name"],
            "bookings": row["bookings"],
            "revenue_cents": row["revenue_cents"] or 0,
        }
        for row in rows
    ]


def daily_kpis(db: sqlite3.Connection, target_date: str) -> dict[str, object]:
    breakdown = status_breakdown(db, target_date)
    completed = breakdown.get("completed", 0)
    total = sum(breakdown.values())

    revenue_row = db.execute(
        """
        SELECT COALESCE(SUM(s.price_cents), 0) AS revenue
        FROM appointments a
        JOIN services s ON s.id = a.service_id
        WHERE a.appointment_date = ? AND a.status = 'completed'
        """,
        (target_date,),
    ).fetchone()

    return {
        "date": target_date,
        "total_appointments": total,
        "completed": completed,
        "cancelled": breakdown.get("cancelled", 0),
        "no_show": breakdown.get("no_show", 0),
        "booked": breakdown.get("booked", 0),
        "revenue_cents": revenue_row["revenue"],
        "completion_rate": round(completed / total * 100, 1) if total else 0.0,
    }


def create_appointment(
    db: sqlite3.Connection, client_name: str, service_id: int, appointment_date: str
) -> int:
    cursor = db.execute(
        """
        INSERT INTO appointments (client_name, service_id, appointment_date)
        VALUES (?, ?, ?)
        """,
        (client_name, service_id, appointment_date),
    )
    db.commit()
    return int(cursor.lastrowid)


def service_exists(db: sqlite3.Connection, service_id: int) -> bool:
    row = db.execute(
        "SELECT 1 FROM services WHERE id = ?", (service_id,)
    ).fetchone()
    return row is not None
