from models.module import Module
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.sql.visitors import prefix_anon_map
from models.student import Student, StudentGender
from models.subscription import Subscription
from database.connexion import get_db
from middleware.role import RoleChecker
from models.completedTask import CompletedTask
from models.task import Task
from models.user import User
from sqlalchemy import literal
professor_router = APIRouter(
    prefix = "/professors"
)


@professor_router.get("/my-stats")
def get_prof_stats(current_user = Depends(RoleChecker("Professor")), db: Session = Depends(get_db)):
    professor_id = current_user.prof_data.id

    module_count = db.query(Module).filter(Module.professor_id == professor_id).count()
    task_count = db.query(Task).join(Module).filter(Module.professor_id == professor_id).count()
    subscribes_query = db.query(Student).join(Subscription).filter(Subscription.professor_id == professor_id)
    
    total_subs = subscribes_query.count()
    males = subscribes_query.filter(Student.gender == StudentGender.Male.value).count()
    females = subscribes_query.filter(Student.gender == StudentGender.Female.value).count()
    
    tasks = db.query(CompletedTask).join(Task).join(Module).filter(Module.professor_id == professor_id).all()
    total_submissions = len(tasks)
    
    difficulty_counts = {"Easy": 0, "Medium": 0, "Hard": 0}
    hard_comments = []
    
    for task in tasks: 
        status = task.difficulty.value if hasattr(task.difficulty, "value") else task.difficulty
        
        if status in difficulty_counts: 
            difficulty_counts[status] += 1
            
        if status == "Hard" and task.comment: 
            hard_comments.append({
                "student_name": f"{task.student.first_name} {task.student.last_name}",
                "task_title": task.task.title,
                "comment": task.comment,
                "date": task.completed_at
            })
    
    percentages = {
        key: round((value / total_submissions * 100), 2) if total_submissions > 0 else 0 
        for key, value in difficulty_counts.items()
    }

    return {
        "stats": {
            "total_modules": module_count,
            "total_tasks": task_count,
            "total_subs": total_subs,
            "total_genders": {"males": males, "females": females},
            "total_tasks" : task_count,
            "total_submissions": total_submissions,
        },
        "difficulty_analysis": {
            "counts": difficulty_counts,
            "percentages": percentages,
            "hard_comments": hard_comments
        }
    }

@professor_router.get("/student-tracking")
def get_professor_tracking(current_user = Depends(RoleChecker("Professor")), db: Session = Depends(get_db)):
    prof_id = current_user.prof_data.id
    name = (Student.first_name + literal(" ") + Student.last_name).label("student_name")
    gender = (Student.gender).label("student_gender")
    tracking_data = db.query(
        CompletedTask.id,
        CompletedTask.actual_minutes,
        CompletedTask.difficulty,
        CompletedTask.comment,
        CompletedTask.completed_at,
        Task.title.label("task_title"),
        Task.estimated_minutes.label("estimated_minutes"),
        name,gender
    ).join(Task, CompletedTask.task_id == Task.id)\
     .join(Module, Task.module_id == Module.id)\
     .join(Student, CompletedTask.student_id == Student.id)\
     .join(User, Student.user_id == User.id)\
     .filter(Module.professor_id == prof_id)\
     .order_by(CompletedTask.completed_at.desc())\
     .all()

    tracking = []
    for row in tracking_data:
        difficulty = row.difficulty.value if hasattr(row.difficulty, "value") else row.difficulty
        tracking.append({
            "id": row.id,
            "actual_minutes": row.actual_minutes,
            "difficulty": difficulty,
            "comment": row.comment,
            "completed_at": row.completed_at,
            "task_title": row.task_title,
            "estimated_minutes": row.estimated_minutes,
            "student_name": row.student_name,
            "student_gender" : row.student_gender
        })

    total_completed = len(tracking)
    hard_tasks_count = len([t for t in tracking if t["difficulty"] == "Hard"])
    
    return {
        "summary": {
            "total_submissions": total_completed,
            "struggling_students": hard_tasks_count
        },
        "tracking": tracking
    }
