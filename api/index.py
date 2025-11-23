from typing import List

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, declarative_base, sessionmaker

DATABASE_URL = "sqlite:///./lms.db"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=False)


class CourseCreate(BaseModel):
    title: str = Field(..., description="Unique course title", min_length=1)
    description: str = Field(..., description="Brief course description", min_length=1)


class CourseRead(CourseCreate):
    id: int

    class Config:
        orm_mode = True


def create_db_tables() -> None:
    Base.metadata.create_all(bind=engine)


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


create_db_tables()
app = FastAPI(title="LMS Backend", version="1.0.0")


@app.get("/health", tags=["health"])
def healthcheck() -> dict:
    return {"status": "ok"}


@app.get("/courses", response_model=List[CourseRead], tags=["courses"])
def list_courses(db: Session = Depends(get_db)):
    return db.query(Course).all()


@app.post("/courses", response_model=CourseRead, status_code=201, tags=["courses"])
def create_course(course: CourseCreate, db: Session = Depends(get_db)):
    new_course = Course(title=course.title, description=course.description)
    db.add(new_course)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail="Course title must be unique") from exc
    db.refresh(new_course)
    return new_course


@app.get("/courses/{course_id}", response_model=CourseRead, tags=["courses"])
def get_course(course_id: int, db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course
