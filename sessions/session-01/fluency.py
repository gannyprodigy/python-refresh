"""
Session 01 — Python Fluency
Production consolidation: every pattern from this session in one runnable script.
Run with: uv run python sessions/session-01/fluency.py
"""

from pathlib import Path
from datetime import datetime, timedelta, timezone
from collections import defaultdict


# --- STRING / LIST / DICT PATTERNS ---

def format_patient_summary(record: dict) -> str:
    name = record.get("name", "Unknown").strip()
    age = record.get("age", 0)
    conditions = record.get("conditions", [])
    return f"{name} (age {age}) — {', '.join(conditions) or 'no conditions'}"


# --- LAMBDA + SORTED ---

def top_lifts(prs: dict[str, float], n: int = 3) -> list[tuple[str, float]]:
    return sorted(prs.items(), key=lambda x: -x[1])[:n]


# --- COMPREHENSIONS ---

def format_sets(exercise_sets: list[dict]) -> str:
    return " | ".join(
        f"{s['weight_kg']}kg×{s['reps']}"
        for s in exercise_sets
        if s.get("weight_kg")
    )


def build_workout_context(workouts: list[dict]) -> str:
    lines = ["# Recent Workouts\n"]
    for w in workouts:
        date = w.get("start_time", "")[:10]
        lines.append(f"\n[{date}] {w.get('title', 'Workout')}")
        for ex in w.get("exercises", []):
            sets_str = format_sets(ex.get("sets", []))
            if sets_str:
                lines.append(f"  {ex['title']}: {sets_str}")
    return "\n".join(lines)


# --- BUILTINS ---

def safe_get_attr(obj: object, attr: str, default=0):
    return getattr(obj, attr, default)


def total_volume(sets: list[dict]) -> float:
    return sum(s["weight_kg"] * s["reps"] for s in sets if s.get("weight_kg"))


# --- DATETIME ---

def workouts_in_last_n_weeks(workouts: list[dict], weeks: int = 4) -> list[dict]:
    cutoff = datetime.now(timezone.utc) - timedelta(weeks=weeks)
    result = []
    for w in workouts:
        ts = w.get("start_time", "")
        if ts:
            dt = datetime.fromisoformat(ts)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            if dt >= cutoff:
                result.append(w)
    return result


# --- DEFAULTDICT ---

def group_workouts_by_date(workouts: list[dict]) -> dict[str, list]:
    by_date: dict[str, list] = defaultdict(list)
    for w in workouts:
        date = w.get("start_time", "")[:10]
        if date:
            by_date[date].append(w.get("title", "Workout"))
    return dict(by_date)


# --- RUN ---

if __name__ == "__main__":
    record = {"name": "  Riya Sharma  ", "age": 34, "conditions": ["diabetes", "hypertension"]}
    print(format_patient_summary(record))

    prs = {"bench press": 80.0, "squat": 120.0, "deadlift": 140.0, "overhead press": 60.0}
    print("Top lifts:", top_lifts(prs))

    sets = [{"weight_kg": 80, "reps": 5}, {"weight_kg": 0, "reps": 10}, {"weight_kg": 82.5, "reps": 3}]
    print("Sets:", format_sets(sets))
    print("Volume:", total_volume(sets), "kg")

    workouts = [
        {
            "start_time": "2026-06-01T09:00:00+00:00",
            "title": "Push Day",
            "exercises": [
                {"title": "Bench Press", "sets": sets},
            ]
        }
    ]
    print(build_workout_context(workouts))
    print("By date:", group_workouts_by_date(workouts))
