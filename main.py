from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker

# ------------------- APP SETUP -------------------
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------- DATABASE -------------------
DATABASE_URL = "sqlite:///./school.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Homework(Base):
    __tablename__ = "homework"

    id = Column(Integer, primary_key=True, index=True)
    student_class = Column(Integer)
    subject = Column(String)
    content = Column(String)

Base.metadata.create_all(bind=engine)

# ------------------- MODELS -------------------
class Question(BaseModel):
    question: str
    student_class: int

class HomeworkCreate(BaseModel):
    student_class: int
    subject: str
    content: str

# ------------------- APIs -------------------

@app.get("/")
def home():
    return {"message": "School AI Agent Running 🚀"}


# 👉 Add Homework
@app.post("/add-homework")
def add_homework(hw: HomeworkCreate):
    db = SessionLocal()

    print("Adding homework:", hw.student_class, hw.subject, hw.content)

    new_hw = Homework(
        student_class=hw.student_class,
        subject=hw.subject,
        content=hw.content
    )
    db.add(new_hw)
    db.commit()
    db.close()

    print("Homework added successfully")

    return {"message": "Homework added successfully"}


# 👉 Ask Question
@app.post("/ask")
def ask(q: Question):

    # ✅ Validation
    if not q.question or not q.student_class:
        return {"answer": "Please enter valid class and question"}

    # 📚 Homework logic
    if "homework" in q.question.lower():
        db = SessionLocal()
        data = db.query(Homework).filter(Homework.student_class == q.student_class).all()

        if not data:
            db.close()
            return {"answer": "No homework found for today"}

        result = ""
        for hw in data:
            result += f"{hw.subject}: {hw.content}\n"

        db.close()
        return {"answer": result}

    # 🤖 Free AI
    return {
        "answer": f"""
📘 Topic: {q.question}

👉 Step 1: Understand the concept  
👉 Step 2: Break into smaller parts  
👉 Step 3: Solve step-by-step  

💡 Tip: Practice similar problems.
"""
    }