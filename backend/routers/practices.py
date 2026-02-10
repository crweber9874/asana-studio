"""
routers/practices.py — Custom practice builder CRUD.
Users can create, update, and delete their own practice sequences.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from database import get_connection

router = APIRouter(prefix="/api/practices", tags=["practices"])


class PracticeCreate(BaseModel):
    name: str
    poses: list = []  # [{pose_id, position, side, hold_seconds}]


class PracticeUpdate(BaseModel):
    name: Optional[str] = None
    poses: Optional[list] = None


@router.post("")
def create_practice(req: PracticeCreate):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO practices (name) VALUES (?)", (req.name,))
    practice_id = cursor.lastrowid

    for p in req.poses:
        cursor.execute(
            "INSERT INTO practice_poses (practice_id, pose_id, position, side, hold_seconds) VALUES (?,?,?,?,?)",
            (practice_id, p["pose_id"], p["position"],
             p.get("side", "both"), p.get("hold_seconds", 30))
        )

    conn.commit()
    conn.close()
    return {"id": practice_id, "message": "Practice created"}


@router.get("")
def list_practices():
    conn = get_connection()
    rows = conn.execute("""
        SELECT p.*, COUNT(pp.id) as pose_count,
               SUM(pp.hold_seconds) as total_seconds
        FROM practices p
        LEFT JOIN practice_poses pp ON pp.practice_id = p.id
        GROUP BY p.id
        ORDER BY p.created_at DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@router.get("/{practice_id}")
def get_practice(practice_id: int):
    conn = get_connection()
    practice = conn.execute(
        "SELECT * FROM practices WHERE id = ?", (practice_id,)
    ).fetchone()
    if not practice:
        conn.close()
        raise HTTPException(404, "Practice not found")

    poses = conn.execute("""
        SELECT pp.*, p.english_name, p.sanskrit_name, p.category,
               p.difficulty, p.is_bilateral
        FROM practice_poses pp
        JOIN poses p ON p.id = pp.pose_id
        WHERE pp.practice_id = ?
        ORDER BY pp.position
    """, (practice_id,)).fetchall()

    conn.close()
    result = dict(practice)
    result["poses"] = [dict(p) for p in poses]
    return result


@router.put("/{practice_id}")
def update_practice(practice_id: int, req: PracticeUpdate):
    conn = get_connection()
    practice = conn.execute(
        "SELECT * FROM practices WHERE id = ?", (practice_id,)
    ).fetchone()
    if not practice:
        conn.close()
        raise HTTPException(404, "Practice not found")

    if req.name:
        conn.execute(
            "UPDATE practices SET name = ? WHERE id = ?",
            (req.name, practice_id)
        )

    if req.poses is not None:
        conn.execute("DELETE FROM practice_poses WHERE practice_id = ?", (practice_id,))
        for p in req.poses:
            conn.execute(
                "INSERT INTO practice_poses (practice_id, pose_id, position, side, hold_seconds) VALUES (?,?,?,?,?)",
                (practice_id, p["pose_id"], p["position"],
                 p.get("side", "both"), p.get("hold_seconds", 30))
            )

    conn.commit()
    conn.close()
    return {"message": "Practice updated"}


@router.delete("/{practice_id}")
def delete_practice(practice_id: int):
    conn = get_connection()
    practice = conn.execute(
        "SELECT * FROM practices WHERE id = ?", (practice_id,)
    ).fetchone()
    if not practice:
        conn.close()
        raise HTTPException(404, "Practice not found")

    conn.execute("DELETE FROM practice_poses WHERE practice_id = ?", (practice_id,))
    conn.execute("DELETE FROM practices WHERE id = ?", (practice_id,))
    conn.commit()
    conn.close()
    return {"message": "Practice deleted"}
