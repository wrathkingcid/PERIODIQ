import pytest
from app.solver.infeasibility_explainer import InfeasibilityExplainer


def test_infeasibility_explainer():
    # Setup an impossible demand: Division demands 50 hours in a 35-hour week (5 days * 7 periods)
    divisions = [{"id": 1, "class_group_id": 1, "name": "Section Overloaded"}]
    subjects = [
        {"id": 101, "class_group_id": 1, "weekly_hours": 30, "is_lab": False},
        {"id": 102, "class_group_id": 1, "weekly_hours": 25, "is_lab": False}
    ]
    teachers = [
        {"id": 1, "name": "Prof Overworked", "max_hours_per_week": 15, "competent_subject_ids": [101, 102]}
    ]
    rooms = [{"id": 1, "name": "Room 101", "capacity": 50, "room_type": "lecture"}]

    diagnostic = InfeasibilityExplainer.diagnose(
        days_count=5,
        periods_per_day=7,
        class_groups=[],
        divisions=divisions,
        subjects=subjects,
        teachers=teachers,
        rooms=rooms
    )

    assert diagnostic["status"] == "INFEASIBLE"
    assert diagnostic["diagnostic_count"] >= 2
    categories = [d["category"] for d in diagnostic["diagnostics"]]
    assert "TIME_SLOT_OVERFLOW" in categories
    assert "TEACHER_MAX_HOURS_EXCEEDED" in categories
    assert len(diagnostic["recommendations"]) > 0
    print(f"\n[SUCCESS] Infeasibility detected accurately with {len(diagnostic['recommendations'])} actionable recommendations!")


if __name__ == "__main__":
    test_infeasibility_explainer()
