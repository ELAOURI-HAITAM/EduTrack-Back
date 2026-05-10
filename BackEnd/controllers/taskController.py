

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.connexion import get_db
from middleware.role import RoleChecker
from models.module import Module
from models.resource import Resource
from models.subscription import Subscription
from models.task import Task
from validations.taskSchema import TaskRequest


task_router = APIRouter(
    prefix="/tasks"
)


from sqlalchemy.orm import joinedload

@task_router.get("/todo")
def get_student_todo(current_user=Depends(RoleChecker("Student")), db: Session = Depends(get_db)): 
    completed_resources_ids = db.query(Task.resource_id).filter(Task.student_id == current_user.student_data.id).all()
    completed_ids = [res[0] for res in completed_resources_ids]

    query = db.query(Resource).options(joinedload(Resource.module)).join(Module).join(
        Subscription, Module.professor_id == Subscription.professor_id
    ).filter(Subscription.student_id == current_user.student_data.id)

    if completed_ids:
        query = query.filter(~Resource.id.in_(completed_ids))

    todo_resources = query.all()

    return [
        {
            "resource_id": res.id,
            "title": res.title,
            "task_type": res.task_type,
            "estimated_minutes": res.estimated_minutes,
            "file_url": res.file_url,
            "module_id": res.module_id,
            "module_title": res.module.title  
        }
        for res in todo_resources
    ]



@task_router.post("/submit")
def submit_task(request: TaskRequest, current_user = Depends(RoleChecker("Student")), db: Session = Depends(get_db)): 
    resource = db.query(Resource).filter(Resource.id == request.resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    already_done = db.query(Task).filter(
        Task.student_id == current_user.student_data.id, 
        Task.resource_id == request.resource_id
    ).first()

    if already_done: 
        raise HTTPException(status_code=400, detail="Task Already Submitted")

    new_task = Task(
        title=resource.title,
        actual_minutes=request.actual_minutes,
        difficulty=request.difficulty,
        comment=request.comment,
        resource_id=request.resource_id,
        student_id=current_user.student_data.id,
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return {"message": "Great job! Progress saved.", "task": new_task}



@task_router.get("/completed")
def get_completed_tasks(current_user = Depends(RoleChecker("Student")) , db : Session = Depends(get_db)) :
    completed_history = db.query(Task , Resource).join(Resource , Task.resource_id == Resource.id).filter(Task.student_id == current_user.student_data.id).order_by(Task.id.desc()).all()

    return [
        {
            "id": task.id,
            "resource_title": resource.title,
            "file_url": resource.file_url,
            "actual_minutes": task.actual_minutes,
            "difficulty": task.difficulty,
            "comment": task.comment,
            "completed_at": task.completed_at,
            "module_title" : resource.module.title
        }
        for task, resource in completed_history
    ]
