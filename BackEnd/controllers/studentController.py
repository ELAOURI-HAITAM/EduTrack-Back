
from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session
from database.connexion import get_db
from middleware.role import RoleChecker
from models.professor import Professor
from models.subscription import Subscription
from models.module import Module
from models.task import Task
from models.completedTask import CompletedTask
student_router = APIRouter(
    prefix = "/students"
)


@student_router.get("/my-stats")
def get_student_stats(current_user = Depends(RoleChecker("Student")) , db : Session = Depends(get_db)):
    student_id = current_user.student_data.id
    
    total_profs = db.query(Subscription).filter(Subscription.student_id == student_id).count()
    
    total_modules = db.query(Module).join(
        Subscription, Module.professor_id == Subscription.professor_id
    ).filter(Subscription.student_id == student_id).count()
    
    completed_tasks = db.query(CompletedTask.task_id).filter(
        CompletedTask.student_id == student_id
    ).distinct().count()
    
    subscribed_tasks_query = db.query(Task.id).join(
        Module, Task.module_id == Module.id
    ).join(
        Subscription, Module.professor_id == Subscription.professor_id
    ).filter(
        Subscription.student_id == student_id
    )
    
    completed_tasks_query = db.query(CompletedTask.task_id).filter(
        CompletedTask.student_id == student_id
    )
    
    total_tasks = subscribed_tasks_query.union(completed_tasks_query).count()
    
    completion_rate = 0
    if total_tasks > 0 :
        completion_rate = round((completed_tasks / total_tasks) * 100 , 2)
        
    time_data = db.query(
        func.sum(Task.estimated_minutes), 
        func.sum(CompletedTask.actual_minutes)
    ).select_from(CompletedTask).join(
        Task, CompletedTask.task_id == Task.id
    ).filter(
        CompletedTask.student_id == student_id
    ).first()
    
    estimed_sum = time_data[0] or 0
    actual_sum = time_data[1] or 0
    
    return {
        "stats" : {
            "total_profs" : total_profs,
            "total_modules" : total_modules,
            "progress" : {
               "total_tasks" : total_tasks,
               "completed" : completed_tasks,
               "percentage" : completion_rate
            },
            "time_analysis" : {
                "total_estimed" : estimed_sum,
                "total_actual" : actual_sum,
                "diffirence" : actual_sum - estimed_sum
            }
        }
    }


@student_router.get("/all-profs")
def get_all_profs(current_user = Depends(RoleChecker("Student")) , db : Session = Depends(get_db)) :
    professors = db.query(Professor).all()
    return professors