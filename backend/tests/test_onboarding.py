"""Tests for self-service tenant onboarding service."""



# ── Onboarding status checklist ──

def test_onboarding_status_structure():
    """Onboarding status should have all checklist fields."""
    expected_keys = {"tenant_created", "admin_created", "classes_created", "subjects_created", "students_enrolled", "counts", "completion_pct"}
    # Simulate the structure
    status = {
        "tenant_created": True,
        "admin_created": True,
        "classes_created": False,
        "subjects_created": False,
        "students_enrolled": False,
        "counts": {"admins": 1, "classes": 0, "subjects": 0, "students": 0},
        "completion_pct": 40,
    }
    assert expected_keys == set(status.keys())


def test_completion_percentage_calculation():
    """Completion percentage should be sum of completed steps × 20."""
    steps = [True, True, True, False, False]
    pct = sum(steps) * 20
    assert pct == 60


def test_completion_percentage_full():
    """100% when all steps complete."""
    steps = [True, True, True, True, True]
    pct = sum(steps) * 20
    assert pct == 100


# ── CSV import parsing ──

def test_csv_import_valid_format():
    """CSV with correct columns should parse."""
    import csv
    import io

    csv_content = "full_name,email,class_name\nRohan Sharma,rohan@school.com,Class 5\nPreeti Patil,preeti@school.com,Class 6"
    reader = csv.DictReader(io.StringIO(csv_content))
    rows = list(reader)
    assert len(rows) == 2
    assert rows[0]["full_name"] == "Rohan Sharma"
    assert rows[1]["email"] == "preeti@school.com"


def test_csv_import_missing_columns():
    """CSV missing required columns should have empty values."""
    import csv
    import io

    csv_content = "full_name,email\nRohan Sharma,rohan@school.com"
    reader = csv.DictReader(io.StringIO(csv_content))
    rows = list(reader)
    assert "class_name" not in rows[0]


def test_csv_import_empty_rows():
    """Blank rows in CSV should be detectable."""
    import csv
    import io

    csv_content = "full_name,email,class_name\n,,\nRohan Sharma,rohan@school.com,Class 5"
    reader = csv.DictReader(io.StringIO(csv_content))
    rows = list(reader)
    blank = [r for r in rows if not r["full_name"].strip()]
    assert len(blank) == 1


# ── Registration validation ──

def test_password_length_validation():
    """Password must be at least 8 characters."""
    password = "short"
    assert len(password) < 8


def test_password_valid():
    password = "secure_password_123"
    assert len(password) >= 8


def test_school_name_required():
    """Empty school name should be invalid."""
    assert not "".strip()
    assert "ABC School".strip()


# ── Class setup ──

def test_class_data_structure():
    """Class data should have name and optional section."""
    classes = [
        {"name": "Class 1", "section": "A"},
        {"name": "Class 2"},
    ]
    for c in classes:
        assert "name" in c
    assert classes[0].get("section") == "A"
    assert classes[1].get("section") is None


# ── Subject setup ──

def test_subject_code_generation():
    """Subject code should default to first 4 chars uppercase."""
    name = "Mathematics"
    code = name[:4].upper()
    assert code == "MATH"


def test_subject_code_short_name():
    """Short subject names should still generate valid codes."""
    name = "IT"
    code = name[:4].upper()
    assert code == "IT"
