"""
Demo seed function — importable version of seed.py for programmatic reseeding.
Creates demo tenant, users, classes, subjects, enrollments, attendance, marks, timetable, lectures.
"""
import uuid
import random
from datetime import date, time


def seed_demo_data(db):
    """Seed comprehensive demo data into the database."""
    from src.domains.identity.models.tenant import Tenant
    from src.domains.identity.models.user import User
    from src.domains.academic.models.core import Class, Subject, Enrollment
    from src.domains.academic.models.parent_link import ParentLink
    from src.domains.academic.models.attendance import Attendance
    from src.domains.academic.models.marks import Exam, Mark
    from src.domains.academic.models.timetable import Timetable
    from src.domains.academic.models.lecture import Lecture

    # ─── Tenant ──────────────────────────────────
    tenant_id = uuid.UUID("00000000-0000-0000-0000-000000000001")
    db.add(Tenant(
        id=tenant_id,
        name="Demo School — Vidya Academy",
        domain="demo.school",
        plan_tier="enterprise",
        max_students=200,
        ai_daily_limit=500,
    ))
    db.flush()

    # ─── Users ───────────────────────────────────
    admin_id = uuid.UUID("00000000-0000-0000-0000-000000000010")
    teacher_id = uuid.UUID("00000000-0000-0000-0000-000000000020")
    parent_id = uuid.UUID("00000000-0000-0000-0000-000000000030")

    db.add(User(id=admin_id, tenant_id=tenant_id, email="admin@demo.school",
                full_name="Dr. Rajesh Kumar (Principal)", role="admin"))
    db.add(User(id=teacher_id, tenant_id=tenant_id, email="teacher@demo.school",
                full_name="Ms. Ananya Sharma", role="teacher"))
    db.add(User(id=parent_id, tenant_id=tenant_id, email="parent@demo.school",
                full_name="Mr. Vikram Patel", role="parent"))

    student_data = [
        ("00000000-0000-0000-0000-000000000041", "Arjun Patel", "arjun@demo.school"),
        ("00000000-0000-0000-0000-000000000042", "Priya Singh", "priya@demo.school"),
        ("00000000-0000-0000-0000-000000000043", "Rahul Kumar", "rahul@demo.school"),
        ("00000000-0000-0000-0000-000000000044", "Sneha Iyer", "sneha@demo.school"),
        ("00000000-0000-0000-0000-000000000045", "Aditya Nair", "aditya@demo.school"),
    ]
    student_ids = []
    for sid, name, email in student_data:
        uid = uuid.UUID(sid)
        student_ids.append(uid)
        db.add(User(id=uid, tenant_id=tenant_id, email=email, full_name=name, role="student"))

    db.flush()

    # Link parent to first student
    db.add(ParentLink(tenant_id=tenant_id, parent_id=parent_id, child_id=student_ids[0]))

    # ─── Classes ─────────────────────────────────
    class_10a_id = uuid.UUID("00000000-0000-0000-0000-000000000100")
    class_9b_id = uuid.UUID("00000000-0000-0000-0000-000000000101")
    db.add(Class(id=class_10a_id, tenant_id=tenant_id, name="Class 10-A",
                 grade_level="10", academic_year="2025-26"))
    db.add(Class(id=class_9b_id, tenant_id=tenant_id, name="Class 9-B",
                 grade_level="9", academic_year="2025-26"))

    # ─── Subjects ────────────────────────────────
    subjects = {}
    subject_names = ["Mathematics", "Science", "English", "Hindi", "Social Studies"]
    for i, subj_name in enumerate(subject_names):
        subj_id = uuid.UUID(f"00000000-0000-0000-0000-0000000002{i:02d}")
        subjects[subj_name] = subj_id
        db.add(Subject(id=subj_id, tenant_id=tenant_id, name=subj_name, class_id=class_10a_id))

    db.flush()

    # ─── Enrollments ─────────────────────────────
    for i, sid in enumerate(student_ids):
        db.add(Enrollment(
            tenant_id=tenant_id, student_id=sid, class_id=class_10a_id,
            roll_number=str(i + 1), academic_year="2025-26",
        ))

    # ─── Attendance (15 days) ────────────────────
    for sid in student_ids:
        for day_offset in range(15):
            d = date(2026, 2, 15 + day_offset if day_offset < 14 else 1)
            if day_offset >= 14:
                d = date(2026, 3, day_offset - 13)
            status = random.choices(["present", "absent", "late"], weights=[82, 10, 8])[0]
            db.add(Attendance(
                tenant_id=tenant_id, student_id=sid, class_id=class_10a_id,
                date=d, status=status,
            ))

    # ─── Exams & Marks ───────────────────────────
    exam_names = ["Unit Test 1", "Midterm", "Unit Test 2"]
    for exam_idx, exam_name in enumerate(exam_names):
        for subj_name, subj_id in subjects.items():
            exam_id = uuid.uuid4()
            exam_date = date(2026, 1 + exam_idx, 15)
            db.add(Exam(
                id=exam_id, tenant_id=tenant_id,
                name=f"{exam_name} - {subj_name}",
                subject_id=subj_id, max_marks=100,
                exam_date=exam_date,
            ))
            db.flush()
            # Generate realistic marks with some variation per student
            base_marks = {"Arjun Patel": 78, "Priya Singh": 88, "Rahul Kumar": 65,
                          "Sneha Iyer": 92, "Aditya Nair": 71}
            for sid in student_ids:
                student = db.query(User).filter(User.id == sid).first()
                base = base_marks.get(student.full_name, 75) if student else 75
                marks = min(100, max(30, base + random.randint(-10, 10)))
                db.add(Mark(tenant_id=tenant_id, student_id=sid, exam_id=exam_id, marks_obtained=marks))

    # ─── Timetable (Full week) ───────────────────
    daily_slots = [
        (time(9, 0), time(9, 45), "Mathematics"),
        (time(9, 45), time(10, 30), "Science"),
        (time(11, 0), time(11, 45), "English"),
        (time(11, 45), time(12, 30), "Hindi"),
        (time(13, 30), time(14, 15), "Social Studies"),
    ]
    for dow in range(5):  # Mon-Fri
        for start, end, subj in daily_slots:
            db.add(Timetable(
                tenant_id=tenant_id, class_id=class_10a_id,
                subject_id=subjects[subj], teacher_id=teacher_id,
                day_of_week=dow, start_time=start, end_time=end,
            ))

    # ─── Lectures ────────────────────────────────
    from datetime import datetime, timedelta, timezone
    now_utc = datetime.now(timezone.utc)
    
    lectures = [
        ("Mathematics", "Introduction to Quadratic Equations", "https://www.youtube.com/watch?v=ZIEFBhKlPCU"),
        ("Science", "Photosynthesis — The Complete Process", "https://www.youtube.com/watch?v=CMiGKs0M0sg"),
        ("English", "Shakespeare's Merchant of Venice — Act 1", "https://www.youtube.com/watch?v=xGQFqglkSIk"),
        ("Social Studies", "Indian Independence Movement", "https://www.youtube.com/watch?v=JqHqJHhk7bI"),
    ]
    for subj, title, url in lectures:
        db.add(Lecture(
            tenant_id=tenant_id, 
            subject_id=subjects[subj], 
            class_id=class_10a_id,
            teacher_id=teacher_id,
            title=title, 
            youtube_url=url,
            scheduled_at=now_utc - timedelta(days=2)
        ))

    # ─── Assignments ──────────────────────────────
    from src.domains.academic.models.assignment import Assignment, AssignmentSubmission

    now_utc = datetime.now(timezone.utc)
    assignment_data = [
        ("Mathematics", "Solve Quadratic Equations (Ch. 4)", "Solve problems 1-25 from Chapter 4. Show all steps.", -2),
        ("Mathematics", "Coordinate Geometry Worksheet", "Plot the given points and find distances between them.", 5),
        ("Science", "Photosynthesis Lab Report", "Write a 2-page report on the photosynthesis experiment conducted in class. Include diagrams.", -1),
        ("Science", "Chemical Reactions Diagram", "Draw and label 5 types of chemical reactions with real-life examples.", 7),
        ("English", "Merchant of Venice Essay", "Write a 500-word essay on the theme of justice in Act 1-3.", 3),
        ("Hindi", "निबंध — भारत की विविधता", "800 शब्दों में भारत की सांस्कृतिक विविधता पर निबंध लिखें।", 10),
    ]
    assignment_ids = []
    for subj_name, title, desc, days_offset in assignment_data:
        a_id = uuid.uuid4()
        assignment_ids.append(a_id)
        db.add(Assignment(
            id=a_id, tenant_id=tenant_id, subject_id=subjects[subj_name],
            title=title, description=desc,
            due_date=now_utc + timedelta(days=days_offset),
            created_by=teacher_id,
        ))

    db.flush()

    # Submissions: Arjun submitted 3 assignments, some graded
    for i, a_id in enumerate(assignment_ids[:3]):
        db.add(AssignmentSubmission(
            tenant_id=tenant_id, assignment_id=a_id, student_id=student_ids[0],
            submission_url=f"uploads/arjun_assignment_{i+1}.pdf",
            grade=random.choice([78, 85, 92, None]),
            feedback="Good work! Pay attention to showing derivation steps." if i == 0 else None,
        ))

    # ─── Complaints ───────────────────────────────
    from src.domains.administrative.models.complaint import Complaint

    db.add(Complaint(
        tenant_id=tenant_id, student_id=student_ids[0],
        category="facilities",
        description="The projector in Room 204 has been broken for 2 weeks. It makes the Science presentations very difficult to follow.",
        status="in_review",
    ))
    db.add(Complaint(
        tenant_id=tenant_id, student_id=student_ids[1],
        category="academics",
        description="The Mathematics Unit Test 2 had questions from chapters that were not yet covered in class.",
        status="resolved", resolved_by=admin_id,
        resolution_note="Reviewed with Ms. Sharma. Extra class scheduled for the missed chapters. Marks adjusted for affected questions.",
    ))

    # ─── AI Query Logs ────────────────────────────
    from src.domains.platform.models.ai import AIQuery

    ai_queries = [
        ("Explain photosynthesis in simple terms", "qa",
         "Photosynthesis is the process by which green plants use sunlight, water, and carbon dioxide to make food (glucose) and release oxygen. It happens in the chloroplasts of leaf cells.\n\n**Light Reaction:** Sunlight splits water → produces ATP + NADPH + O₂\n**Calvin Cycle:** CO₂ is fixed into glucose using ATP + NADPH\n\n📚 Source: Chapter 6, Biology NCERT (p.42-45)", 340, 820, 3),
        ("What is the quadratic formula and when do I use it?", "qa",
         "The quadratic formula solves any equation of the form ax² + bx + c = 0:\n\n**x = (-b ± √(b²-4ac)) / 2a**\n\nUse it when:\n1. Factoring is difficult\n2. Coefficients are large\n3. Discriminant analysis is needed\n\n📚 Source: Chapter 4, Mathematics NCERT (p.71)", 280, 650, 2),
        ("Generate a quiz on Indian Independence Movement", "quiz",
         '{"questions": [{"q": "Who led the Salt March in 1930?", "options": ["Jawaharlal Nehru", "Mahatma Gandhi", "Subhas Chandra Bose", "Sardar Patel"], "answer": 1}, {"q": "In which year was the Quit India Movement launched?", "options": ["1940", "1942", "1944", "1946"], "answer": 1}]}', 420, 1100, 0),
        ("Create flashcards for chemical bonding", "flashcards",
         '{"cards": [{"front": "What is an ionic bond?", "back": "A bond formed by the transfer of electrons from one atom to another, creating oppositely charged ions."}, {"front": "What is a covalent bond?", "back": "A bond formed by the sharing of electron pairs between atoms."}]}', 380, 900, 0),
        ("Summarize Act 1 of Merchant of Venice", "qa",
         "**Act 1 Summary:**\n\nAntonio, a wealthy merchant, agrees to borrow money from Shylock for his friend Bassanio, who needs funds to court Portia. Shylock demands a pound of Antonio's flesh as collateral.\n\nMeanwhile in Belmont, Portia discusses the casket test her father left: suitors must choose between gold, silver, and lead caskets.\n\n**Key Themes:** Friendship, greed, appearance vs reality\n\n📚 Source: Merchant of Venice, Act 1 Scenes 1-3", 450, 950, 4),
        ("What are Newton's three laws of motion?", "qa",
         "**Newton's Three Laws of Motion:**\n\n1. **First Law (Inertia):** An object stays at rest or in uniform motion unless acted on by an external force.\n\n2. **Second Law (F=ma):** Force equals mass × acceleration. More force = more acceleration.\n\n3. **Third Law (Action-Reaction):** Every action has an equal and opposite reaction.\n\n📚 Source: Chapter 9, Physics NCERT (p.118-125)", 310, 780, 3),
        ("Help me understand trigonometric identities", "study_guide",
         "# Trigonometric Identities Study Guide\n\n## Basic Identities\n- sin²θ + cos²θ = 1\n- tan θ = sin θ / cos θ\n- 1 + tan²θ = sec²θ\n\n## Tips for Remembering\n- Use the unit circle\n- Practice converting between forms\n- Start with sin²+cos²=1 and derive others", 520, 1200, 0),
        ("Explain the water cycle with a concept map", "concept_map",
         '{"nodes": ["Evaporation", "Condensation", "Precipitation", "Collection", "Transpiration"], "edges": [["Evaporation", "Condensation"], ["Condensation", "Precipitation"], ["Precipitation", "Collection"], ["Collection", "Evaporation"], ["Transpiration", "Condensation"]]}', 400, 1050, 0),
        ("Analyze my weak topics in Science", "weak_topic",
         "Based on your recent Science exams (average 58%), your weakest topics are **Thermodynamics** and **Cell Division**.\n\n### Remediation Plan:\n1. **Day 1**: Re-read Chapter 4 (Cell Cycle) and watch the uploaded lecture.\n2. **Day 2**: Practice 20 MCQs on Thermodynamics.\n3. **Day 3**: Try a concept map connecting Mitosis and Meiosis.\n\n📚 Source: Subject Performance Analytics", 550, 1400, 0),
        ("How does a bill become a law?", "flowchart",
         "```mermaid\ngraph TD;\nA[Idea Drafted] --> B[Introduced in House/Senate];\nB --> C[Committee Review];\nC --> D[Floor Debate and Vote];\nD --> E[Sent to Other Chamber];\nE --> F[President Signs/Vetoes];\nF --> G{Is it Law?};\nG -- Signed --> H[Law Enacted];\nG -- Vetoed --> I[Return to Congress for Override];\n```", 320, 800, 0),
        ("Create a mind map for World War II", "mindmap",
         '{"name": "World War II", "children": [{"name": "Causes", "children": [{"name": "Treaty of Versailles"}, {"name": "Rise of Fascism"}]}, {"name": "Major Theaters", "children": [{"name": "European"}, {"name": "Pacific"}]}, {"name": "Outcomes", "children": [{"name": "United Nations Created"}, {"name": "Cold War Begins"}]}]}', 610, 1300, 0),
        ("I think gravity pulls things down.", "socratic",
         "That's a very intuitive start! Indeed, objects fall towards the Earth. But let me ask you this: if gravity is pulling everything *down*, why does the Moon stay up in the sky instead of crashing into us? What role do you think its velocity plays in orbit?", 180, 500, 0),
        ("I mastered Pythagorean theorem. Ask me something harder.", "perturbation",
         "Excellent. You know that for a right-angled triangle, a² + b² = c².\n\nBut what if the triangle is **NOT** a right-angled triangle? Can we still use the Pythagorean theorem, or do we need something else to find the missing side? Tell me about the Law of Cosines.", 220, 600, 0),
        ("Renewable energy is the only solution.", "debate",
         "While transitioning to renewable energy is essential for climate goals, your argument ignores the 'base-load' problem. Solar and wind are intermittent. Without massive, incredibly expensive battery infrastructure, a grid cannot provide 24/7 continuous power strictly on renewables alone. Should we rely entirely on weather patterns?", 310, 850, 0),
        ("Can you review my essay on Macbeth's ambition?", "essay_review",
         "**Structure**: Strong introduction; thesis is clear in paragraph 1.\n**Evidence**: Paragraph 3 lacks supporting quotes. Consider adding a citation regarding Lady Macbeth's influence in Act 1, Scene 5.\n**Grammar/Flow**: Your transitions between paragraph 2 and 3 feel abrupt. Try using a transition phrase like 'Furthermore' or 'Consequently'.\n\nOverall Score: 7.5/10. Focus on embedding your quotes smoothly.", 400, 950, 0),
    ]
    for i, (query, mode, response, tokens, time_ms, citations) in enumerate(ai_queries):
        db.add(AIQuery(
            tenant_id=tenant_id,
            user_id=student_ids[i % len(student_ids)],
            query_text=query, mode=mode,
            response_text=response,
            token_usage=tokens, response_time_ms=time_ms,
            citation_count=citations,
            trace_id=f"demo-trace-{uuid.uuid4().hex[:12]}",
        ))

    # ─── Uploaded Documents ───────────────────────
    from src.domains.platform.models.document import Document

    doc_data = [
        (teacher_id, subjects["Mathematics"], "NCERT_Mathematics_Ch4_Quadratics.pdf", "pdf", "completed", 24),
        (teacher_id, subjects["Science"], "Biology_Photosynthesis_Notes.pdf", "pdf", "completed", 18),
        (teacher_id, subjects["English"], "Merchant_of_Venice_Analysis.pdf", "pdf", "completed", 31),
        (teacher_id, subjects["Social Studies"], "Indian_Independence_Movement.pdf", "pdf", "completed", 22),
        (student_ids[0], subjects["Mathematics"], "Arjun_Quadratic_Equations_Notes.pdf", "pdf", "completed", 8),
        (student_ids[0], subjects["Science"], "Lab_Report_Photosynthesis.docx", "docx", "completed", 5),
    ]
    for uploader, subj_id, fname, ftype, status, chunks in doc_data:
        db.add(Document(
            tenant_id=tenant_id, subject_id=subj_id,
            uploaded_by=uploader,
            file_name=fname, file_type=ftype,
            storage_path=f"uploads/{fname}",
            ingestion_status=status, chunk_count=chunks,
        ))

    # ─── Subject Performance ──────────────────────
    from src.domains.academic.models.performance import SubjectPerformance

    perf_data = {
        student_ids[0]: {"Mathematics": 78, "Science": 72, "English": 82, "Hindi": 75, "Social Studies": 79},
        student_ids[1]: {"Mathematics": 88, "Science": 91, "English": 85, "Hindi": 90, "Social Studies": 87},
        student_ids[2]: {"Mathematics": 62, "Science": 58, "English": 70, "Hindi": 65, "Social Studies": 68},
        student_ids[3]: {"Mathematics": 94, "Science": 96, "English": 88, "Hindi": 92, "Social Studies": 90},
        student_ids[4]: {"Mathematics": 71, "Science": 68, "English": 74, "Hindi": 70, "Social Studies": 73},
    }
    for sid, perfs in perf_data.items():
        for subj_name, avg_score in perfs.items():
            db.add(SubjectPerformance(
                tenant_id=tenant_id, student_id=sid,
                subject_id=subjects[subj_name],
                average_score=avg_score,
            ))

    # ─── Spaced Repetition Reviews ────────────────
    from src.domains.platform.models.spaced_repetition import ReviewSchedule

    review_topics = [
        ("Quadratic Formula Derivation", "Mathematics", 0, 3, 2.6),
        ("Photosynthesis Light Reactions", "Science", 1, 7, 2.8),
        ("Shakespeare's Themes", "English", -1, 1, 2.3),
        ("Newton's Laws of Motion", "Science", 2, 4, 2.5),
        ("Trigonometric Identities", "Mathematics", 5, 14, 3.0),
    ]
    for topic, subj, days_offset, interval, ease in review_topics:
        db.add(ReviewSchedule(
            tenant_id=tenant_id, student_id=student_ids[0],
            subject_id=subjects[subj],
            topic=topic,
            next_review_at=now_utc + timedelta(days=days_offset),
            interval_days=interval, ease_factor=ease,
            review_count=random.randint(1, 5),
        ))

    # ─── Test Series & Leaderboard ─────────────────
    from src.domains.academic.models.test_series import TestSeries, MockTestAttempt

    ts1_id = uuid.UUID("00000000-0000-0000-0000-000000000501")
    ts2_id = uuid.UUID("00000000-0000-0000-0000-000000000502")

    db.add(TestSeries(
        id=ts1_id, tenant_id=tenant_id, name="JEE Main 2026 Mock Series",
        description="Full-length JEE Main mock test with Physics, Chemistry, and Mathematics.",
        subject_id=subjects["Mathematics"], class_id=class_10a_id,
        total_marks=300, duration_minutes=180, is_active=True, created_by=teacher_id,
    ))
    db.add(TestSeries(
        id=ts2_id, tenant_id=tenant_id, name="NEET Biology Mock Test",
        description="Biology section mock test covering Botany and Zoology.",
        subject_id=subjects["Science"], class_id=class_10a_id,
        total_marks=180, duration_minutes=90, is_active=True, created_by=teacher_id,
    ))
    db.flush()

    # Mock Test Attempts — 5 students with varied results
    ts1_attempts = [
        (student_ids[0], 225, 300, 140, 1, 80.0),   # Arjun - Rank 3
        (student_ids[1], 260, 300, 165, 2, 60.0),   # Priya - Rank 2
        (student_ids[2], 185, 300, 170, 3, 40.0),   # Rahul - Rank 4
        (student_ids[3], 275, 300, 150, 4, 100.0),  # Sneha - Rank 1
        (student_ids[4], 170, 300, 175, 5, 0.0),    # Aditya - Rank 5
    ]
    # Sort by marks desc to assign real ranks
    ts1_attempts_sorted = sorted(ts1_attempts, key=lambda x: -x[1])
    for rank, (sid, marks, total, time_min, _, _) in enumerate(ts1_attempts_sorted, 1):
        percentile = round((len(ts1_attempts_sorted) - rank) / len(ts1_attempts_sorted) * 100, 1)
        db.add(MockTestAttempt(
            tenant_id=tenant_id, test_series_id=ts1_id, student_id=sid,
            marks_obtained=marks, total_marks=total, time_taken_minutes=time_min,
            rank=rank, percentile=percentile,
        ))

    ts2_attempts = [
        (student_ids[0], 130, 180, 75),   # Arjun
        (student_ids[1], 155, 180, 80),   # Priya
        (student_ids[2], 110, 180, 85),   # Rahul
        (student_ids[3], 165, 180, 70),   # Sneha
        (student_ids[4], 95, 180, 88),    # Aditya
    ]
    ts2_sorted = sorted(ts2_attempts, key=lambda x: -x[1])
    for rank, (sid, marks, total, time_min) in enumerate(ts2_sorted, 1):
        percentile = round((len(ts2_sorted) - rank) / len(ts2_sorted) * 100, 1)
        db.add(MockTestAttempt(
            tenant_id=tenant_id, test_series_id=ts2_id, student_id=sid,
            marks_obtained=marks, total_marks=total, time_taken_minutes=time_min,
            rank=rank, percentile=percentile,
        ))

    db.commit()
    print("Demo data seeded successfully.")
    return True

