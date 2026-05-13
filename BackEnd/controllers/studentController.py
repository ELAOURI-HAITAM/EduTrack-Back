
from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session
from database.connexion import get_db
from middleware.role import RoleChecker
from models.professor import Professor
from models.subscription import Subscription
from models.module import Module
from models.resource import Resource
from models.task import Task
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
    
    completed_resources = db.query(Task.resource_id).filter(
        Task.student_id == student_id
    ).distinct().count()
    
    subscribed_resources_query = db.query(Resource.id).join(
        Module, Resource.module_id == Module.id
    ).join(
        Subscription, Module.professor_id == Subscription.professor_id
    ).filter(
        Subscription.student_id == student_id
    )
    
    completed_resources_query = db.query(Task.resource_id).filter(
        Task.student_id == student_id
    )
    
    total_resources = subscribed_resources_query.union(completed_resources_query).count()
    
    completion_rate = 0
    if total_resources > 0 :
        completion_rate = round((completed_resources / total_resources) * 100 , 2)
        
    time_data = db.query(
        func.sum(Resource.estimated_minutes), 
        func.sum(Task.actual_minutes)
    ).select_from(Task).join(
        Resource, Task.resource_id == Resource.id
    ).filter(
        Task.student_id == student_id
    ).first()
    
    estimed_sum = time_data[0] or 0
    actual_sum = time_data[1] or 0
    
    return {
        "stats" : {
            "total_profs" : total_profs,
            "total_modules" : total_modules,
            "progress" : {
               "total_resources" : total_resources,
               "completed" : completed_resources,
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