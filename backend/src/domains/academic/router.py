from fastapi import APIRouter

from .routes import students
from .routes import teacher
from .routes import parent

router = APIRouter()
router.include_router(students.router)
router.include_router(teacher.router)
router.include_router(parent.router)
