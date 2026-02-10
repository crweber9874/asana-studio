"""
routers/sequences.py — Generate & manage yoga sequences.
Intelligent sequence builder with warmup → peak → cooldown structure.
"""
from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel
from typing import Optional
import random
import json
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from database import get_connection

router = APIRouter(prefix="/api/sequences", tags=["sequences"])


# ─── Sequence Generation Logic ─────────────────────────────────────────
STYLE_TEMPLATES = {
    "morning_flow": {
        "name": "Morning Flow",
        "warmup_tags": ["foundation", "forward-bend"],
        "warmup_categories": ["Standing", "Kneeling"],
        "peak_tags": ["standing", "strengthening", "balancing"],
        "peak_categories": ["Standing", "Balance"],
        "cooldown_tags": ["restorative", "forward-bend", "supine"],
        "cooldown_categories": ["Supine", "Restorative", "Seated"],
        "max_difficulty": 3,
    },
    "power": {
        "name": "Power Vinyasa",
        "warmup_tags": ["standing", "core"],
        "warmup_categories": ["Standing", "Core"],
        "peak_tags": ["strengthening", "arm-balance", "core"],
        "peak_categories": ["Standing", "Arm Balance", "Core"],
        "cooldown_tags": ["restorative", "forward-bend"],
        "cooldown_categories": ["Supine", "Seated", "Restorative"],
        "max_difficulty": 4,
    },
    "hip_opener": {
        "name": "Deep Hip Opening",
        "warmup_tags": ["standing", "hip-opener"],
        "warmup_categories": ["Standing", "Kneeling"],
        "peak_tags": ["hip-opener"],
        "peak_categories": ["Seated", "Kneeling", "Standing"],
        "cooldown_tags": ["restorative", "hip-opener", "supine"],
        "cooldown_categories": ["Supine", "Restorative"],
        "max_difficulty": 3,
    },
    "backbend": {
        "name": "Heart Opening Backbends",
        "warmup_tags": ["chest-opener", "standing"],
        "warmup_categories": ["Standing", "Kneeling"],
        "peak_tags": ["backbend", "chest-opener"],
        "peak_categories": ["Prone", "Kneeling", "Supine"],
        "cooldown_tags": ["forward-bend", "restorative"],
        "cooldown_categories": ["Seated", "Supine", "Restorative"],
        "max_difficulty": 4,
    },
    "balance": {
        "name": "Balance & Focus",
        "warmup_tags": ["standing", "foundation"],
        "warmup_categories": ["Standing"],
        "peak_tags": ["balancing"],
        "peak_categories": ["Balance", "Standing"],
        "cooldown_tags": ["seated", "restorative"],
        "cooldown_categories": ["Seated", "Supine", "Restorative"],
        "max_difficulty": 4,
    },
    "restorative": {
        "name": "Restorative & Yin",
        "warmup_tags": ["kneeling", "restorative"],
        "warmup_categories": ["Kneeling"],
        "peak_tags": ["restorative", "hip-opener", "forward-bend"],
        "peak_categories": ["Restorative", "Supine", "Seated"],
        "cooldown_tags": ["restorative", "supine"],
        "cooldown_categories": ["Restorative", "Supine"],
        "max_difficulty": 2,
    },
    "twist": {
        "name": "Twist & Detox",
        "warmup_tags": ["standing", "forward-bend"],
        "warmup_categories": ["Standing", "Kneeling"],
        "peak_tags": ["twist"],
        "peak_categories": ["Standing", "Seated"],
        "cooldown_tags": ["restorative", "supine"],
        "cooldown_categories": ["Supine", "Restorative"],
        "max_difficulty": 3,
    },
    "full_body": {
        "name": "Full Body Flow",
        "warmup_tags": ["foundation", "forward-bend", "standing"],
        "warmup_categories": ["Standing", "Kneeling"],
        "peak_tags": ["strengthening", "hip-opener", "backbend"],
        "peak_categories": ["Standing", "Core", "Balance"],
        "cooldown_tags": ["restorative", "forward-bend", "supine"],
        "cooldown_categories": ["Seated", "Supine", "Restorative"],
        "max_difficulty": 3,
    },
    "arm_balance": {
        "name": "Arm Balance Workshop",
        "warmup_tags": ["core", "strengthening", "standing"],
        "warmup_categories": ["Standing", "Core"],
        "peak_tags": ["arm-balance", "core"],
        "peak_categories": ["Arm Balance", "Core"],
        "cooldown_tags": ["restorative", "forward-bend"],
        "cooldown_categories": ["Seated", "Supine", "Restorative"],
        "max_difficulty": 5,
    },
    "inversion": {
        "name": "Inversions Practice",
        "warmup_tags": ["core", "strengthening", "standing"],
        "warmup_categories": ["Standing", "Core"],
        "peak_tags": ["inversion", "balancing"],
        "peak_categories": ["Inversion", "Core"],
        "cooldown_tags": ["restorative", "supine"],
        "cooldown_categories": ["Supine", "Restorative"],
        "max_difficulty": 5,
    },
}


def _fetch_poses_by_criteria(conn, tags, categories, max_diff, exclude_ids, limit):
    """Fetch poses matching tags OR categories, respecting difficulty ceiling."""
    tag_placeholders = ",".join("?" for _ in tags)
    cat_placeholders = ",".join("?" for _ in categories)
    excl_placeholders = ",".join("?" for _ in exclude_ids) if exclude_ids else "0"

    sql = f"""
        SELECT DISTINCT p.id, p.english_name, p.sanskrit_name, p.category,
               p.difficulty, p.is_bilateral, p.default_hold_seconds
        FROM poses p
        LEFT JOIN pose_tags pt ON pt.pose_id = p.id
        WHERE p.difficulty <= ?
          AND p.parent_pose_id IS NULL
          AND p.id NOT IN ({excl_placeholders})
          AND (pt.tag IN ({tag_placeholders}) OR p.category IN ({cat_placeholders}))
        GROUP BY p.id
        ORDER BY RANDOM()
        LIMIT ?
    """
    params = [max_diff] + list(exclude_ids) + list(tags) + list(categories) + [limit]
    return conn.execute(sql, params).fetchall()


def generate_sequence_logic(style: str, duration_minutes: int, difficulty: int):
    """Build an intelligent sequence: warmup → peak → cooldown."""
    template = STYLE_TEMPLATES.get(style, STYLE_TEMPLATES["full_body"])
    max_diff = min(difficulty, template["max_difficulty"])

    conn = get_connection()
    used_ids = set()
    sequence_poses = []
    position = 0

    # Calculate phase sizes based on duration
    # A pose averages ~30s, so duration_min * 60 / 30 ≈ total poses
    total_poses = max(6, duration_minutes * 2)
    warmup_count = max(2, total_poses // 4)
    cooldown_count = max(2, total_poses // 4)
    peak_count = total_poses - warmup_count - cooldown_count

    # ─── Warmup ─────────────────────────────
    warmup = _fetch_poses_by_criteria(
        conn, template["warmup_tags"], template["warmup_categories"],
        max(1, max_diff - 1), used_ids, warmup_count
    )
    for pose in warmup:
        position += 1
        pose_dict = dict(pose)
        used_ids.add(pose_dict["id"])
        entry = {
            "position": position,
            "pose_id": pose_dict["id"],
            "english_name": pose_dict["english_name"],
            "sanskrit_name": pose_dict["sanskrit_name"],
            "side": "both",
            "hold_seconds": min(pose_dict["default_hold_seconds"], 30),
            "phase": "warmup",
        }
        sequence_poses.append(entry)
        # Add other side if bilateral
        if pose_dict["is_bilateral"]:
            position += 1
            entry_r = {**entry, "position": position, "side": "right"}
            entry["side"] = "left"
            sequence_poses.append(entry_r)

    # ─── Peak ───────────────────────────────
    peak = _fetch_poses_by_criteria(
        conn, template["peak_tags"], template["peak_categories"],
        max_diff, used_ids, peak_count
    )
    for pose in peak:
        position += 1
        pose_dict = dict(pose)
        used_ids.add(pose_dict["id"])
        entry = {
            "position": position,
            "pose_id": pose_dict["id"],
            "english_name": pose_dict["english_name"],
            "sanskrit_name": pose_dict["sanskrit_name"],
            "side": "both",
            "hold_seconds": pose_dict["default_hold_seconds"],
            "phase": "peak",
        }
        sequence_poses.append(entry)
        if pose_dict["is_bilateral"]:
            position += 1
            entry_r = {**entry, "position": position, "side": "right"}
            entry["side"] = "left"
            sequence_poses.append(entry_r)

    # ─── Cooldown ───────────────────────────
    cooldown = _fetch_poses_by_criteria(
        conn, template["cooldown_tags"], template["cooldown_categories"],
        2, used_ids, cooldown_count
    )
    for pose in cooldown:
        position += 1
        pose_dict = dict(pose)
        used_ids.add(pose_dict["id"])
        entry = {
            "position": position,
            "pose_id": pose_dict["id"],
            "english_name": pose_dict["english_name"],
            "sanskrit_name": pose_dict["sanskrit_name"],
            "side": "both",
            "hold_seconds": max(pose_dict["default_hold_seconds"], 45),
            "phase": "cooldown",
        }
        sequence_poses.append(entry)
        if pose_dict["is_bilateral"]:
            position += 1
            entry_r = {**entry, "position": position, "side": "right"}
            entry["side"] = "left"
            sequence_poses.append(entry_r)

    # Always end with Savasana
    savasana = conn.execute(
        "SELECT id, english_name, sanskrit_name, default_hold_seconds FROM poses WHERE slug='corpse-pose'"
    ).fetchone()
    if savasana and savasana["id"] not in used_ids:
        position += 1
        sequence_poses.append({
            "position": position,
            "pose_id": savasana["id"],
            "english_name": savasana["english_name"],
            "sanskrit_name": savasana["sanskrit_name"],
            "side": "both",
            "hold_seconds": max(120, duration_minutes * 10),
            "phase": "cooldown",
        })

    conn.close()

    total_seconds = sum(p["hold_seconds"] for p in sequence_poses)
    return {
        "style": style,
        "style_name": template["name"],
        "difficulty": max_diff,
        "duration_minutes": round(total_seconds / 60, 1),
        "total_poses": len(sequence_poses),
        "poses": sequence_poses,
    }


# ─── API Endpoints ──────────────────────────────────────────────────────

class GenerateRequest(BaseModel):
    style: str = "full_body"
    duration_minutes: int = 20
    difficulty: int = 3


@router.post("/generate")
def generate_sequence(req: GenerateRequest):
    if req.style not in STYLE_TEMPLATES:
        raise HTTPException(400, f"Unknown style. Available: {list(STYLE_TEMPLATES.keys())}")
    return generate_sequence_logic(req.style, req.duration_minutes, req.difficulty)


@router.get("/styles")
def list_styles():
    return [{"id": k, "name": v["name"]} for k, v in STYLE_TEMPLATES.items()]


class SaveSequenceRequest(BaseModel):
    name: str
    description: Optional[str] = None
    style: str
    difficulty: int = 3
    poses: list  # [{pose_id, position, side, hold_seconds}]


@router.post("")
def save_sequence(req: SaveSequenceRequest):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO sequences (name, description, style, difficulty) VALUES (?,?,?,?)",
        (req.name, req.description, req.style, req.difficulty)
    )
    seq_id = cursor.lastrowid
    for p in req.poses:
        cursor.execute(
            "INSERT INTO sequence_poses (sequence_id, pose_id, position, side, hold_seconds) VALUES (?,?,?,?,?)",
            (seq_id, p["pose_id"], p["position"], p.get("side", "both"), p.get("hold_seconds", 30))
        )
    conn.commit()
    conn.close()
    return {"id": seq_id, "message": "Sequence saved"}


@router.get("")
def list_sequences():
    conn = get_connection()
    rows = conn.execute(
        "SELECT s.*, COUNT(sp.id) as pose_count FROM sequences s LEFT JOIN sequence_poses sp ON sp.sequence_id = s.id GROUP BY s.id ORDER BY s.created_at DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@router.get("/{seq_id}")
def get_sequence(seq_id: int):
    conn = get_connection()
    seq = conn.execute("SELECT * FROM sequences WHERE id = ?", (seq_id,)).fetchone()
    if not seq:
        conn.close()
        raise HTTPException(404, "Sequence not found")

    poses = conn.execute("""
        SELECT sp.*, p.english_name, p.sanskrit_name, p.category, p.difficulty
        FROM sequence_poses sp
        JOIN poses p ON p.id = sp.pose_id
        WHERE sp.sequence_id = ?
        ORDER BY sp.position
    """, (seq_id,)).fetchall()

    conn.close()
    result = dict(seq)
    result["poses"] = [dict(p) for p in poses]
    return result


@router.get("/{seq_id}/export")
def export_sequence(seq_id: int, format: str = Query("json", pattern="^(json|text)$")):
    data = get_sequence(seq_id)
    if format == "text":
        lines = [f"# {data['name']}", f"Style: {data['style']}", f"Difficulty: {data['difficulty']}", ""]
        for p in data["poses"]:
            side_str = f" ({p['side']})" if p["side"] != "both" else ""
            lines.append(f"{p['position']}. {p['english_name']}{side_str} — {p['hold_seconds']}s")
        return {"text": "\n".join(lines)}
    return data
