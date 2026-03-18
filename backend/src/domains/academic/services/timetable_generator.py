"""Timetable generator using heuristic backtracking with class-balance scoring."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time, timedelta
from typing import Any, Dict, Iterable, List, Tuple


@dataclass(frozen=True)
class SlotKey:
    day: int
    period: int


@dataclass(frozen=True)
class TimeSlot:
    day: int
    period: int
    start_time: time
    end_time: time


def _parse_hhmm(value: str) -> time:
    return datetime.strptime(value, "%H:%M").time()


def _build_time_slots(time_grid: dict) -> tuple[list[TimeSlot], dict[SlotKey, TimeSlot]]:
    days_per_week = int(time_grid.get("days_per_week", 5))
    periods_per_day = int(time_grid.get("periods_per_day", 7))
    period_minutes = int(time_grid.get("period_minutes", 45))
    start_time = _parse_hhmm(time_grid.get("day_start_time", "09:00"))

    breaks = time_grid.get("breaks") or []
    break_keys = {SlotKey(int(b["day"]), int(b["period"])) for b in breaks if "day" in b and "period" in b}

    slots: list[TimeSlot] = []
    slot_map: dict[SlotKey, TimeSlot] = {}
    start_dt = datetime.combine(datetime.today().date(), start_time)
    for day in range(days_per_week):
        for period in range(periods_per_day):
            key = SlotKey(day, period)
            if key in break_keys:
                continue
            slot_start = start_dt + timedelta(minutes=period * period_minutes)
            slot_end = slot_start + timedelta(minutes=period_minutes)
            slot = TimeSlot(day=day, period=period, start_time=slot_start.time(), end_time=slot_end.time())
            slots.append(slot)
            slot_map[key] = slot
    return slots, slot_map


def _teacher_availability(teacher: dict, slot_keys: Iterable[SlotKey], time_grid: dict) -> set[SlotKey]:
    days_per_week = int(time_grid.get("days_per_week", 5))
    periods_per_day = int(time_grid.get("periods_per_day", 7))

    availability = teacher.get("availability") or {}
    days = availability.get("days") or list(range(days_per_week))
    start_period = int(availability.get("start_period", 0))
    end_period = int(availability.get("end_period", periods_per_day - 1))
    blocked_slots = {
        SlotKey(int(b["day"]), int(b["period"]))
        for b in availability.get("blocked_slots", [])
        if "day" in b and "period" in b
    }

    allowed = set()
    for day in days:
        for period in range(start_period, end_period + 1):
            key = SlotKey(int(day), int(period))
            if key in blocked_slots:
                continue
            if key in slot_keys:
                allowed.add(key)
    return allowed


def generate_timetable(payload: dict) -> dict:
    """Generate timetable based on constraints. Returns schedule or conflict report."""
    time_grid = payload.get("time_grid") or {}
    teachers = payload.get("teachers") or []
    requirements = payload.get("requirements") or []
    fixed_lessons = payload.get("fixed_lessons") or []
    rules = payload.get("rules") or {}
    max_nodes_value = payload.get("max_nodes")
    max_nodes = int(max_nodes_value) if max_nodes_value is not None else 200000

    slots, slot_map = _build_time_slots(time_grid)
    slot_keys = set(slot_map.keys())

    teacher_map = {t["id"]: t for t in teachers}
    teacher_ids = list(teacher_map.keys())
    teacher_availability = {
        tid: _teacher_availability(teacher_map[tid], slot_keys, time_grid)
        for tid in teacher_ids
    }

    class_schedule: dict[str, dict[SlotKey, dict]] = {}
    teacher_schedule: dict[str, dict[SlotKey, dict]] = {tid: {} for tid in teacher_ids}
    teacher_weekly_counts = {tid: 0 for tid in teacher_ids}
    teacher_daily_counts: dict[tuple[str, int], int] = {}
    class_subject_day_counts: dict[tuple[str, str, int], int] = {}
    fixed_assignments: list[dict] = []

    conflicts: dict[str, list[dict]] = {
        "insufficient_slots": [],
        "fixed_conflicts": [],
        "capacity": [],
    }

    # Pre-check requirement feasibility
    req_map: dict[tuple[str, str], dict] = {}
    required_totals: dict[tuple[str, str], int] = {}
    for req in requirements:
        class_id = req["class_id"]
        subject_id = req["subject_id"]
        key = (class_id, subject_id)
        req_map[key] = req
        required_totals[key] = int(req.get("required_periods_per_week", 0))
        allowed_teachers = req.get("allowed_teachers") or teacher_ids
        eligible_slots = set()
        for tid in allowed_teachers:
            eligible_slots |= teacher_availability.get(tid, set())
        if len(eligible_slots) < int(req.get("required_periods_per_week", 0)):
            conflicts["insufficient_slots"].append({
                "class_id": class_id,
                "subject_id": subject_id,
                "required_periods": req.get("required_periods_per_week", 0),
                "eligible_slots": len(eligible_slots),
            })

    # Fixed lessons placement
    for fixed in fixed_lessons:
        class_id = fixed["class_id"]
        subject_id = fixed["subject_id"]
        teacher_id = fixed["teacher_id"]
        day = int(fixed["day"])
        period = int(fixed["period"])
        slot_key = SlotKey(day, period)
        if slot_key not in slot_keys:
            conflicts["fixed_conflicts"].append({"detail": "slot_not_available", "lesson": fixed})
            continue
        if slot_key in class_schedule.get(class_id, {}):
            conflicts["fixed_conflicts"].append({"detail": "class_collision", "lesson": fixed})
            continue
        if slot_key in teacher_schedule.get(teacher_id, {}):
            conflicts["fixed_conflicts"].append({"detail": "teacher_collision", "lesson": fixed})
            continue
        if teacher_id not in teacher_availability or slot_key not in teacher_availability[teacher_id]:
            conflicts["fixed_conflicts"].append({"detail": "teacher_unavailable", "lesson": fixed})
            continue
        max_week = int(teacher_map.get(teacher_id, {}).get("max_periods_per_week", 999))
        max_day = int(teacher_map.get(teacher_id, {}).get("max_periods_per_day", 999))
        if teacher_weekly_counts.get(teacher_id, 0) + 1 > max_week:
            conflicts["fixed_conflicts"].append({"detail": "teacher_weekly_cap", "lesson": fixed})
            continue
        if teacher_daily_counts.get((teacher_id, day), 0) + 1 > max_day:
            conflicts["fixed_conflicts"].append({"detail": "teacher_daily_cap", "lesson": fixed})
            continue

        if rules.get("no_back_to_back_classes", True):
            prev_slot = SlotKey(day, period - 1)
            next_slot = SlotKey(day, period + 1)
            for neighbor in (prev_slot, next_slot):
                neighbor_assignment = class_schedule.get(class_id, {}).get(neighbor)
                if neighbor_assignment and neighbor_assignment["subject_id"] == subject_id:
                    conflicts["fixed_conflicts"].append({"detail": "class_back_to_back", "lesson": fixed})
                    break
        if rules.get("no_back_to_back_teachers", True):
            prev_slot = SlotKey(day, period - 1)
            next_slot = SlotKey(day, period + 1)
            for neighbor in (prev_slot, next_slot):
                if neighbor in teacher_schedule.get(teacher_id, {}):
                    conflicts["fixed_conflicts"].append({"detail": "teacher_back_to_back", "lesson": fixed})
                    break

        assignment = {
            "class_id": class_id,
            "subject_id": subject_id,
            "teacher_id": teacher_id,
            "day": day,
            "period": period,
        }
        class_schedule.setdefault(class_id, {})[slot_key] = assignment
        teacher_schedule.setdefault(teacher_id, {})[slot_key] = assignment
        teacher_weekly_counts[teacher_id] = teacher_weekly_counts.get(teacher_id, 0) + 1
        teacher_daily_counts[(teacher_id, day)] = teacher_daily_counts.get((teacher_id, day), 0) + 1
        class_subject_day_counts[(class_id, subject_id, day)] = class_subject_day_counts.get((class_id, subject_id, day), 0) + 1
        fixed_assignments.append(assignment)

        if (class_id, subject_id) in req_map:
            remaining = int(req_map[(class_id, subject_id)]["required_periods_per_week"])
            if remaining <= 0:
                conflicts["fixed_conflicts"].append({"detail": "fixed_exceeds_requirement", "lesson": fixed})
            else:
                req_map[(class_id, subject_id)]["required_periods_per_week"] = remaining - 1

    if any(conflicts.values()):
        return {"status": "infeasible", "conflicts": conflicts}

    # Build task list
    tasks: list[tuple[str, str]] = []
    candidates_by_req: dict[tuple[str, str], list[tuple[str, SlotKey]]] = {}
    for req in requirements:
        class_id = req["class_id"]
        subject_id = req["subject_id"]
        remaining = int(req.get("required_periods_per_week", 0))
        if remaining <= 0:
            continue
        key = (class_id, subject_id)
        allowed_teachers = req.get("allowed_teachers") or teacher_ids
        combos: list[tuple[str, SlotKey]] = []
        for tid in allowed_teachers:
            for slot_key in teacher_availability.get(tid, set()):
                combos.append((tid, slot_key))
        candidates_by_req[key] = combos
        tasks.extend([key] * remaining)

    tasks.sort(key=lambda k: len(candidates_by_req.get(k, [])))

    nodes = 0
    assignments: list[dict] = []

    def can_place(class_id: str, subject_id: str, teacher_id: str, slot_key: SlotKey) -> bool:
        if slot_key not in slot_keys:
            return False
        if slot_key in class_schedule.get(class_id, {}):
            return False
        if slot_key in teacher_schedule.get(teacher_id, {}):
            return False
        if slot_key not in teacher_availability.get(teacher_id, set()):
            return False

        if rules.get("no_back_to_back_classes", True):
            for neighbor in (SlotKey(slot_key.day, slot_key.period - 1), SlotKey(slot_key.day, slot_key.period + 1)):
                neighbor_assignment = class_schedule.get(class_id, {}).get(neighbor)
                if neighbor_assignment and neighbor_assignment["subject_id"] == subject_id:
                    return False
        if rules.get("no_back_to_back_teachers", True):
            for neighbor in (SlotKey(slot_key.day, slot_key.period - 1), SlotKey(slot_key.day, slot_key.period + 1)):
                if neighbor in teacher_schedule.get(teacher_id, {}):
                    return False

        max_week = int(teacher_map[teacher_id].get("max_periods_per_week", 999))
        max_day = int(teacher_map[teacher_id].get("max_periods_per_day", 999))
        if teacher_weekly_counts.get(teacher_id, 0) + 1 > max_week:
            return False
        if teacher_daily_counts.get((teacher_id, slot_key.day), 0) + 1 > max_day:
            return False
        return True

    def place(class_id: str, subject_id: str, teacher_id: str, slot_key: SlotKey):
        assignment = {
            "class_id": class_id,
            "subject_id": subject_id,
            "teacher_id": teacher_id,
            "day": slot_key.day,
            "period": slot_key.period,
        }
        class_schedule.setdefault(class_id, {})[slot_key] = assignment
        teacher_schedule.setdefault(teacher_id, {})[slot_key] = assignment
        teacher_weekly_counts[teacher_id] = teacher_weekly_counts.get(teacher_id, 0) + 1
        teacher_daily_counts[(teacher_id, slot_key.day)] = teacher_daily_counts.get((teacher_id, slot_key.day), 0) + 1
        class_subject_day_counts[(class_id, subject_id, slot_key.day)] = class_subject_day_counts.get(
            (class_id, subject_id, slot_key.day), 0
        ) + 1
        assignments.append(assignment)

    def unplace(class_id: str, subject_id: str, teacher_id: str, slot_key: SlotKey):
        class_schedule.get(class_id, {}).pop(slot_key, None)
        teacher_schedule.get(teacher_id, {}).pop(slot_key, None)
        teacher_weekly_counts[teacher_id] = max(0, teacher_weekly_counts.get(teacher_id, 0) - 1)
        teacher_daily_counts[(teacher_id, slot_key.day)] = max(0, teacher_daily_counts.get((teacher_id, slot_key.day), 0) - 1)
        class_subject_day_counts[(class_id, subject_id, slot_key.day)] = max(
            0, class_subject_day_counts.get((class_id, subject_id, slot_key.day), 0) - 1
        )
        assignments.pop()

    def balance_delta(class_id: str, subject_id: str, day: int) -> float:
        total_required = required_totals.get((class_id, subject_id), 0)
        ideal = float(total_required) / max(1, int(time_grid.get("days_per_week", 5)))
        current = class_subject_day_counts.get((class_id, subject_id, day), 0)
        return abs((current + 1) - ideal) - abs(current - ideal)

    def backtrack(index: int) -> bool:
        nonlocal nodes
        if index >= len(tasks):
            return True
        if nodes > max_nodes:
            return False
        key = tasks[index]
        class_id, subject_id = key
        candidates = candidates_by_req.get(key, [])
        candidates.sort(key=lambda c: (
            balance_delta(class_id, subject_id, c[1].day),
            teacher_weekly_counts.get(c[0], 0),
            c[1].day,
            c[1].period,
        ))
        for teacher_id, slot_key in candidates:
            nodes += 1
            if not can_place(class_id, subject_id, teacher_id, slot_key):
                continue
            place(class_id, subject_id, teacher_id, slot_key)
            if backtrack(index + 1):
                return True
            unplace(class_id, subject_id, teacher_id, slot_key)
        return False

    solved = backtrack(0)
    if not solved:
        return {
            "status": "infeasible",
            "conflicts": {
                "search_exhausted": True,
                "explored_nodes": nodes,
            },
        }

    # Build schedule output with times
    output_assignments = []
    for assignment in fixed_assignments + assignments:
        slot_key = SlotKey(assignment["day"], assignment["period"])
        slot = slot_map.get(slot_key)
        if slot:
            assignment = {**assignment}
            assignment["start_time"] = slot.start_time.strftime("%H:%M")
            assignment["end_time"] = slot.end_time.strftime("%H:%M")
        output_assignments.append(assignment)

    class_balance_score = 0.0
    for (class_id, subject_id, day), count in class_subject_day_counts.items():
        total_required = required_totals.get((class_id, subject_id), 0)
        ideal = float(total_required) / max(1, int(time_grid.get("days_per_week", 5)))
        class_balance_score += abs(count - ideal)

    teacher_loads = {}
    for tid in teacher_ids:
        daily = {str(day): teacher_daily_counts.get((tid, day), 0) for day in range(int(time_grid.get("days_per_week", 5)))}
        teacher_loads[tid] = {
            "weekly": teacher_weekly_counts.get(tid, 0),
            "daily": daily,
        }

    return {
        "status": "success",
        "assignments": output_assignments,
        "class_balance_score": class_balance_score,
        "teacher_loads": teacher_loads,
    }
