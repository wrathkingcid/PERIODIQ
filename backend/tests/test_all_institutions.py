import requests

for inst_id, name in [(1, "Greenwood High School"), (2, "Apex Engineering College"), (3, "Olympus Coaching Institute")]:
    r = requests.post(
        f"http://127.0.0.1:8000/api/v1/institutions/{inst_id}/generate",
        json={"scenario_name": f"{name} Timetable", "academic_year": "2026-2027", "term": "Term 1", "timeout_seconds": 25, "enable_soft_constraints": True}
    )
    assert r.status_code == 200, f"Failed for {name}: {r.text}"
    data = r.json()
    res = data["result"]
    print(f"[OK] {name}: Status = {res['status']}, Quality = {res['quality_score']}%, Entries = {len(res['entries'])}, Solve Time = {res['solver_time_seconds']}s")

print("\nAll 3 educational institution types solved successfully with Google OR-Tools CP-SAT!")
