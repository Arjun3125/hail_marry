"""
Canonical Class 11 CBSE showcase seeder.

This is the single supported demo dataset for VidyaOS. It provisions one
Class 11 Science (CBSE) tenant with six months of synthetic history for the
student, parent, teacher, and admin personas used in the product walkthrough.

Run: ``python seed_cbse_demo.py``
Optional env var:
  ``EMBEDDING_API_KEY`` for live NVIDIA NIM embeddings
"""
import os
import uuid
import random
from datetime import datetime, timedelta, date, time, UTC
from pathlib import Path

from loguru import logger
from dotenv import load_dotenv

load_dotenv("../.env")

from database import SessionLocal, engine, Base
import models  # noqa — register all ORM models

from src.domains.identity.models.tenant import Tenant
from src.domains.identity.models.user import User
from src.domains.academic.models.core import Class, Subject, Enrollment
from src.domains.academic.models.attendance import Attendance
from src.domains.academic.models.marks import Exam, Mark
from src.domains.academic.models.timetable import Timetable
from src.domains.academic.models.lecture import Lecture
from src.domains.academic.models.assignment import Assignment, AssignmentSubmission
from src.domains.academic.models.performance import SubjectPerformance
from src.domains.academic.services.student_profile_sync import sync_student_profile_context
from src.domains.academic.models.test_series import TestSeries, MockTestAttempt
from src.domains.academic.models.parent_link import ParentLink
from src.domains.platform.models.notebook import Notebook
from src.domains.platform.models.document import Document
from src.domains.platform.models.ai import AIFolder, AIQuery
from src.domains.platform.models.audit import AuditLog
from src.domains.platform.models.generated_content import GeneratedContent
from src.domains.platform.models.topic_mastery import TopicMastery
from src.domains.platform.models.learner_profile import LearnerProfile
from src.domains.platform.models.study_path_plan import StudyPathPlan
from src.domains.platform.models.spaced_repetition import ReviewSchedule
from src.domains.platform.models.knowledge_graph import KGConcept, KGRelationship
from src.domains.platform.models.notification import Notification, NotificationPreference
from src.domains.platform.models.study_session import StudySession
from src.domains.platform.models.usage_counter import UsageCounter

# ── Config ────────────────────────────────────────────────────
EMBED_MODEL = "nvidia/nv-embedqa-e5-v5"
EMBED_DIM = 1024
EMBED_API_KEY = os.getenv("EMBEDDING_API_KEY", "")
EMBED_BASE_URL = "https://integrate.api.nvidia.com/v1"
TENANT_NAME = "Modern Hustlers Academy"
DEMO_STUDENT_EMAIL = "demo_cbse11@modernhustlers.com"
DEMO_TEACHER_EMAIL = "teacher@modernhustlers.com"
DEMO_ADMIN_EMAIL = "admin@modernhustlers.com"
DEMO_PARENT_EMAIL = "parent@modernhustlers.com"

# ── CBSE 11 Study Material ────────────────────────────────────
NOTEBOOKS = {
    "Physics": {
        "name": "NCERT Physics Vol 1",
        "icon": "Book",
        "color": "#8b5cf6",
        "chunks": [
            "Chapter 2 - Units and Measurements: The SI system defines seven base units. The metre is the unit of length, kilogram for mass, second for time, ampere for electric current, kelvin for temperature, mole for amount of substance, and candela for luminous intensity. Dimensional analysis helps verify equations and convert units.",
            "Chapter 3 - Motion in a Straight Line: Displacement is a vector quantity representing the shortest path between initial and final positions. Distance is a scalar representing total path length. Average velocity equals displacement divided by time interval. Instantaneous velocity is the limit of average velocity as time interval approaches zero.",
            "Chapter 4 - Motion in a Plane: Projectile motion is the motion of an object thrown at an angle to the horizontal. The horizontal component of velocity remains constant while vertical component changes due to gravity. Range R = (u²sin2θ)/g and maximum height H = (u²sin²θ)/(2g).",
            "Chapter 5 - Laws of Motion: Newton's First Law states that a body remains at rest or in uniform motion unless acted upon by an external force (law of inertia). Newton's Second Law: F = ma, force equals mass times acceleration. Newton's Third Law: For every action there is an equal and opposite reaction.",
            "Chapter 6 - Work, Energy and Power: Work done W = F·d·cosθ. Kinetic energy KE = ½mv². The work-energy theorem states that net work done on an object equals the change in its kinetic energy. Power is the rate of doing work, P = W/t, measured in watts.",
            "Chapter 7 - System of Particles: The centre of mass of a system is the point where the entire mass can be considered concentrated. For a rigid body, the centre of mass moves as if all external forces act on it. Torque τ = r × F is the rotational analogue of force.",
        ],
    },
    "Chemistry": {
        "name": "NCERT Chemistry Part 1",
        "icon": "FlaskConical",
        "color": "#10b981",
        "chunks": [
            "Chapter 12 - Organic Chemistry: IUPAC nomenclature follows systematic rules for naming organic compounds. The longest carbon chain determines the parent name: meth- (1C), eth- (2C), prop- (3C), but- (4C), pent- (5C). Functional groups get characteristic suffixes: -ol (alcohol), -al (aldehyde), -one (ketone), -oic acid (carboxylic acid).",
            "Chapter 12 - Isomerism: Structural isomers have the same molecular formula but different structural arrangements. Chain isomers differ in carbon skeleton, position isomers differ in position of functional group, and functional group isomers have different functional groups.",
            "Chapter 4 - Chemical Bonding: A covalent bond is formed by sharing of electron pairs between atoms. Sigma bonds result from head-on overlap and pi bonds from lateral overlap of orbitals. VSEPR theory predicts molecular geometry based on electron pair repulsion around the central atom.",
            "Chapter 6 - Thermodynamics: Enthalpy change (ΔH) measures heat exchange at constant pressure. Exothermic reactions have negative ΔH (release heat). Endothermic reactions have positive ΔH (absorb heat). Hess's Law states that total enthalpy change is independent of the pathway.",
            "Chapter 7 - Equilibrium: Chemical equilibrium is reached when rate of forward reaction equals rate of backward reaction. Le Chatelier's Principle: if a system at equilibrium is disturbed, it shifts to counteract the disturbance. The equilibrium constant Kc = [products]/[reactants].",
        ],
    },
    "Mathematics": {
        "name": "NCERT Mathematics",
        "icon": "Calculator",
        "color": "#3b82f6",
        "chunks": [
            "Chapter 13 - Limits and Derivatives: The limit of f(x) as x approaches a, written lim(x→a) f(x), is the value f(x) approaches. Standard limits include lim(x→0) sin(x)/x = 1 and lim(x→0) (1-cos(x))/x = 0. The derivative f'(x) = lim(h→0) [f(x+h) - f(x)]/h.",
            "Chapter 13 - Differentiation Rules: The power rule states d/dx(xⁿ) = nxⁿ⁻¹. Product rule: d/dx(uv) = u(dv/dx) + v(du/dx). Quotient rule: d/dx(u/v) = [v(du/dx) - u(dv/dx)]/v². Chain rule: d/dx f(g(x)) = f'(g(x))·g'(x).",
            "Chapter 1 - Sets: A set is a well-defined collection of distinct objects. Set operations include union (A∪B), intersection (A∩B), difference (A-B), and complement (A'). De Morgan's Laws: (A∪B)' = A'∩B' and (A∩B)' = A'∪B'.",
            "Chapter 3 - Trigonometric Functions: sin²θ + cos²θ = 1, 1 + tan²θ = sec²θ, 1 + cot²θ = cosec²θ. The sine rule: a/sinA = b/sinB = c/sinC. The cosine rule: c² = a² + b² - 2ab·cosC.",
            "Chapter 5 - Complex Numbers: A complex number z = a + bi where i = √(-1). The modulus |z| = √(a²+b²). Argand diagram plots complex numbers on a plane. Euler's formula: e^(iθ) = cosθ + i·sinθ.",
        ],
    },
    "English": {
        "name": "Hornbill & Snapshots",
        "icon": "BookOpen",
        "color": "#f59e0b",
        "chunks": [
            "The Portrait of a Lady by Khushwant Singh: The author describes his grandmother as short, fat, and slightly bent. She was beautiful in the way old people are. The story traces their changing relationship as he grows from a village school to a city university. The grandmother's death is described with serene composure.",
            "We're Not Afraid to Die by Gordon Cook: The narrative recounts a harrowing journey across the southern Indian Ocean. The family's boat is hit by a massive wave. The courage of the children, particularly the son's remark 'We're not afraid to die if we can all be together', is the emotional core of the story.",
            "Discovering Tut: Howard Carter discovered Tutankhamun's tomb in 1922 in the Valley of the Kings. The mummy was examined using CT scanning in 2005. Forensic analysis suggested Tut was about 19 when he died, likely from complications of a leg fracture.",
        ],
    },
    "Computer Science": {
        "name": "NCERT Computer Science with Python",
        "icon": "Code",
        "color": "#ec4899",
        "chunks": [
            "Chapter 5 - Getting Started with Python: Python is a high-level, interpreted programming language created by Guido van Rossum. It supports multiple paradigms including procedural, object-oriented, and functional programming. Variables in Python are dynamically typed. Common data types include int, float, str, bool, list, tuple, and dict.",
            "Chapter 6 - Flow of Control: Python uses if-elif-else statements for conditional execution. The for loop iterates over sequences (range, list, string). The while loop repeats as long as a condition is True. break exits the loop, continue skips to the next iteration, and pass is a null statement placeholder.",
            "Chapter 7 - Functions: Functions are defined using the def keyword. Parameters can be positional, keyword, or default. The return statement sends a value back to the caller. Variable scope follows the LEGB rule: Local, Enclosing, Global, Built-in.",
            "Chapter 9 - Lists: Lists are mutable ordered collections created with square brackets. Common operations include append(), extend(), insert(), pop(), remove(), and sort(). List comprehension provides a concise way to create lists: [expr for item in iterable if condition].",
            "Chapter 11 - Strings: Strings are immutable sequences of characters. Slicing syntax is str[start:stop:step]. Important methods include upper(), lower(), strip(), split(), join(), find(), replace(), and count(). f-strings provide formatted string literals.",
        ],
    },
}

# ── 6-Month AI History Templates ─────────────────────────────
AI_HISTORY = [
    {"mode": "qa", "q": "What is the difference between distance and displacement?", "r": "**Distance vs Displacement**\n\nBased on your NCERT Physics notebook:\n\n- **Distance** is a *scalar* quantity — it measures the total path length traveled, regardless of direction.\n- **Displacement** is a *vector* quantity — it measures the shortest straight-line distance between initial and final positions, with direction.\n\n**Example:** If you walk 3m east then 4m north, your distance is 7m but displacement is 5m (by Pythagoras).\n\n📖 *Source: Chapter 3 - Motion in a Straight Line*", "subj": "Physics", "cites": 2},
    {"mode": "qa", "q": "Explain Newton's three laws of motion with examples", "r": "# Newton's Laws of Motion\n\n## First Law (Inertia)\nA body at rest stays at rest, and a body in motion stays in uniform motion, unless acted upon by an external force.\n**Example:** A ball on a table won't move unless pushed.\n\n## Second Law (F = ma)\nThe acceleration of a body is directly proportional to the net force and inversely proportional to its mass.\n**Example:** Pushing a loaded cart requires more force than an empty one.\n\n## Third Law\nFor every action, there is an equal and opposite reaction.\n**Example:** Rocket exhaust pushes downward, propelling the rocket upward.\n\n📖 *Source: Chapter 5 - Laws of Motion*", "subj": "Physics", "cites": 2},
    {"mode": "quiz", "q": "Generate a quiz on IUPAC nomenclature", "r": "# 🧪 IUPAC Nomenclature Quiz\n\n**Q1.** What is the IUPAC name for CH₄?\n- A) Methane ✅\n- B) Ethane\n- C) Propane\n\n**Q2.** How many carbons does 'butane' have?\n- A) 3\n- B) 4 ✅\n- C) 5\n\n**Q3.** What suffix indicates an alcohol?\n- A) -al\n- B) -ol ✅\n- C) -one\n\n**Q4.** What is C₃H₈?\n- A) Ethane\n- B) Propane ✅\n- C) Butane\n\n**Score: Review Chapter 12 for full nomenclature rules!**", "subj": "Chemistry", "cites": 1},
    {"mode": "study_guide", "q": "Create a study guide for thermodynamics", "r": "# 📚 Study Guide: Thermodynamics (Ch. 6)\n\n## Key Concepts\n- **System & Surroundings** — System is the part under study\n- **Enthalpy (H)** — Heat content at constant pressure\n- **ΔH < 0** → Exothermic (releases heat)\n- **ΔH > 0** → Endothermic (absorbs heat)\n\n## Important Laws\n1. **First Law:** Energy cannot be created or destroyed (ΔU = q + w)\n2. **Hess's Law:** Total ΔH is path-independent\n\n## Must-Remember Formulas\n| Formula | Meaning |\n|---|---|\n| ΔG = ΔH - TΔS | Gibbs free energy |\n| w = -PΔV | Work done by expansion |", "subj": "Chemistry", "cites": 1},
    {"mode": "mindmap", "q": "Create a mind map for derivatives and differentiation", "r": "{\"central\": \"Derivatives\", \"branches\": [{\"topic\": \"Definition\", \"children\": [\"Limit definition\", \"Rate of change\", \"Slope of tangent\"]}, {\"topic\": \"Rules\", \"children\": [\"Power Rule: nxⁿ⁻¹\", \"Product Rule\", \"Quotient Rule\", \"Chain Rule\"]}, {\"topic\": \"Standard Results\", \"children\": [\"d/dx(sinx) = cosx\", \"d/dx(eˣ) = eˣ\", \"d/dx(lnx) = 1/x\"]}, {\"topic\": \"Applications\", \"children\": [\"Maxima & Minima\", \"Rate problems\", \"Tangent & Normal\"]}]}", "subj": "Mathematics", "cites": 2},
    {"mode": "socratic", "q": "Why does a ball keep rolling in space but stops on Earth?", "r": "Great question! Let's think step by step:\n\n🤔 **What stops the ball on Earth?**\n→ Friction from the ground and air resistance.\n\n🤔 **What happens in space?**\n→ There's no air and no ground friction.\n\n🤔 **So what law explains this?**\n→ Newton's First Law! An object in motion stays in motion unless an external force acts on it.\n\n💡 **Key Insight:** The ball doesn't \"want\" to stop — friction forces it to stop on Earth. In space, with no friction, it continues forever!\n\n*Can you think of another example of inertia in everyday life?*", "subj": "Physics", "cites": 1},
    {"mode": "qa", "q": "What is the derivative of x^5 using the power rule?", "r": "Using the **Power Rule** from your Calculus notebook:\n\nd/dx(xⁿ) = n·xⁿ⁻¹\n\nFor x⁵:\nd/dx(x⁵) = 5·x⁴\n\n✅ **Answer: 5x⁴**\n\n📖 *Source: Chapter 13 - Differentiation Rules*", "subj": "Mathematics", "cites": 1},
    {"mode": "debate", "q": "Are exothermic reactions more useful than endothermic?", "r": "# ⚔️ Debate: Exothermic vs Endothermic\n\n## 🔥 For Exothermic\n- **Combustion** powers cars, generators, and rockets\n- **Respiration** keeps us alive!\n\n## ❄️ For Endothermic\n- **Photosynthesis** sustains all life\n- **Cooking** involves endothermic processes\n\n## 🏆 Verdict\nBoth are essential! Exothermic reactions provide energy, while endothermic reactions enable crucial biological and industrial processes.", "subj": "Chemistry", "cites": 1},
    {"mode": "qa", "q": "Summarize 'The Portrait of a Lady'", "r": "# The Portrait of a Lady — Summary\n**By Khushwant Singh**\n\nThe story traces the author's evolving relationship with his grandmother across three phases:\n\n1. **Village Life:** Inseparable bond, grandmother feeds stale chapattis to street dogs.\n2. **City Life:** Bond loosens. She disapproves of music lessons.\n3. **University Years:** Complete disconnect. She spends time spinning her wheel.\n\n**Climax:** She celebrates his return by singing and playing the drum. That night she dies peacefully. Sparrows gather silently around her body.\n\n📖 *Source: Hornbill - Chapter 1*", "subj": "English", "cites": 1},
    {"mode": "flashcards", "q": "Flashcards for trigonometric identities", "r": "# 🎴 Trig Identity Flashcards\n\n**Card 1** — sin²θ + cos²θ = ? → **1**\n**Card 2** — 1 + tan²θ = ? → **sec²θ**\n**Card 3** — sin(A+B) = ? → **sinA·cosB + cosA·sinB**\n**Card 4** — cos(2θ) = ? → **cos²θ - sin²θ**\n**Card 5** — Sine Rule? → **a/sinA = b/sinB = c/sinC**", "subj": "Mathematics", "cites": 1},
    {"mode": "qa", "q": "What is Le Chatelier's Principle?", "r": "## Le Chatelier's Principle\n\nFrom your Chemistry notebook (Ch. 7 - Equilibrium):\n\n> *If a system at equilibrium is subjected to a change, the equilibrium shifts to counteract the change.*\n\n| Change | Shift Direction |\n|---|---|\n| Add reactant | → Forward |\n| Remove product | → Forward |\n| Increase temperature (exothermic) | ← Backward |\n| Increase pressure | → Toward fewer gas moles |", "subj": "Chemistry", "cites": 1},
    {"mode": "qa", "q": "What is projectile motion? Give the formula for range.", "r": "## Projectile Motion\n\nProjectile motion is the motion of an object launched at an angle θ to the horizontal with initial velocity u.\n\n**Key Formulas:**\n- Range: **R = (u²·sin2θ) / g**\n- Max Height: **H = (u²·sin²θ) / (2g)**\n- Time of Flight: **T = (2u·sinθ) / g**\n- Maximum range at θ = 45°\n\n📖 *Source: Chapter 4 - Motion in a Plane*", "subj": "Physics", "cites": 1},
    {"mode": "qa", "q": "Explain list comprehension in Python with examples", "r": "## List Comprehension in Python\n\nA concise way to create lists:\n\n```python\n# Basic syntax\n[expression for item in iterable if condition]\n\n# Examples:\nsquares = [x**2 for x in range(10)]\nevens = [x for x in range(20) if x % 2 == 0]\nupper = [s.upper() for s in ['hello', 'world']]\n```\n\n📖 *Source: Chapter 9 - Lists*", "subj": "Computer Science", "cites": 1},
    {"mode": "quiz", "q": "Generate a quiz on Python data types", "r": "# 🐍 Python Data Types Quiz\n\n**Q1.** Which is mutable? → List ✅\n**Q2.** type(3.14)? → float ✅\n**Q3.** Is a tuple mutable? → No ✅\n**Q4.** What does str(42) return? → '42' ✅", "subj": "Computer Science", "cites": 1},
    {"mode": "qa", "q": "What is the work-energy theorem?", "r": "## Work-Energy Theorem\n\nThe net work done on an object equals the change in its kinetic energy:\n\nW_net = ΔKE = ½mv² - ½mu²\n\nThis means if positive work is done, the object speeds up. If negative work is done (friction), it slows down.\n\n📖 *Source: Chapter 6 - Work, Energy and Power*", "subj": "Physics", "cites": 1},
    {"mode": "qa", "q": "Explain VSEPR theory", "r": "## VSEPR Theory\n\nValence Shell Electron Pair Repulsion theory predicts molecular geometry.\n\n| Electron Pairs | Shape |\n|---|---|\n| 2 | Linear (180°) |\n| 3 | Trigonal planar (120°) |\n| 4 | Tetrahedral (109.5°) |\n| 5 | Trigonal bipyramidal |\n| 6 | Octahedral (90°) |\n\nLone pairs occupy more space than bonding pairs.\n\n📖 *Source: Chapter 4 - Chemical Bonding*", "subj": "Chemistry", "cites": 1},
    {"mode": "socratic", "q": "Why can't we divide by zero?", "r": "Let's reason through this:\n\n🤔 If 6/3 = 2, that means 2 × 3 = 6. Division is inverse multiplication.\n\n🤔 So if 6/0 = x, then x × 0 = 6. But anything × 0 = 0, never 6!\n\n💡 **No number x satisfies x × 0 = 6**, so division by zero is undefined.\n\nFor 0/0, ANY number works (0 × x = 0), so it's *indeterminate*.", "subj": "Mathematics", "cites": 0},
    {"mode": "qa", "q": "Explain scope of variables in Python (LEGB rule)", "r": "## LEGB Rule — Variable Scope in Python\n\nPython searches for variables in this order:\n\n1. **L**ocal — inside the current function\n2. **E**nclosing — in enclosing function (closures)\n3. **G**lobal — module-level variables\n4. **B**uilt-in — Python's built-in names (len, print, etc.)\n\nUse `global` keyword to modify global variables from inside a function.\n\n📖 *Source: Chapter 7 - Functions*", "subj": "Computer Science", "cites": 1},
]


def get_nvidia_embeddings(texts: list[str]) -> list[list[float]]:
    """Call NVIDIA NIM embedding API directly via the openai SDK."""
    try:
        from openai import OpenAI
    except ModuleNotFoundError as exc:
        raise RuntimeError("openai package is required for live embedding generation") from exc

    client = OpenAI(base_url=EMBED_BASE_URL, api_key=EMBED_API_KEY)
    response = client.embeddings.create(
        input=texts, model=EMBED_MODEL, encoding_format="float",
        extra_body={"input_type": "passage", "truncate": "END"},
    )
    return [item.embedding for item in response.data]


PERSONA_AI_HISTORY = {
    "teacher": [
        {"mode": "qa", "q": "Create a remediation plan for projectile motion weak learners", "r": "Use a three-step sequence: recap vectors, guided derivations, then mixed numericals. Close with a 15-minute exit quiz.", "subj": "Physics", "cites": 1},
        {"mode": "study_guide", "q": "Summarize common student errors in thermodynamics", "r": "Students are mixing state functions with path functions and losing sign conventions for work and enthalpy. Re-teach through solved comparisons.", "subj": "Chemistry", "cites": 1},
        {"mode": "quiz", "q": "Generate a quick formative quiz for derivatives", "r": "Five short questions covering power rule, chain rule, and slope interpretation with one application problem.", "subj": "Mathematics", "cites": 1},
        {"mode": "qa", "q": "Draft feedback comments for Python functions lab", "r": "Praise decomposition and naming first, then point to parameter use, return values, and missed edge cases.", "subj": "Computer Science", "cites": 0},
    ],
    "parent": [
        {"mode": "qa", "q": "How should I help with low chemistry confidence at home?", "r": "Keep the support routine light: 20-minute revision blocks, formula recall, then one concept question. Avoid turning the conversation into a marks lecture.", "subj": "Chemistry", "cites": 0},
        {"mode": "qa", "q": "Explain this month's attendance trend in simple words", "r": "Attendance improved after the second week. One absence and two late arrivals are the main reasons the rate is not above 95 percent yet.", "subj": "English", "cites": 0},
        {"mode": "study_guide", "q": "Build a weekend revision plan before exams", "r": "Saturday: Physics and Mathematics practice. Sunday: light English reading, Chemistry flashcards, and one Computer Science recap block.", "subj": "Mathematics", "cites": 0},
    ],
    "admin": [
        {"mode": "qa", "q": "Summarize AI usage spikes across the last week", "r": "Usage spikes came from student quiz generation before tests and teacher grading workflows. Peak load was concentrated between 6 PM and 9 PM IST.", "subj": "Computer Science", "cites": 0},
        {"mode": "qa", "q": "Draft a principal briefing on attendance and fee risk", "r": "Highlight the student risk radar first, then connect attendance recovery actions with pending fee follow-ups. Keep the note actionable and short.", "subj": "English", "cites": 0},
        {"mode": "study_guide", "q": "Prepare an onboarding checklist for the next batch", "r": "Include user activation, class allocation, timetable verification, parent linking, branding check, and WhatsApp communication readiness.", "subj": "Computer Science", "cites": 0},
    ],
}

PERSONA_NOTIFICATION_TEMPLATES = {
    "student": [
        {"category": "assignment", "title": "Assignment feedback posted", "body": "Differentiation assignment feedback is ready in your workspace.", "channel": "in_app", "triggered_by": "teacher"},
        {"category": "review", "title": "Review session due", "body": "Three revision cards are due for Chemistry and Physics today.", "channel": "push", "triggered_by": "system"},
        {"category": "test_reminder", "title": "Mock test this weekend", "body": "JEE Foundation mock test opens on Saturday morning.", "channel": "in_app", "triggered_by": "teacher"},
    ],
    "teacher": [
        {"category": "attendance", "title": "Attendance summary ready", "body": "Class 11 Science attendance sync finished for today's register.", "channel": "in_app", "triggered_by": "system"},
        {"category": "ai_review", "title": "AI grading draft available", "body": "A subjective answer sheet now has proposed marks for review.", "channel": "in_app", "triggered_by": "automation"},
        {"category": "announcement", "title": "Lesson resources indexed", "body": "Uploaded lecture notes are searchable in Discover.", "channel": "email", "triggered_by": "system"},
    ],
    "parent": [
        {"category": "attendance", "title": "Attendance update", "body": "Your child was present for all scheduled classes this week.", "channel": "whatsapp", "triggered_by": "system"},
        {"category": "report", "title": "Monthly progress report", "body": "A new summary report is available with subject-wise highlights.", "channel": "email", "triggered_by": "system"},
        {"category": "homework", "title": "Homework reminder", "body": "Two assignments remain pending for the coming week.", "channel": "whatsapp", "triggered_by": "teacher"},
    ],
    "admin": [
        {"category": "security", "title": "Security digest", "body": "Daily security posture summary has been generated.", "channel": "in_app", "triggered_by": "system"},
        {"category": "queue", "title": "Queue pressure recovered", "body": "AI queue depth returned to the normal operating band.", "channel": "in_app", "triggered_by": "system"},
        {"category": "branding", "title": "Branding review due", "body": "Review tenant brand assets before the new admission cycle.", "channel": "email", "triggered_by": "system"},
    ],
}

PERSONA_AUDIT_TEMPLATES = {
    "student": [
        {"action": "mascot.message", "entity_type": "assistant_session", "metadata": {"surface": "student.assistant", "channel": "web"}},
        {"action": "ai_history.pin", "entity_type": "ai_query", "metadata": {"surface": "student.ai_history"}},
        {"action": "study_path.viewed", "entity_type": "study_path", "metadata": {"surface": "student.tools"}},
    ],
    "teacher": [
        {"action": "teacher.assignment.created", "entity_type": "assignment", "metadata": {"surface": "teacher.assignments"}},
        {"action": "teacher.attendance.marked", "entity_type": "attendance", "metadata": {"surface": "teacher.attendance"}},
        {"action": "teacher.discovery.ingested", "entity_type": "document", "metadata": {"surface": "teacher.discover"}},
    ],
    "parent": [
        {"action": "parent.report.viewed", "entity_type": "report", "metadata": {"surface": "parent.reports"}},
        {"action": "mascot.message", "entity_type": "assistant_session", "metadata": {"surface": "parent.assistant", "channel": "web"}},
        {"action": "parent.attendance.viewed", "entity_type": "attendance", "metadata": {"surface": "parent.attendance"}},
    ],
    "admin": [
        {"action": "branding.updated", "entity_type": "branding", "metadata": {"surface": "admin.branding"}},
        {"action": "feature_flag.toggled", "entity_type": "feature_flag", "metadata": {"surface": "admin.security"}},
        {"action": "webhook.updated", "entity_type": "webhook", "metadata": {"surface": "admin.webhooks"}},
        {"action": "ai_review.completed", "entity_type": "ai_review", "metadata": {"surface": "admin.ai-review"}},
    ],
}


def _history_start(now: datetime, *, days: int = 180) -> date:
    return (now - timedelta(days=days - 1)).date()


def _school_days_between(start: date, end: date) -> list[date]:
    days: list[date] = []
    cursor = start
    while cursor <= end:
        if cursor.weekday() < 6:
            days.append(cursor)
        cursor += timedelta(days=1)
    return days


def _history_timestamp(target_day: date, *, hour: int = 9, minute: int = 0) -> datetime:
    return datetime.combine(target_day, time(hour, minute), tzinfo=UTC)


def _month_start(value: date) -> date:
    return value.replace(day=1)


def cleanup_existing(db):
    """Remove existing Modern Hustlers Academy tenant and all associated data."""
    tenant = db.query(Tenant).filter(Tenant.name == TENANT_NAME).first()
    if not tenant:
        logger.info("No existing tenant found — fresh seed.")
        return
    tid = tenant.id
    logger.info(f"Cleaning up existing tenant {tid}...")
    # Delete in dependency order (children first)
    for model_cls in [
        MockTestAttempt, TestSeries, UsageCounter, AuditLog, NotificationPreference,
        Notification, StudySession, KGRelationship, KGConcept,
        ReviewSchedule, StudyPathPlan, LearnerProfile, TopicMastery,
        GeneratedContent, AIQuery, AIFolder, AssignmentSubmission, Assignment,
        Mark, Exam, Attendance, Lecture, Timetable, SubjectPerformance,
        ParentLink, Document, Notebook, Enrollment, Subject, Class, User, Tenant,
    ]:
        try:
            db.query(model_cls).filter(model_cls.tenant_id == tid).delete()
        except Exception:
            try:
                db.query(model_cls).filter(model_cls.id == tid).delete()
            except Exception:
                pass
    db.flush()
    # Clean FAISS files
    from config import settings
    vs_dir = Path(settings.storage.vector_store_dir).resolve()
    for f in vs_dir.glob(f"tenant_{tid.hex}*"):
        f.unlink(missing_ok=True)
        logger.info(f"  Removed {f.name}")
    logger.info("✓ Cleanup complete")


def seed(skip_embeddings: bool = False):
    logger.info("═" * 60)
    logger.info("  CBSE Class 11 Demo Seeder — Full 20-Model Edition")
    logger.info("═" * 60)

    if not EMBED_API_KEY and not skip_embeddings:
        logger.warning("EMBEDDING_API_KEY not set — seeding with dummy vectors (RAG Q&A will not work).")
        skip_embeddings = True

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    now = datetime.now(UTC)
    history_start = _history_start(now)
    history_days = _school_days_between(history_start, now.date())

    try:
        # ── 0. Cleanup ───────────────────────────────────────────
        cleanup_existing(db)
        db.commit()

        # ── 1. Tenant ────────────────────────────────────────────
        tenant_id = uuid.uuid4()
        db.add(Tenant(id=tenant_id, name=TENANT_NAME, domain="modernhustlers.com",
                       plan_tier="pro", max_students=100, ai_daily_limit=500,
                       primary_color="#4f46e5", secondary_color="#10b981",
                       accent_color="#f59e0b", font_family="Inter", theme_style="modern"))
        db.flush()
        logger.info(f"✓ Tenant created: {tenant_id}")

        # ── 2. Users ─────────────────────────────────────────────
        student_id = uuid.uuid4()
        db.add(User(id=student_id, tenant_id=tenant_id,
                     email=DEMO_STUDENT_EMAIL,
                     full_name="Naren (Demo)", role="student",
                     preferred_locale="en", phone_number="+919800000101",
                     whatsapp_linked=True, last_login=now - timedelta(hours=3)))

        teacher_id = uuid.uuid4()
        db.add(User(id=teacher_id, tenant_id=tenant_id,
                     email=DEMO_TEACHER_EMAIL,
                     full_name="Mr. Sharma", role="teacher",
                     preferred_locale="en", phone_number="+919800000102",
                     whatsapp_linked=True, last_login=now - timedelta(hours=5)))

        admin_id = uuid.uuid4()
        db.add(User(id=admin_id, tenant_id=tenant_id,
                     email=DEMO_ADMIN_EMAIL,
                     full_name="Admin", role="admin",
                     preferred_locale="en", phone_number="+919800000103",
                     whatsapp_linked=False, last_login=now - timedelta(hours=1)))

        parent_id = uuid.uuid4()
        db.add(User(id=parent_id, tenant_id=tenant_id,
                     email=DEMO_PARENT_EMAIL,
                     full_name="Mrs. Sharma (Parent)", role="parent",
                     preferred_locale="en", phone_number="+919800000104",
                     whatsapp_linked=True, last_login=now - timedelta(days=1, hours=2)))
        db.flush()
        logger.info("✓ Users created (student + teacher + admin + parent)")

        # ── 2b. Parent Link ──────────────────────────────────────
        db.add(ParentLink(tenant_id=tenant_id, parent_id=parent_id,
                           child_id=student_id, relationship_type="parent"))
        db.flush()
        logger.info("✓ Parent-student link created")

        for user_id in (student_id, teacher_id, admin_id, parent_id):
            db.add(NotificationPreference(
                tenant_id=tenant_id,
                user_id=user_id,
                whatsapp_enabled=user_id != admin_id,
                sms_enabled=False,
                email_enabled=True,
                push_enabled=user_id != parent_id,
                in_app_enabled=True,
            ))
        db.flush()
        logger.info("✓ Notification preferences created")

        # ── 3. Academic structure ────────────────────────────────
        class_id = uuid.uuid4()
        db.add(Class(id=class_id, tenant_id=tenant_id,
                      name="Class 11 Science (CBSE)", grade_level="11",
                      academic_year="2025-26"))

        subjects = {}
        for subj_name in ["Physics", "Chemistry", "Mathematics", "English", "Computer Science"]:
            sid = uuid.uuid4()
            subjects[subj_name] = sid
            db.add(Subject(id=sid, tenant_id=tenant_id, name=subj_name, class_id=class_id))

        db.flush()
        db.add(Enrollment(tenant_id=tenant_id, student_id=student_id,
                           class_id=class_id, roll_number="101", academic_year="2025-26"))
        db.flush()
        logger.info("✓ Class, 5 subjects, enrollment created")

        # ── 4. Timetable (Mon-Sat) ───────────────────────────────
        schedule = {
            0: [("Physics", "08:00", "08:45"), ("Mathematics", "08:50", "09:35"), ("English", "09:50", "10:35"),
                ("Chemistry", "10:40", "11:25"), ("Computer Science", "11:30", "12:15"), ("Physics", "12:30", "13:15")],
            1: [("Mathematics", "08:00", "08:45"), ("Chemistry", "08:50", "09:35"), ("Computer Science", "09:50", "10:35"),
                ("Physics", "10:40", "11:25"), ("English", "11:30", "12:15"), ("Mathematics", "12:30", "13:15")],
            2: [("Chemistry", "08:00", "08:45"), ("Physics", "08:50", "09:35"), ("Mathematics", "09:50", "10:35"),
                ("English", "10:40", "11:25"), ("Chemistry", "11:30", "12:15"), ("Computer Science", "12:30", "13:15")],
            3: [("Physics", "08:00", "08:45"), ("Computer Science", "08:50", "09:35"), ("Chemistry", "09:50", "10:35"),
                ("Mathematics", "10:40", "11:25"), ("Physics", "11:30", "12:15"), ("English", "12:30", "13:15")],
            4: [("Mathematics", "08:00", "08:45"), ("English", "08:50", "09:35"), ("Physics", "09:50", "10:35"),
                ("Chemistry", "10:40", "11:25"), ("Computer Science", "11:30", "12:15"), ("Mathematics", "12:30", "13:15")],
            5: [("Chemistry", "08:00", "08:45"), ("Physics", "08:50", "09:35"), ("Mathematics", "09:50", "10:35"),
                ("Computer Science", "10:40", "11:25")],
        }
        tt_count = 0
        for dow, periods in schedule.items():
            for subj_name, start, end in periods:
                sh, sm = map(int, start.split(":"))
                eh, em = map(int, end.split(":"))
                db.add(Timetable(tenant_id=tenant_id, class_id=class_id,
                                  subject_id=subjects[subj_name], teacher_id=teacher_id,
                                  day_of_week=dow, start_time=time(sh, sm), end_time=time(eh, em),
                                  room_number=f"Room {random.choice(['101','102','103','Lab-1','Lab-2'])}"))
                tt_count += 1
        db.flush()
        logger.info(f"✓ Timetable: {tt_count} periods seeded")

        # ── 5. Attendance (90 days) ──────────────────────────────
        att_count = 0
        for idx, day_value in enumerate(history_days):
            if idx < 45:
                weights = [84, 11, 5]
            elif idx < 110:
                weights = [88, 8, 4]
            else:
                weights = [91, 5, 4]
            status = random.choices(["present", "absent", "late"], weights=weights)[0]
            db.add(Attendance(
                tenant_id=tenant_id,
                student_id=student_id,
                class_id=class_id,
                date=day_value,
                status=status,
            ))
            att_count += 1
        db.flush()
        logger.info(f"✓ {att_count} attendance records seeded across 6 months")

        # ── 6. Exams & Marks ─────────────────────────────────────
        exam_ids = {}
        exam_plan = [
            ("Diagnostic", history_start + timedelta(days=14)),
            ("Unit Test 1", history_start + timedelta(days=42)),
            ("Mid Term", history_start + timedelta(days=88)),
            ("Unit Test 2", history_start + timedelta(days=126)),
            ("Pre-Board Practice", history_start + timedelta(days=166)),
        ]
        baseline_scores = {
            "Physics": 68,
            "Chemistry": 64,
            "Mathematics": 74,
            "English": 72,
            "Computer Science": 80,
        }
        for subj_name in ["Physics", "Chemistry", "Mathematics", "English", "Computer Science"]:
            for exam_idx, (exam_name, exam_date_obj) in enumerate(exam_plan):
                eid = uuid.uuid4()
                exam_ids[f"{exam_name}-{subj_name}"] = eid
                max_marks = 100 if subj_name != "Computer Science" else 80
                db.add(Exam(id=eid, tenant_id=tenant_id, name=f"{exam_name} - {subj_name}",
                             subject_id=subjects[subj_name], max_marks=max_marks, exam_date=exam_date_obj,
                             created_at=_history_timestamp(exam_date_obj, hour=10)))
                db.flush()
                score_floor = min(max_marks, baseline_scores[subj_name] + exam_idx * 3)
                db.add(Mark(tenant_id=tenant_id, student_id=student_id,
                             exam_id=eid,
                             marks_obtained=min(max_marks, random.randint(score_floor, min(score_floor + 18, max_marks))),
                             created_at=_history_timestamp(exam_date_obj, hour=15)))
        db.flush()
        logger.info("✓ Exams & marks seeded across the full six-month window")

        # ── 7. Lectures ──────────────────────────────────────────
        _ = [
            ("Physics", "Kinematics - Displacement vs Distance", -60),
            ("Physics", "Newton's Laws of Motion - Numericals", -52),
            ("Physics", "Projectile Motion - Derivation of Range", -45),
            ("Chemistry", "IUPAC Nomenclature Basics", -58),
            ("Chemistry", "Chemical Bonding and VSEPR Theory", -40),
            ("Chemistry", "Thermodynamics - Enthalpy Problems", -33),
            ("Mathematics", "Introduction to Limits", -55),
            ("Mathematics", "Differentiation - Power Rule and Chain Rule", -48),
            ("Mathematics", "Trigonometric Identities Revision", -42),
            ("English", "The Portrait of a Lady - Analysis", -50),
            ("English", "We're Not Afraid to Die - Themes", -35),
            ("Computer Science", "Python Basics - Variables and Data Types", -44),
            ("Computer Science", "Control Flow - Loops and Conditions", -38),
            ("Computer Science", "Functions and Scope in Python", -30),
            ("Physics", "Work Energy Theorem - Applications", -25),
        ]
        lecture_topics = {
            "Physics": [
                "Kinematics - Displacement vs Distance",
                "Newton's Laws of Motion - Numericals",
                "Projectile Motion - Derivation of Range",
                "Work Energy Theorem - Applications",
                "Center of Mass - Problem Solving",
                "Units and Measurements - Error Analysis",
            ],
            "Chemistry": [
                "IUPAC Nomenclature Basics",
                "Chemical Bonding and VSEPR Theory",
                "Thermodynamics - Enthalpy Problems",
                "Equilibrium - Le Chatelier Applications",
                "Isomerism - Types and Recognition",
            ],
            "Mathematics": [
                "Introduction to Limits",
                "Differentiation - Power Rule and Chain Rule",
                "Trigonometric Identities Revision",
                "Complex Numbers on the Argand Plane",
                "Sets and Relations - Core Revision",
            ],
            "English": [
                "The Portrait of a Lady - Analysis",
                "We're Not Afraid to Die - Themes",
                "Discovering Tut - Evidence and Tone",
            ],
            "Computer Science": [
                "Python Basics - Variables and Data Types",
                "Control Flow - Loops and Conditions",
                "Functions and Scope in Python",
                "Lists and Comprehensions Lab",
                "String Processing and Formatting",
            ],
        }
        lecture_data = []
        lecture_dates = history_days[::5]
        subject_cycle = list(lecture_topics.keys())
        for idx, lecture_day in enumerate(lecture_dates):
            subject_name = subject_cycle[idx % len(subject_cycle)]
            topic_pool = lecture_topics[subject_name]
            title = topic_pool[(idx // len(subject_cycle)) % len(topic_pool)]
            lecture_data.append((subject_name, title, lecture_day))

        for idx, (subj_name, title, lecture_day) in enumerate(lecture_data):
            db.add(Lecture(tenant_id=tenant_id, subject_id=subjects[subj_name],
                           class_id=class_id, teacher_id=teacher_id, title=title,
                           scheduled_at=_history_timestamp(lecture_day, hour=8 + (idx % 4)),
                           duration_minutes=45 + ((idx % 3) * 5),
                           transcript_ingested=(idx % 3) != 0,
                           created_at=_history_timestamp(lecture_day, hour=7, minute=30)))
        db.flush()
        logger.info(f"✓ {len(lecture_data)} lectures seeded across 6 months")

        # ── 8. Assignments + Submissions ─────────────────────────
        _ = [
            ("Physics", "Numericals on Kinematics Ch.3", -30, 82),
            ("Physics", "Laws of Motion - Worksheet", -15, 88),
            ("Chemistry", "IUPAC Naming Practice Set", -25, 76),
            ("Chemistry", "Thermodynamics Problem Set", -10, 85),
            ("Mathematics", "Limits & Continuity Exercise", -20, 91),
            ("Mathematics", "Differentiation Assignment", -8, None),  # pending
            ("English", "Essay: Portrait of a Lady Character Sketch", -18, 78),
            ("Computer Science", "Python Functions Lab", -12, 90),
            ("Computer Science", "List Comprehension Exercises", -5, None),  # pending
            ("Physics", "Projectile Motion Numericals", -3, None),  # pending
        ]
        assignment_topics = {
            "Physics": ["Numericals on Kinematics", "Laws of Motion Worksheet", "Projectile Motion Practice", "Work-Energy Problem Set"],
            "Chemistry": ["IUPAC Naming Practice Set", "Thermodynamics Problem Set", "Chemical Bonding Worksheet", "Equilibrium Revision Sheet"],
            "Mathematics": ["Limits and Continuity Exercise", "Differentiation Assignment", "Trigonometry Revision", "Complex Numbers Drill"],
            "English": ["Essay: Portrait of a Lady Character Sketch", "Reading Response: Discovering Tut", "Theme Analysis Writing Task"],
            "Computer Science": ["Python Functions Lab", "List Comprehension Exercises", "String Methods Worksheet", "Flow Control Coding Practice"],
        }
        assignment_data = []
        assignment_dates = history_days[::9]
        subject_rotation = list(assignment_topics.keys())
        for idx, assignment_day in enumerate(assignment_dates):
            subject_name = subject_rotation[idx % len(subject_rotation)]
            topic_pool = assignment_topics[subject_name]
            topic_title = topic_pool[(idx // len(subject_rotation)) % len(topic_pool)]
            due = _history_timestamp(assignment_day + timedelta(days=5), hour=18)
            grade = None if assignment_day >= now.date() - timedelta(days=12) and idx % 2 == 0 else random.randint(72, 94)
            assignment_data.append((subject_name, topic_title, due, grade, assignment_day))

        for subj_name, title, due, grade, created_day in assignment_data:
            aid = uuid.uuid4()
            db.add(Assignment(id=aid, tenant_id=tenant_id, subject_id=subjects[subj_name],
                               title=title, description=f"Complete all problems from {title}",
                               due_date=due, created_by=teacher_id,
                               created_at=_history_timestamp(created_day, hour=16)))
            db.flush()
            if grade is not None:
                db.add(AssignmentSubmission(
                    tenant_id=tenant_id, assignment_id=aid, student_id=student_id,
                    submitted_at=due - timedelta(days=1, hours=2), grade=grade,
                    feedback="Good work!" if grade >= 85 else "Review the weak areas."))
        db.flush()
        logger.info(f"✓ {len(assignment_data)} assignments seeded across 6 months")

        # ── 9. SubjectPerformance ────────────────────────────────
        perf_data = {"Physics": (78.5, 92.0), "Chemistry": (74.2, 88.5),
                     "Mathematics": (82.1, 95.0), "English": (76.0, 90.0),
                     "Computer Science": (88.3, 94.0)}
        for subj_name, (avg, att) in perf_data.items():
            db.add(SubjectPerformance(tenant_id=tenant_id, student_id=student_id,
                                      subject_id=subjects[subj_name],
                                      average_score=avg, attendance_rate=att))
        db.flush()
        logger.info("✓ SubjectPerformance seeded")

        student_profile = sync_student_profile_context(
            db=db,
            tenant_id=tenant_id,
            student_id=student_id,
        )
        student_profile.last_computed_at = now
        db.flush()
        logger.info("✓ Unified StudentProfile seeded from live records")

        # ── 10. AI Folders ───────────────────────────────────────
        folders = {}
        for fname, fcolor in [("Exam Prep", "red"), ("Daily Doubts", "yellow"),
                               ("Homework Help", "blue"), ("Revision", "green")]:
            fid = uuid.uuid4()
            folders[fname] = fid
            db.add(AIFolder(id=fid, tenant_id=tenant_id, user_id=student_id,
                             name=fname, color=fcolor))
        db.flush()
        logger.info("✓ AI Folders created")

        # ── 11. Notebooks + NVIDIA Embeddings → FAISS ────────────
        from src.infrastructure.vector_store.vector_store import get_vector_store
        vs = get_vector_store(str(tenant_id))
        total_chunks = 0
        notebook_ids = {}

        for subj_name, nb_data in NOTEBOOKS.items():
            nb_id = uuid.uuid4()
            notebook_ids[subj_name] = nb_id
            db.add(Notebook(id=nb_id, tenant_id=tenant_id, user_id=student_id,
                             name=nb_data["name"], subject=subj_name,
                             color=nb_data["color"], icon=nb_data["icon"], is_active=True))
            db.flush()

            doc_id = uuid.uuid4()
            db.add(Document(id=doc_id, tenant_id=tenant_id, subject_id=subjects[subj_name],
                             uploaded_by=student_id, notebook_id=nb_id,
                             file_name=f"{nb_data['name']}.pdf", file_type="pdf",
                             ingestion_status="completed", chunk_count=len(nb_data["chunks"])))
            db.flush()

            logger.info(f"  → Embedding {len(nb_data['chunks'])} chunks for {subj_name}...")
            if skip_embeddings:
                logger.info(f"  ⏭ Skipping embeddings for {subj_name} (no API key)")
                total_chunks += len(nb_data["chunks"])
            else:
                embeddings = get_nvidia_embeddings(nb_data["chunks"])

                chunks_for_vs = []
                for idx, text in enumerate(nb_data["chunks"]):
                    chunks_for_vs.append({
                        "document_id": str(doc_id), "text": text,
                        "subject_id": str(subjects[subj_name]),
                        "notebook_id": str(nb_id), "chunk_index": idx,
                        "source_file": f"{nb_data['name']}.pdf",
                    })

                vs.add_chunks(chunks_for_vs, embeddings)
                total_chunks += len(chunks_for_vs)
                logger.info(f"  ✓ {subj_name}: {len(chunks_for_vs)} chunks indexed")

        logger.info(f"✓ All notebooks indexed — {total_chunks} total FAISS vectors")

        # ── 12. TopicMastery ─────────────────────────────────────
        mastery_data = [
            ("Physics", "Kinematics", "core", 78, 0.72, 5),
            ("Physics", "Newton's Laws", "core", 85, 0.80, 7),
            ("Physics", "Projectile Motion", "core", 65, 0.55, 3),
            ("Physics", "Work & Energy", "core", 72, 0.65, 4),
            ("Chemistry", "IUPAC Nomenclature", "core", 62, 0.50, 4),
            ("Chemistry", "Chemical Bonding", "core", 75, 0.68, 5),
            ("Chemistry", "Thermodynamics", "core", 58, 0.45, 3),
            ("Chemistry", "Equilibrium", "core", 70, 0.60, 4),
            ("Chemistry", "Isomerism", "core", 55, 0.40, 2),
            ("Mathematics", "Limits", "core", 80, 0.75, 6),
            ("Mathematics", "Derivatives", "core", 73, 0.65, 5),
            ("Mathematics", "Trigonometry", "core", 88, 0.85, 8),
            ("Mathematics", "Sets", "core", 92, 0.90, 9),
            ("Mathematics", "Complex Numbers", "core", 60, 0.48, 3),
            ("English", "Prose Analysis", "core", 76, 0.68, 4),
            ("Computer Science", "Python Basics", "core", 90, 0.88, 7),
            ("Computer Science", "Control Flow", "core", 85, 0.80, 6),
            ("Computer Science", "Functions", "core", 78, 0.70, 5),
            ("Computer Science", "Lists", "core", 82, 0.75, 5),
            ("Computer Science", "Strings", "core", 79, 0.72, 4),
        ]
        for subj, topic, concept, score, conf, evidence in mastery_data:
            db.add(TopicMastery(
                tenant_id=tenant_id, user_id=student_id, subject_id=subjects[subj],
                topic=topic, concept=concept, mastery_score=float(score),
                confidence_score=conf, evidence_count=evidence,
                last_evidence_type=random.choice(["quiz", "qa", "assignment"]),
                last_evidence_score=float(score + random.randint(-5, 5)),
                last_evidence_at=now - timedelta(days=random.randint(1, 30)),
                review_due_at=now + timedelta(days=random.randint(-5, 14)),
            ))
        db.flush()
        logger.info(f"✓ {len(mastery_data)} TopicMastery entries seeded")

        # ── 13. LearnerProfile ───────────────────────────────────
        db.add(LearnerProfile(
            tenant_id=tenant_id, user_id=student_id,
            preferred_language="english", inferred_expertise_level="standard",
            preferred_response_length="default",
            primary_subjects=["Physics", "Mathematics", "Chemistry"],
            engagement_score=0.72, consistency_score=0.68,
            signal_summary={"top_modes": ["qa", "quiz"], "avg_session_min": 22,
                                        "queries_per_week": 8, "strongest_subject": "Mathematics"},
            last_recomputed_at=now - timedelta(hours=6),
        ))
        db.flush()
        logger.info("✓ LearnerProfile seeded")

        study_topics = [
            "Projectile Motion",
            "Thermodynamics",
            "Derivatives",
            "Python Functions",
            "Chemical Bonding",
            "Trigonometric Identities",
        ]
        study_session_count = 0
        for idx, session_day in enumerate(history_days[::3]):
            db.add(StudySession(
                tenant_id=tenant_id,
                user_id=student_id,
                topic=study_topics[idx % len(study_topics)],
                duration_seconds=900 + ((idx % 5) * 420),
                questions_answered=3 + (idx % 6),
                created_at=_history_timestamp(session_day, hour=18 + (idx % 3), minute=15),
                updated_at=_history_timestamp(session_day, hour=18 + (idx % 3), minute=45),
                last_active_at=_history_timestamp(session_day, hour=18 + (idx % 3), minute=45),
            ))
            study_session_count += 1
        db.flush()
        logger.info(f"✓ {study_session_count} study sessions seeded across 6 months")

        # ── 14. StudyPathPlan ────────────────────────────────────
        physics_nb = notebook_ids.get("Physics")
        chem_nb = notebook_ids.get("Chemistry")
        db.add(StudyPathPlan(
            tenant_id=tenant_id, user_id=student_id, notebook_id=physics_nb,
            subject_id=subjects["Physics"], plan_type="remediation",
            focus_topic="Mechanics Mastery", status="active", current_step_index=2,
            items=[
                {"title": "Review Kinematics basics", "type": "review", "done": True},
                {"title": "Solve 10 displacement problems", "type": "practice", "done": True},
                {"title": "Newton's Laws numericals", "type": "practice", "done": False},
                {"title": "Projectile motion derivation", "type": "concept", "done": False},
                {"title": "Full chapter test", "type": "assessment", "done": False},
            ],
            source_context={"trigger": "low_mastery", "score": 65},
        ))
        db.add(StudyPathPlan(
            tenant_id=tenant_id, user_id=student_id, notebook_id=chem_nb,
            subject_id=subjects["Chemistry"], plan_type="remediation",
            focus_topic="Organic Reactions", status="active", current_step_index=0,
            items=[
                {"title": "IUPAC naming rules review", "type": "review", "done": False},
                {"title": "Isomerism types practice", "type": "practice", "done": False},
                {"title": "Reaction mechanisms intro", "type": "concept", "done": False},
                {"title": "Chapter quiz", "type": "assessment", "done": False},
            ],
            source_context={"trigger": "low_mastery", "score": 55},
        ))
        db.flush()
        logger.info("✓ 2 StudyPathPlans seeded")

        # ── 15. ReviewSchedule (Spaced Repetition) ───────────────
        sr_topics = [
            ("Kinematics", "Physics", 7, 3, 2.5), ("Newton's Laws", "Physics", 14, 4, 2.6),
            ("IUPAC Naming", "Chemistry", 1, 1, 2.5), ("Chemical Bonding", "Chemistry", 3, 2, 2.4),
            ("Thermodynamics", "Chemistry", 1, 1, 2.2), ("Limits", "Mathematics", 14, 5, 2.7),
            ("Derivatives", "Mathematics", 7, 3, 2.5), ("Trigonometry", "Mathematics", 30, 6, 2.8),
            ("Python Basics", "Computer Science", 14, 4, 2.6),
            ("Control Flow", "Computer Science", 7, 3, 2.5),
            ("Portrait of a Lady", "English", 3, 2, 2.4),
            ("Equilibrium", "Chemistry", 1, 1, 2.3),
        ]
        for topic, subj, interval, review_ct, ease in sr_topics:
            db.add(ReviewSchedule(
                tenant_id=tenant_id, student_id=student_id,
                subject_id=subjects[subj], topic=topic,
                next_review_at=now + timedelta(days=random.randint(-3, interval)),
                interval_days=interval, ease_factor=ease, review_count=review_ct,
            ))
        db.flush()
        logger.info(f"✓ {len(sr_topics)} ReviewSchedule entries seeded")

        # ── 16. Knowledge Graph ──────────────────────────────────
        kg_concepts = {}
        concept_data = [
            ("Physics", "Force"), ("Physics", "Acceleration"), ("Physics", "Velocity"),
            ("Physics", "Displacement"), ("Physics", "Inertia"), ("Physics", "Kinetic Energy"),
            ("Chemistry", "Covalent Bond"), ("Chemistry", "IUPAC"), ("Chemistry", "Isomerism"),
            ("Chemistry", "Equilibrium"), ("Chemistry", "Enthalpy"),
            ("Mathematics", "Limits"), ("Mathematics", "Derivatives"), ("Mathematics", "Trigonometry"),
            ("Computer Science", "Variables"), ("Computer Science", "Functions"),
        ]
        for subj, cname in concept_data:
            cid = uuid.uuid4()
            kg_concepts[cname] = cid
            nb = notebook_ids.get(subj)
            db.add(KGConcept(id=cid, tenant_id=tenant_id, notebook_id=nb,
                              name=cname, subject_id=subjects[subj],
                              description=f"Core concept: {cname} in {subj}"))
        db.flush()

        kg_rels = [
            ("Velocity", "Displacement", "related"), ("Acceleration", "Velocity", "prerequisite"),
            ("Force", "Acceleration", "prerequisite"), ("Inertia", "Force", "related"),
            ("Kinetic Energy", "Velocity", "prerequisite"), ("Force", "Kinetic Energy", "related"),
            ("Covalent Bond", "IUPAC", "related"), ("Isomerism", "IUPAC", "prerequisite"),
            ("Enthalpy", "Equilibrium", "related"), ("Limits", "Derivatives", "prerequisite"),
            ("Trigonometry", "Derivatives", "related"), ("Variables", "Functions", "prerequisite"),
        ]
        for src, tgt, rel in kg_rels:
            if src in kg_concepts and tgt in kg_concepts:
                db.add(KGRelationship(tenant_id=tenant_id,
                                       source_concept_id=kg_concepts[src],
                                       target_concept_id=kg_concepts[tgt],
                                       relation_type=rel, weight=round(random.uniform(0.6, 1.0), 2)))
        db.flush()
        logger.info(f"✓ KG: {len(concept_data)} concepts, {len(kg_rels)} relationships")

        # ── 17. GeneratedContent ─────────────────────────────────
        gen_content = [
            ("quiz", "Kinematics Quick Quiz", "Physics", {"questions": [
                {"q": "What is displacement?", "options": ["Vector distance", "Scalar distance"], "answer": 0},
                {"q": "SI unit of velocity?", "options": ["m/s", "km/h", "m/s²"], "answer": 0},
            ]}),
            ("flashcard_set", "Newton's Laws Flashcards", "Physics", {"cards": [
                {"front": "First Law", "back": "Law of Inertia"},
                {"front": "F = ?", "back": "ma (mass × acceleration)"},
            ]}),
            ("mind_map", "Organic Chemistry Map", "Chemistry", {"central": "Organic Chemistry", "branches": [
                {"topic": "IUPAC", "children": ["meth-", "eth-", "prop-", "but-"]},
                {"topic": "Functional Groups", "children": ["-ol", "-al", "-one"]},
            ]}),
            ("summary", "Thermodynamics Summary", "Chemistry", {"text": "Key formulas: ΔG = ΔH - TΔS, w = -PΔV. Exothermic ΔH<0, Endothermic ΔH>0."}),
            ("quiz", "Python Data Types Quiz", "Computer Science", {"questions": [
                {"q": "Is list mutable?", "options": ["Yes", "No"], "answer": 0},
                {"q": "type(3.14)?", "options": ["int", "float", "str"], "answer": 1},
            ]}),
            ("flashcard_set", "Trig Identities", "Mathematics", {"cards": [
                {"front": "sin²θ + cos²θ", "back": "1"},
                {"front": "1 + tan²θ", "back": "sec²θ"},
            ]}),
        ]
        for gtype, title, subj, content in gen_content:
            nb = notebook_ids.get(subj)
            if nb:
                db.add(GeneratedContent(
                    tenant_id=tenant_id, notebook_id=nb, user_id=student_id,
                    type=gtype, title=title, content=content,
                    source_query=f"Generate {gtype} for {subj}",
                ))
        db.flush()
        logger.info(f"✓ {len(gen_content)} GeneratedContent items seeded")

        # ── 18. UsageCounter (6-month analytics) ─────────────────
        usage_profiles = {
            student_id: {"metric": "ai_requests", "count_range": (2, 9), "tokens_per_request": (260, 720), "model": "meta/llama-3.1-70b-instruct"},
            teacher_id: {"metric": "teacher_assistant_requests", "count_range": (1, 5), "tokens_per_request": (320, 820), "model": "meta/llama-3.1-70b-instruct"},
            parent_id: {"metric": "parent_assistant_requests", "count_range": (0, 3), "tokens_per_request": (180, 520), "model": "meta/llama-3.1-8b-instruct"},
            admin_id: {"metric": "admin_ai_requests", "count_range": (0, 4), "tokens_per_request": (280, 760), "model": "meta/llama-3.1-70b-instruct"},
        }
        uc_count = 0
        month_rollups: dict[tuple[uuid.UUID, str, date], dict[str, float]] = {}
        tenant_day_rollups: dict[date, dict[str, float]] = {}
        tenant_month_rollups: dict[date, dict[str, float]] = {}
        for bucket_day in history_days:
            for user_id, profile in usage_profiles.items():
                min_count, max_count = profile["count_range"]
                count = random.randint(min_count, max_count)
                if count <= 0:
                    continue
                tokens = sum(random.randint(*profile["tokens_per_request"]) for _ in range(count))
                cache_hits = min(count, random.randint(0, max(1, count // 2)))
                cost_units = round(tokens * 0.00002, 4)
                db.add(UsageCounter(
                    tenant_id=tenant_id, user_id=user_id, scope="user",
                    metric=profile["metric"], bucket_type="day", bucket_start=bucket_day,
                    count=count, token_total=tokens, cache_hits=cache_hits,
                    estimated_cost_units=cost_units, last_model=profile["model"],
                ))
                uc_count += 1

                month_key = (user_id, profile["metric"], _month_start(bucket_day))
                month_rollups.setdefault(month_key, {"count": 0, "tokens": 0, "cache_hits": 0, "cost_units": 0.0})
                month_rollups[month_key]["count"] += count
                month_rollups[month_key]["tokens"] += tokens
                month_rollups[month_key]["cache_hits"] += cache_hits
                month_rollups[month_key]["cost_units"] += cost_units

                tenant_day_rollups.setdefault(bucket_day, {"count": 0, "tokens": 0, "cache_hits": 0, "cost_units": 0.0})
                tenant_day_rollups[bucket_day]["count"] += count
                tenant_day_rollups[bucket_day]["tokens"] += tokens
                tenant_day_rollups[bucket_day]["cache_hits"] += cache_hits
                tenant_day_rollups[bucket_day]["cost_units"] += cost_units

                tenant_month = _month_start(bucket_day)
                tenant_month_rollups.setdefault(tenant_month, {"count": 0, "tokens": 0, "cache_hits": 0, "cost_units": 0.0})
                tenant_month_rollups[tenant_month]["count"] += count
                tenant_month_rollups[tenant_month]["tokens"] += tokens
                tenant_month_rollups[tenant_month]["cache_hits"] += cache_hits
                tenant_month_rollups[tenant_month]["cost_units"] += cost_units
        for (user_id, metric, bucket_start), totals in month_rollups.items():
            db.add(UsageCounter(
                tenant_id=tenant_id, user_id=user_id, scope="user",
                metric=metric, bucket_type="month", bucket_start=bucket_start,
                count=int(totals["count"]), token_total=int(totals["tokens"]),
                cache_hits=int(totals["cache_hits"]),
                estimated_cost_units=round(float(totals["cost_units"]), 4),
                last_model=usage_profiles[user_id]["model"],
            ))
            uc_count += 1

        for bucket_day, totals in tenant_day_rollups.items():
            db.add(UsageCounter(
                tenant_id=tenant_id, user_id=None, scope="tenant",
                metric="ai_requests", bucket_type="day", bucket_start=bucket_day,
                count=int(totals["count"]), token_total=int(totals["tokens"]),
                cache_hits=int(totals["cache_hits"]),
                estimated_cost_units=round(float(totals["cost_units"]), 4),
                last_model="meta/llama-3.1-70b-instruct",
            ))
            uc_count += 1

        for bucket_month, totals in tenant_month_rollups.items():
            db.add(UsageCounter(
                tenant_id=tenant_id, user_id=None, scope="tenant",
                metric="ai_requests", bucket_type="month", bucket_start=bucket_month,
                count=int(totals["count"]), token_total=int(totals["tokens"]),
                cache_hits=int(totals["cache_hits"]),
                estimated_cost_units=round(float(totals["cost_units"]), 4),
                last_model="meta/llama-3.1-70b-instruct",
            ))
            uc_count += 1
        db.flush()
        logger.info(f"✓ {uc_count} UsageCounter entries seeded for all personas")

        # ── 19. TestSeries + MockTestAttempts ────────────────────
        ts1_id = uuid.uuid4()
        db.add(TestSeries(id=ts1_id, tenant_id=tenant_id, name="CBSE Midterm Practice",
                           description="Practice tests for midterm exams",
                           class_id=class_id, total_marks=100, duration_minutes=90,
                           is_active=True, created_by=teacher_id))
        ts2_id = uuid.uuid4()
        db.add(TestSeries(id=ts2_id, tenant_id=tenant_id, name="JEE Foundation Series",
                           description="JEE preparation mock tests",
                           subject_id=subjects["Physics"], class_id=class_id,
                           total_marks=120, duration_minutes=60,
                           is_active=True, created_by=teacher_id))
        db.flush()

        for ts_id, total in [(ts1_id, 100), (ts2_id, 120)]:
            for attempt_num in range(random.randint(3, 5)):
                db.add(MockTestAttempt(
                    tenant_id=tenant_id, test_series_id=ts_id, student_id=student_id,
                    marks_obtained=round(random.uniform(total * 0.55, total * 0.88), 1),
                    total_marks=float(total),
                    time_taken_minutes=random.randint(40, 85),
                    percentile=round(random.uniform(60, 92), 1),
                    rank=random.randint(5, 45),
                ))
        db.flush()
        logger.info("✓ TestSeries + MockTestAttempts seeded")

        # ── 20. 6-Month AI Query History ─────────────────────────
        folder_keys = list(folders.keys())
        query_count = 0
        for i in range(len(AI_HISTORY) * 3):  # ~54 queries
            template = AI_HISTORY[i % len(AI_HISTORY)]
            days_ago = random.randint(0, 180)
            q_date = now - timedelta(days=days_ago, hours=random.randint(8, 22),
                                      minutes=random.randint(0, 59))
            folder_id = random.choice([None, None, folders[random.choice(folder_keys)]])

            nb = notebook_ids.get(template["subj"])
            db.add(AIQuery(
                id=uuid.uuid4(), tenant_id=tenant_id, user_id=student_id,
                folder_id=folder_id, notebook_id=nb,
                mode=template["mode"], query_text=template["q"],
                response_text=template["r"],
                title=f"{template['mode'].replace('_', ' ').title()} — {template['subj']}",
                token_usage=random.randint(200, 900),
                citation_count=template.get("cites", 0),
                is_pinned=random.random() < 0.15, created_at=q_date,
            ))
            query_count += 1

        persona_users = {
            "student": student_id,
            "teacher": teacher_id,
            "parent": parent_id,
            "admin": admin_id,
        }
        for role, templates in PERSONA_AI_HISTORY.items():
            user_id = persona_users[role]
            for idx, query_day in enumerate(history_days[::14]):
                template = templates[idx % len(templates)]
                nb = notebook_ids.get(template["subj"])
                db.add(AIQuery(
                    id=uuid.uuid4(), tenant_id=tenant_id, user_id=user_id,
                    folder_id=None, notebook_id=nb,
                    mode=template["mode"], query_text=template["q"],
                    response_text=template["r"],
                    title=f"{role.title()} {template['mode'].replace('_', ' ').title()} - {template['subj']}",
                    token_usage=random.randint(180, 760),
                    citation_count=template.get("cites", 0),
                    is_pinned=idx % 7 == 0,
                    created_at=_history_timestamp(query_day, hour=9 + (idx % 8), minute=(idx * 7) % 60),
                ))
                query_count += 1

        notification_count = 0
        for role, templates in PERSONA_NOTIFICATION_TEMPLATES.items():
            user_id = persona_users[role]
            for idx, notify_day in enumerate(history_days[::18]):
                template = templates[idx % len(templates)]
                created_at = _history_timestamp(notify_day, hour=8 + (idx % 9), minute=(idx * 11) % 60)
                was_read = role != "admin" or idx < len(history_days[::18]) - 2
                db.add(Notification(
                    tenant_id=tenant_id,
                    user_id=user_id,
                    recipient_role=role,
                    recipient_channel=template["channel"],
                    category=template["category"],
                    title=template["title"],
                    body=template["body"],
                    body_locale="en",
                    read=was_read,
                    status="delivered" if was_read else "sent",
                    sent_at=created_at,
                    delivered_at=created_at + timedelta(minutes=3),
                    read_at=(created_at + timedelta(hours=4)) if was_read else None,
                    triggered_by=template["triggered_by"],
                    triggered_by_user_id=teacher_id if template["triggered_by"] == "teacher" else None,
                    related_entity_type=template["category"],
                    created_at=created_at,
                    updated_at=created_at + timedelta(minutes=5),
                ))
                notification_count += 1

        audit_count = 0
        for role, templates in PERSONA_AUDIT_TEMPLATES.items():
            user_id = persona_users[role]
            for idx, audit_day in enumerate(history_days[::15]):
                template = templates[idx % len(templates)]
                audit_time = _history_timestamp(audit_day, hour=7 + (idx % 10), minute=(idx * 13) % 60)
                db.add(AuditLog(
                    tenant_id=tenant_id,
                    user_id=user_id,
                    action=template["action"],
                    entity_type=template["entity_type"],
                    entity_id=None,
                    metadata_=template["metadata"],
                    ip_address=f"10.0.0.{10 + (idx % 40)}",
                    created_at=audit_time,
                ))
                audit_count += 1

        db.flush()
        logger.info(f"✓ {query_count} AI history entries over 6 months")
        logger.info(f"✓ {notification_count} notifications seeded across student, teacher, parent, and admin")
        logger.info(f"✓ {audit_count} audit events seeded across student, teacher, parent, and admin")

        # ── Commit ───────────────────────────────────────────────
        db.commit()
        logger.info("═" * 60)
        logger.info("  🎉 FULL 20-MODEL SEEDING COMPLETE!")
        logger.info("  Student login: {}", DEMO_STUDENT_EMAIL)
        logger.info("  Teacher login: {}", DEMO_TEACHER_EMAIL)
        logger.info("  Admin login:   {}", DEMO_ADMIN_EMAIL)
        logger.info("  Parent login:  {}", DEMO_PARENT_EMAIL)
        logger.info(f"  Tenant ID:     {tenant_id}")
        logger.info(f"  FAISS chunks:  {total_chunks}")
        logger.info("═" * 60)

    except Exception as e:
        db.rollback()
        logger.error(f"Seeding failed: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()


def seed_demo_data(*, skip_embeddings: bool = True) -> bool:
    """Canonical programmatic entrypoint for the demo showcase dataset."""
    seed(skip_embeddings=skip_embeddings)
    return True


if __name__ == "__main__":
    seed()
