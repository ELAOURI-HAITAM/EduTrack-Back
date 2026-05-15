

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.connexion import get_db
from middleware.role import RoleChecker
from models.module import Module
from models.notification import Notification
from models.professor import Professor
from models.task import Task
from models.subscription import Subscription
from models.completedTask import CompletedTask
from validations.taskSchema import CompleteTaskRequest


completed_task_router = APIRouter(
    prefix="/completed_tasks"
)


from sqlalchemy.orm import joinedload

@completed_task_router.get("/todo")
def get_student_todo(current_user=Depends(RoleChecker("Student")), db: Session = Depends(get_db)): 
    student_id = current_user.student_data.id 
    print("STUDENT ID : ",student_id) 
    
    completed_ids = db.query(CompletedTask.task_id).filter(
        CompletedTask.student_id == student_id,
        CompletedTask.task_id.is_not(None)
    ).all()
    completed_ids_list = [tas[0] for tas in completed_ids if tas[0] is not None]

    query = db.query(Task).join(
        Module, Task.module_id == Module.id 
    ).join(
        Subscription, Module.professor_id == Subscription.professor_id 
    ).filter(
        Subscription.student_id == student_id
    )

    if completed_ids_list:
        query = query.filter(Task.id.notin_(completed_ids_list))

    todo_tasks = query.options(joinedload(Task.module)).distinct().all()

    return [
        {
            "task_id": tas.id,
            "title": tas.title,
            "task_type": tas.task_type.value if tas.task_type else None, 
            "estimated_minutes": tas.estimated_minutes,
            "file_url": tas.file_url,
            "module_id": tas.module_id,
            "module_title": tas.module.title if tas.module else "No Module" 
        }
        for tas in todo_tasks
    ]



@completed_task_router.post("/submit")
def submit_task(request: CompleteTaskRequest, current_user = Depends(RoleChecker("Student")), db: Session = Depends(get_db)): 
    task = db.query(Task).filter(Task.id == request.task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    already_done = db.query(CompletedTask).filter(
        CompletedTask.student_id == current_user.student_data.id, 
        CompletedTask.task_id == request.task_id
    ).first()

    if already_done: 
        raise HTTPException(status_code=400, detail="CompletedTask Already Submitted")

    new_task = CompletedTask(
        title=task.title,
        actual_minutes=request.actual_minutes,
        difficulty=request.difficulty,
        comment=request.comment,
        task_id=request.task_id,
        student_id=current_user.student_data.id,
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    if request.comment : 
        tas = db.query(Task).filter(Task.id == request.task_id).first()
        module = db.query(Module).filter(Module.id == tas.module_id).first()
        professor_user_id = db.query(Professor).filter(Professor.id == module.professor_id).first().user_id
        new_notification = Notification(
            user_id = professor_user_id,
            title = "New Student FeedBack",
            message = f"A Student Left A Comment on : {tas.title}"
        )
        db.add(new_notification)
        db.commit()

    return {"message": "Great job! Progress saved.", "task": new_task , "notification" : "notification send to profs"}



@completed_task_router.get("/completed")
def get_completed_tasks(current_user = Depends(RoleChecker("Student")) , db : Session = Depends(get_db)) :
    completed_history = db.query(CompletedTask , Task).join(Task , CompletedTask.task_id == Task.id).filter(CompletedTask.student_id == current_user.student_data.id).order_by(CompletedTask.id.desc()).all()

    return [
        {
            "id": completed_task.id,
            "task_title": task.title,
            "file_url": task.file_url,
            "actual_minutes": completed_task.actual_minutes,
            "difficulty": completed_task.difficulty,
            "comment": completed_task.comment,
            "completed_at": completed_task.completed_at,
            "module_title" : task.module.title
        }
        for completed_task, task in completed_history
    ]
