"""
routers/poses.py — Search/browse yoga poses.
"""
from fastapi import APIRouter, Query
from typing import Optional
import sqlite3
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from database import get_connection

router = APIRouter(prefix="/api/poses", tags=["poses"])


@router.get("")
def list_poses(
    q: Optional[str] = Query(None, description="Search english/sanskrit name"),
    category: Optional[str] = Query(None),
    difficulty: Optional[int] = Query(None, ge=1, le=5),
    tag: Optional[str] = Query(None),
    bilateral_only: Optional[bool] = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
):
    """List poses with optional filters."""
    conn = get_connection()
    conditions = []
    params = []

    if q:
        conditions.append("(p.english_name LIKE ? OR p.sanskrit_name LIKE ?)")
        params.extend([f"%{q}%", f"%{q}%"])

    if category:
        conditions.append("p.category = ?")
        params.append(category)

    if difficulty:
        conditions.append("p.difficulty = ?")
        params.append(difficulty)

    if bilateral_only is not None:
        conditions.append("p.is_bilateral = ?")
        params.append(int(bilateral_only))

    if tag:
        conditions.append("p.id IN (SELECT pose_id FROM pose_tags WHERE tag = ?)")
        params.append(tag)

    where = "WHERE " + " AND ".join(conditions) if conditions else ""
    offset = (page - 1) * per_page

    # Get total count
    count_sql = f"SELECT COUNT(*) FROM poses p {where}"
    total = conn.execute(count_sql, params).fetchone()[0]

    # Get poses
    sql = f"""
        SELECT p.*, GROUP_CONCAT(DISTINCT pt.tag) as tags
        FROM poses p
        LEFT JOIN pose_tags pt ON pt.pose_id = p.id
        {where}
        GROUP BY p.id
        ORDER BY p.category, p.difficulty, p.english_name
        LIMIT ? OFFSET ?
    """
    rows = conn.execute(sql, params + [per_page, offset]).fetchall()

    poses = []
    for row in rows:
        pose = dict(row)
        pose["tags"] = pose["tags"].split(",") if pose["tags"] else []
        poses.append(pose)

    conn.close()
    return {
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": (total + per_page - 1) // per_page,
        "poses": poses,
    }


@router.get("/categories")
def list_categories():
    conn = get_connection()
    rows = conn.execute(
        "SELECT category, COUNT(*) as count FROM poses GROUP BY category ORDER BY category"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@router.get("/tags")
def list_tags():
    conn = get_connection()
    rows = conn.execute(
        "SELECT tag, COUNT(*) as count FROM pose_tags GROUP BY tag ORDER BY count DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@router.get("/{pose_id}")
def get_pose(pose_id: int):
    conn = get_connection()
    row = conn.execute("SELECT * FROM poses WHERE id = ?", (pose_id,)).fetchone()
    if not row:
        conn.close()
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Pose not found")

    pose = dict(row)

    # Get tags
    tags = conn.execute(
        "SELECT tag FROM pose_tags WHERE pose_id = ?", (pose_id,)
    ).fetchall()
    pose["tags"] = [t["tag"] for t in tags]

    # Get variations (children)
    variations = conn.execute(
        "SELECT id, english_name, sanskrit_name, slug, difficulty FROM poses WHERE parent_pose_id = ?",
        (pose_id,)
    ).fetchall()
    pose["variations"] = [dict(v) for v in variations]

    # Get parent if exists
    if pose.get("parent_pose_id"):
        parent = conn.execute(
            "SELECT id, english_name, sanskrit_name FROM poses WHERE id = ?",
            (pose["parent_pose_id"],)
        ).fetchone()
        pose["parent"] = dict(parent) if parent else None

    conn.close()
    return pose
