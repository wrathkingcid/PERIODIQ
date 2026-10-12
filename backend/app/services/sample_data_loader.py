from typing import Dict, Any
from sqlalchemy.orm import Session
from app.models.institution import Institution
from app.models.academic import Department, ClassGroup, Division, Batch
from app.models.curriculum import Subject
from app.models.teacher import Teacher
from app.models.resource import Room
from app.models.timetable import TimetableScenario


class SampleDataLoader:
    """
    Seeds realistic institutional sample data:
    1. High School (Greenwood High)
    2. Engineering College (Apex Institute of Technology)
    3. Coaching Institute (Olympus IIT-JEE & NEET Academy)
    """

    @classmethod
    def load_all_samples(cls, db: Session) -> Dict[str, int]:
        school_id = cls.load_school(db)
        college_id = cls.load_engineering_college(db)
        coaching_id = cls.load_coaching_institute(db)
        return {
            "school_id": school_id,
            "college_id": college_id,
            "coaching_id": coaching_id
        }

    @classmethod
    def load_school(cls, db: Session) -> int:
        existing = db.query(Institution).filter(Institution.code == "GREENWOOD-HS").first()
        if existing:
            return existing.id

        inst = Institution(
            name="Greenwood International High School",
            type="SCHOOL",
            code="GREENWOOD-HS",
            description="Prestigious secondary school with STEM labs, balanced daily curriculum, and extracurricular periods.",
            contact_email="admin@greenwood.edu",
            working_days=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
            periods_per_day=7,
            period_duration_minutes=45,
            day_start_time="08:15",
            breaks=[
                {"name": "Morning Recess", "after_period": 2, "duration_minutes": 15},
                {"name": "Lunch Break", "after_period": 4, "duration_minutes": 40}
            ],
            shifts=[
                {"name": "Regular Day Shift", "start_time": "08:15", "end_time": "14:45", "periods": 7}
            ]
        )
        db.add(inst)
        db.flush()

        # Departments
        dept_sci = Department(institution_id=inst.id, name="Science & Technology", code="SCI")
        dept_math = Department(institution_id=inst.id, name="Mathematics", code="MATH")
        dept_hum = Department(institution_id=inst.id, name="Humanities & Languages", code="HUM")
        db.add_all([dept_sci, dept_math, dept_hum])
        db.flush()

        # Class Groups & Divisions
        cg_9 = ClassGroup(institution_id=inst.id, department_id=dept_hum.id, name="Grade 9", code="G9", year=9)
        cg_10 = ClassGroup(institution_id=inst.id, department_id=dept_hum.id, name="Grade 10", code="G10", year=10)
        db.add_all([cg_9, cg_10])
        db.flush()

        div_9a = Division(institution_id=inst.id, class_group_id=cg_9.id, name="Section 9-A", student_count=35)
        div_9b = Division(institution_id=inst.id, class_group_id=cg_9.id, name="Section 9-B", student_count=35)
        div_10a = Division(institution_id=inst.id, class_group_id=cg_10.id, name="Section 10-A", student_count=38)
        div_10b = Division(institution_id=inst.id, class_group_id=cg_10.id, name="Section 10-B", student_count=38)
        db.add_all([div_9a, div_9b, div_10a, div_10b])
        db.flush()

        # Rooms
        r_101 = Room(institution_id=inst.id, name="Classroom 101", code="CR-101", room_type="lecture", capacity=40, building="North Block")
        r_102 = Room(institution_id=inst.id, name="Classroom 102", code="CR-102", room_type="lecture", capacity=40, building="North Block")
        r_103 = Room(institution_id=inst.id, name="Classroom 103", code="CR-103", room_type="lecture", capacity=40, building="North Block")
        r_104 = Room(institution_id=inst.id, name="Classroom 104", code="CR-104", room_type="lecture", capacity=40, building="North Block")
        r_scilab = Room(institution_id=inst.id, name="Integrated Science Lab", code="SCI-LAB", room_type="lab_science", capacity=45, building="North Block")
        r_complab = Room(institution_id=inst.id, name="Junior Computer Lab", code="COMP-LAB", room_type="lab_computer", capacity=40, building="North Block")
        db.add_all([r_101, r_102, r_103, r_104, r_scilab, r_complab])
        db.flush()

        # Subjects
        s_m9 = Subject(institution_id=inst.id, class_group_id=cg_9.id, department_id=dept_math.id, name="Grade 9 Mathematics", code="MTH-901", weekly_hours=5, consecutive_periods=1, is_lab=False, color_code="#3b82f6")
        s_s9 = Subject(institution_id=inst.id, class_group_id=cg_9.id, department_id=dept_sci.id, name="Grade 9 General Science", code="SCI-901", weekly_hours=4, consecutive_periods=1, is_lab=False, color_code="#10b981")
        s_slab9 = Subject(institution_id=inst.id, class_group_id=cg_9.id, department_id=dept_sci.id, name="Grade 9 Science Lab", code="SCI-902L", weekly_hours=2, consecutive_periods=2, is_lab=True, preferred_room_type="lab_science", color_code="#059669")
        s_e9 = Subject(institution_id=inst.id, class_group_id=cg_9.id, department_id=dept_hum.id, name="Grade 9 English Literature", code="ENG-901", weekly_hours=4, consecutive_periods=1, is_lab=False, color_code="#f59e0b")
        s_cs9 = Subject(institution_id=inst.id, class_group_id=cg_9.id, department_id=dept_sci.id, name="Grade 9 Computer Applications", code="CS-901", weekly_hours=3, consecutive_periods=2, is_lab=True, preferred_room_type="lab_computer", color_code="#8b5cf6")
        s_ss9 = Subject(institution_id=inst.id, class_group_id=cg_9.id, department_id=dept_hum.id, name="Grade 9 Social Studies", code="SOC-901", weekly_hours=4, consecutive_periods=1, is_lab=False, color_code="#ec4899")

        # Grade 10 Subjects
        s_m10 = Subject(institution_id=inst.id, class_group_id=cg_10.id, department_id=dept_math.id, name="Grade 10 Mathematics", code="MTH-101", weekly_hours=5, consecutive_periods=1, is_lab=False, color_code="#3b82f6")
        s_s10 = Subject(institution_id=inst.id, class_group_id=cg_10.id, department_id=dept_sci.id, name="Grade 10 Physical Science", code="SCI-101", weekly_hours=4, consecutive_periods=1, is_lab=False, color_code="#10b981")
        s_slab10 = Subject(institution_id=inst.id, class_group_id=cg_10.id, department_id=dept_sci.id, name="Grade 10 Science Practical", code="SCI-102L", weekly_hours=2, consecutive_periods=2, is_lab=True, preferred_room_type="lab_science", color_code="#059669")
        s_e10 = Subject(institution_id=inst.id, class_group_id=cg_10.id, department_id=dept_hum.id, name="Grade 10 English Language", code="ENG-101", weekly_hours=4, consecutive_periods=1, is_lab=False, color_code="#f59e0b")
        s_cs10 = Subject(institution_id=inst.id, class_group_id=cg_10.id, department_id=dept_sci.id, name="Grade 10 Coding & AI", code="CS-101", weekly_hours=3, consecutive_periods=2, is_lab=True, preferred_room_type="lab_computer", color_code="#8b5cf6")
        s_ss10 = Subject(institution_id=inst.id, class_group_id=cg_10.id, department_id=dept_hum.id, name="Grade 10 World History", code="SOC-101", weekly_hours=4, consecutive_periods=1, is_lab=False, color_code="#ec4899")

        db.add_all([s_m9, s_s9, s_slab9, s_e9, s_cs9, s_ss9, s_m10, s_s10, s_slab10, s_e10, s_cs10, s_ss10])
        db.flush()

        # Teachers
        t1 = Teacher(institution_id=inst.id, department_id=dept_math.id, name="Robert Vance (Math Head)", code="RV-MTH", designation="Senior Teacher", max_hours_per_day=4, max_hours_per_week=20, competent_subject_ids=[s_m9.id, s_m10.id], preferred_slots=[[0, 0], [1, 0], [2, 0]])
        t2 = Teacher(institution_id=inst.id, department_id=dept_math.id, name="Sarah Jenkins (Math)", code="SJ-MTH", designation="Teacher", max_hours_per_day=4, max_hours_per_week=18, competent_subject_ids=[s_m9.id, s_m10.id])
        t3 = Teacher(institution_id=inst.id, department_id=dept_sci.id, name="Dr. Marcus Brody (Science)", code="MB-SCI", designation="Head of Science", max_hours_per_day=4, max_hours_per_week=20, competent_subject_ids=[s_s9.id, s_slab9.id, s_s10.id, s_slab10.id])
        t4 = Teacher(institution_id=inst.id, department_id=dept_sci.id, name="Elena Rostova (Science)", code="ER-SCI", designation="Teacher", max_hours_per_day=4, max_hours_per_week=18, competent_subject_ids=[s_s9.id, s_slab9.id, s_s10.id, s_slab10.id])
        t5 = Teacher(institution_id=inst.id, department_id=dept_hum.id, name="Claire Redfield (English)", code="CR-ENG", designation="Senior Teacher", max_hours_per_day=4, max_hours_per_week=18, competent_subject_ids=[s_e9.id, s_e10.id])
        t6 = Teacher(institution_id=inst.id, department_id=dept_hum.id, name="David Miller (Social Studies)", code="DM-SOC", designation="Teacher", max_hours_per_day=4, max_hours_per_week=18, competent_subject_ids=[s_ss9.id, s_ss10.id])
        t7 = Teacher(institution_id=inst.id, department_id=dept_sci.id, name="Arthur Clarke (Computers)", code="AC-CS", designation="Teacher", max_hours_per_day=4, max_hours_per_week=18, competent_subject_ids=[s_cs9.id, s_cs10.id], blackout_slots=[[2, 5], [2, 6]])
        db.add_all([t1, t2, t3, t4, t5, t6, t7])
        db.commit()
        return inst.id

    @classmethod
    def load_engineering_college(cls, db: Session) -> int:
        existing = db.query(Institution).filter(Institution.code == "APEX-TECH").first()
        if existing:
            return existing.id

        inst = Institution(
            name="Apex Institute of Technology & Engineering",
            type="COLLEGE",
            code="APEX-TECH",
            description="Leading engineering university with lecture-tutorial-practical credit framework, specialized laboratories, and elective tracks.",
            contact_email="dean@apextech.edu",
            working_days=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
            periods_per_day=7,
            period_duration_minutes=50,
            day_start_time="08:45",
            breaks=[
                {"name": "Mid-Morning Break", "after_period": 2, "duration_minutes": 15},
                {"name": "Lunch Break", "after_period": 4, "duration_minutes": 50}
            ],
            shifts=[
                {"name": "University Main Shift", "start_time": "08:45", "end_time": "15:45", "periods": 7}
            ]
        )
        db.add(inst)
        db.flush()

        # Departments
        dept_cse = Department(institution_id=inst.id, name="Computer Science & Engineering", code="CSE")
        dept_ece = Department(institution_id=inst.id, name="Electronics & Communication", code="ECE")
        dept_math = Department(institution_id=inst.id, name="Applied Mathematics", code="MATH")
        db.add_all([dept_cse, dept_ece, dept_math])
        db.flush()

        # Class Groups & Divisions
        cg_cse3 = ClassGroup(institution_id=inst.id, department_id=dept_cse.id, name="B.Tech CSE - 3rd Semester", code="CSE-SEM3", year=2, semester=3)
        cg_cse5 = ClassGroup(institution_id=inst.id, department_id=dept_cse.id, name="B.Tech CSE - 5th Semester", code="CSE-SEM5", year=3, semester=5)
        db.add_all([cg_cse3, cg_cse5])
        db.flush()

        div_cse3a = Division(institution_id=inst.id, class_group_id=cg_cse3.id, name="CSE-3A", student_count=60)
        div_cse3b = Division(institution_id=inst.id, class_group_id=cg_cse3.id, name="CSE-3B", student_count=58)
        div_cse5a = Division(institution_id=inst.id, class_group_id=cg_cse5.id, name="CSE-5A", student_count=55)
        db.add_all([div_cse3a, div_cse3b, div_cse5a])
        db.flush()

        # Rooms
        lh_201 = Room(institution_id=inst.id, name="Lecture Hall 201", code="LH-201", room_type="lecture", capacity=75, building="Turing Block")
        lh_202 = Room(institution_id=inst.id, name="Lecture Hall 202", code="LH-202", room_type="lecture", capacity=75, building="Turing Block")
        lh_203 = Room(institution_id=inst.id, name="Lecture Hall 203", code="LH-203", room_type="lecture", capacity=75, building="Turing Block")
        lh_204 = Room(institution_id=inst.id, name="Lecture Hall 204", code="LH-204", room_type="lecture", capacity=75, building="Turing Block")
        lab_ds = Room(institution_id=inst.id, name="Data Structures & Algorithms Lab", code="DS-LAB", room_type="lab_computer", capacity=65, building="Turing Block")
        lab_os = Room(institution_id=inst.id, name="Systems & Cloud Computing Lab", code="SYS-LAB", room_type="lab_computer", capacity=65, building="Turing Block")
        db.add_all([lh_201, lh_202, lh_203, lh_204, lab_ds, lab_os])
        db.flush()

        # Subjects
        s_dsa = Subject(institution_id=inst.id, class_group_id=cg_cse3.id, department_id=dept_cse.id, name="Data Structures & Algorithms", code="CS-301", weekly_hours=3, consecutive_periods=1, is_lab=False, color_code="#6366f1")
        s_dsalab = Subject(institution_id=inst.id, class_group_id=cg_cse3.id, department_id=dept_cse.id, name="DSA Practical Lab", code="CS-301L", weekly_hours=2, consecutive_periods=2, is_lab=True, preferred_room_type="lab_computer", color_code="#4f46e5")
        s_dld = Subject(institution_id=inst.id, class_group_id=cg_cse3.id, department_id=dept_ece.id, name="Digital Logic Design", code="EC-302", weekly_hours=3, consecutive_periods=1, is_lab=False, color_code="#06b6d4")
        s_dm = Subject(institution_id=inst.id, class_group_id=cg_cse3.id, department_id=dept_math.id, name="Discrete Mathematical Structures", code="MA-303", weekly_hours=4, consecutive_periods=1, is_lab=False, color_code="#f59e0b")
        s_oop = Subject(institution_id=inst.id, class_group_id=cg_cse3.id, department_id=dept_cse.id, name="Object-Oriented Programming (Java/C++)", code="CS-304", weekly_hours=3, consecutive_periods=1, is_lab=False, color_code="#10b981")

        # CSE 5th Sem Subjects
        s_os = Subject(institution_id=inst.id, class_group_id=cg_cse5.id, department_id=dept_cse.id, name="Operating Systems & Concurrency", code="CS-501", weekly_hours=3, consecutive_periods=1, is_lab=False, color_code="#ec4899")
        s_oslab = Subject(institution_id=inst.id, class_group_id=cg_cse5.id, department_id=dept_cse.id, name="Operating Systems Kernel Lab", code="CS-501L", weekly_hours=2, consecutive_periods=2, is_lab=True, preferred_room_type="lab_computer", color_code="#db2777")
        s_dbms = Subject(institution_id=inst.id, class_group_id=cg_cse5.id, department_id=dept_cse.id, name="Database Management Systems", code="CS-502", weekly_hours=3, consecutive_periods=1, is_lab=False, color_code="#8b5cf6")
        s_cn = Subject(institution_id=inst.id, class_group_id=cg_cse5.id, department_id=dept_cse.id, name="Computer Networks & Protocols", code="CS-503", weekly_hours=3, consecutive_periods=1, is_lab=False, color_code="#0ea5e9")
        s_ai = Subject(institution_id=inst.id, class_group_id=cg_cse5.id, department_id=dept_cse.id, name="Artificial Intelligence & Heuristics", code="CS-504", weekly_hours=3, consecutive_periods=1, is_lab=False, color_code="#14b8a6")

        db.add_all([s_dsa, s_dsalab, s_dld, s_dm, s_oop, s_os, s_oslab, s_dbms, s_cn, s_ai])
        db.flush()

        # Teachers
        t_turing = Teacher(institution_id=inst.id, department_id=dept_cse.id, name="Prof. Alan Turing", code="AT-CSE", designation="Professor", max_hours_per_day=4, max_hours_per_week=18, competent_subject_ids=[s_dsa.id, s_dsalab.id, s_ai.id])
        t_knuth = Teacher(institution_id=inst.id, department_id=dept_cse.id, name="Dr. Donald Knuth", code="DK-CSE", designation="Associate Professor", max_hours_per_day=4, max_hours_per_week=18, competent_subject_ids=[s_dsa.id, s_oop.id, s_dbms.id])
        t_tanenbaum = Teacher(institution_id=inst.id, department_id=dept_cse.id, name="Dr. Andrew Tanenbaum", code="ATN-CSE", designation="Professor", max_hours_per_day=4, max_hours_per_week=18, competent_subject_ids=[s_os.id, s_oslab.id, s_cn.id])
        t_hopper = Teacher(institution_id=inst.id, department_id=dept_cse.id, name="Prof. Grace Hopper", code="GH-CSE", designation="Associate Professor", max_hours_per_day=4, max_hours_per_week=18, competent_subject_ids=[s_oop.id, s_dbms.id, s_dsalab.id])
        t_shannon = Teacher(institution_id=inst.id, department_id=dept_ece.id, name="Dr. Claude Shannon", code="CS-ECE", designation="Professor", max_hours_per_day=4, max_hours_per_week=16, competent_subject_ids=[s_dld.id, s_cn.id])
        t_ramanujan = Teacher(institution_id=inst.id, department_id=dept_math.id, name="Dr. Srinivasa Ramanujan", code="SR-MATH", designation="Senior Professor", max_hours_per_day=4, max_hours_per_week=18, competent_subject_ids=[s_dm.id])

        db.add_all([t_turing, t_knuth, t_tanenbaum, t_hopper, t_shannon, t_ramanujan])
        db.commit()
        return inst.id

    @classmethod
    def load_coaching_institute(cls, db: Session) -> int:
        existing = db.query(Institution).filter(Institution.code == "OLYMPUS-PREP").first()
        if existing:
            return existing.id

        inst = Institution(
            name="Olympus IIT-JEE & NEET Academy",
            type="COACHING",
            code="OLYMPUS-PREP",
            description="Intensive competitive entrance coaching institute with high-impact problem-solving sessions and dual shifts.",
            contact_email="director@olympusprep.in",
            working_days=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
            periods_per_day=6,
            period_duration_minutes=60,
            day_start_time="07:30",
            breaks=[
                {"name": "Tea & Discussion Break", "after_period": 2, "duration_minutes": 15},
                {"name": "Lunch & Mentoring", "after_period": 4, "duration_minutes": 45}
            ],
            shifts=[
                {"name": "Morning IIT-JEE Shift", "start_time": "07:30", "end_time": "13:45", "periods": 6},
                {"name": "Evening NEET Shift", "start_time": "14:15", "end_time": "20:30", "periods": 6}
            ]
        )
        db.add(inst)
        db.flush()

        # Departments
        dept_phy = Department(institution_id=inst.id, name="Physics Faculty", code="PHY")
        dept_chem = Department(institution_id=inst.id, name="Chemistry Faculty", code="CHEM")
        dept_math = Department(institution_id=inst.id, name="Mathematics Faculty", code="MATH")
        dept_bio = Department(institution_id=inst.id, name="Biology & Medical Sciences", code="BIO")
        db.add_all([dept_phy, dept_chem, dept_math, dept_bio])
        db.flush()

        # Classes & Divisions
        cg_jee1 = ClassGroup(institution_id=inst.id, name="JEE Advanced Target Batch", code="JEE-ADV-26", year=1)
        cg_neet1 = ClassGroup(institution_id=inst.id, name="NEET Apex Medical Batch", code="NEET-MED-26", year=1)
        db.add_all([cg_jee1, cg_neet1])
        db.flush()

        div_j1 = Division(institution_id=inst.id, class_group_id=cg_jee1.id, name="Batch Alpha (JEE)", student_count=50)
        div_n1 = Division(institution_id=inst.id, class_group_id=cg_neet1.id, name="Batch Genesis (NEET)", student_count=50)
        db.add_all([div_j1, div_n1])
        db.flush()

        # Rooms
        audi_1 = Room(institution_id=inst.id, name="Auditorium Hall A (Smart AV)", code="AUDI-A", room_type="lecture", capacity=70)
        audi_2 = Room(institution_id=inst.id, name="Auditorium Hall B (Smart AV)", code="AUDI-B", room_type="lecture", capacity=70)
        db.add_all([audi_1, audi_2])
        db.flush()

        # Subjects
        s_j_phy = Subject(institution_id=inst.id, class_group_id=cg_jee1.id, department_id=dept_phy.id, name="Advanced Mechanics & Electromagnetism", code="JEE-PHY", weekly_hours=6, consecutive_periods=2, is_lab=False, color_code="#0ea5e9")
        s_j_mth = Subject(institution_id=inst.id, class_group_id=cg_jee1.id, department_id=dept_math.id, name="Calculus & Coordinate Geometry", code="JEE-MTH", weekly_hours=6, consecutive_periods=2, is_lab=False, color_code="#6366f1")
        s_j_chm = Subject(institution_id=inst.id, class_group_id=cg_jee1.id, department_id=dept_chem.id, name="Physical & Organic Chemistry", code="JEE-CHM", weekly_hours=6, consecutive_periods=2, is_lab=False, color_code="#f59e0b")

        s_n_bio = Subject(institution_id=inst.id, class_group_id=cg_neet1.id, department_id=dept_bio.id, name="Botany & Zoology Masterclass", code="NEET-BIO", weekly_hours=8, consecutive_periods=2, is_lab=False, color_code="#10b981")
        s_n_phy = Subject(institution_id=inst.id, class_group_id=cg_neet1.id, department_id=dept_phy.id, name="NEET Applied Physics", code="NEET-PHY", weekly_hours=5, consecutive_periods=1, is_lab=False, color_code="#0ea5e9")
        s_n_chm = Subject(institution_id=inst.id, class_group_id=cg_neet1.id, department_id=dept_chem.id, name="NEET Inorganic & Organic Chemistry", code="NEET-CHM", weekly_hours=5, consecutive_periods=1, is_lab=False, color_code="#f59e0b")

        db.add_all([s_j_phy, s_j_mth, s_j_chm, s_n_bio, s_n_phy, s_n_chm])
        db.flush()

        # Star Teachers
        t_p1 = Teacher(institution_id=inst.id, department_id=dept_phy.id, name="H.C. Verma (Physics Lead)", code="HCV-PHY", designation="Senior Specialist", max_hours_per_day=4, max_hours_per_week=20, competent_subject_ids=[s_j_phy.id, s_n_phy.id])
        t_m1 = Teacher(institution_id=inst.id, department_id=dept_math.id, name="I.A. Maron (Math Lead)", code="IAM-MTH", designation="Senior Specialist", max_hours_per_day=4, max_hours_per_week=20, competent_subject_ids=[s_j_mth.id])
        t_c1 = Teacher(institution_id=inst.id, department_id=dept_chem.id, name="O.P. Tandon (Chemistry Lead)", code="OPT-CHM", designation="Senior Specialist", max_hours_per_day=4, max_hours_per_week=20, competent_subject_ids=[s_j_chm.id, s_n_chm.id])
        t_b1 = Teacher(institution_id=inst.id, department_id=dept_bio.id, name="Dr. Trueman (Biology Lead)", code="TM-BIO", designation="Senior Specialist", max_hours_per_day=4, max_hours_per_week=20, competent_subject_ids=[s_n_bio.id])

        db.add_all([t_p1, t_m1, t_c1, t_b1])
        db.commit()
        return inst.id
