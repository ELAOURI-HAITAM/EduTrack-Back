import os
import shutil
from typing import Optional
import uuid
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session
from database.connexion import get_db
from middleware.role import RoleChecker
from models.module import Module
from models.notification import Notification
from models.professor import Professor
from models.student import Student
from models.task import Task
from models.subscription import Subscription


task_router = APIRouter(
    prefix="/tasks"
)

@task_router.post("/upload")
def upload_file(
    title: str = Form(...),
    task_type: str = Form(...),
    estimated_minutes: int = Form(...),
    module_id: int = Form(...),
    file_url: UploadFile = File(...),
    current_user = Depends(RoleChecker("Professor")), 
    db: Session = Depends(get_db)
):
    module = db.query(Module).filter(Module.id == module_id).first()
    if not module : 
        raise HTTPException(status_code=404 , detail="module not found")

    if module.professor_id != current_user.prof_data.id :
        raise HTTPException(status_code=404 , detail="You are not authorized to add tasks to this module")
    file_extension = os.path.splitext(file_url.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join("uploads" , unique_filename)

    with open(file_path , "wb") as buffer : 
        shutil.copyfileobj(file_url.file , buffer)


    new_resource = Task(
        title = title,
        file_url = f"/uploads/{unique_filename}",
        task_type = task_type,
        estimated_minutes = estimated_minutes,
        module_id = module_id
    )
    db.add(new_resource)
    db.commit()
    db.refresh(new_resource)



    subscriptions = db.query(Subscription).filter(Subscription.professor_id == current_user.prof_data.id).all()

    for sub in subscriptions : 
        student_user_id = db.query(Student).filter(Student.id == sub.student_id).first().user_id
        professor_name = f"{sub.professor.first_name} {sub.professor.last_name}"
        new_notification = Notification(
            receiver_id = student_user_id,
            sender_id = current_user.id,
            title = "New Task Added",
            message = f"New Assignment Added From {professor_name}"
        )
        db.add(new_notification)
    db.commit()

    return {"message" : "file added successfully " , "task" : new_resource , "notification" : "notifications sent to students"}

@task_router.get("/my-tasks")
def get_all_assignments(current_user = Depends(RoleChecker("Professor")) , db : Session = Depends(get_db)) : 
    tasks = db.query(Task , Module.title.label("module_title")).join(Module , Task.module_id == Module.id).filter(Module.professor_id == current_user.prof_data.id).all();
    result = []
    for task,module_title in tasks : 
        result.append({
            "id": task.id,
            "title": task.title,
            "task_type": task.task_type,
            "file_url": task.file_url,
            "estimated_minutes": task.estimated_minutes,
            "module_id": task.module_id,
            "module_title": module_title
        })
    return result

    
@task_router.get("/{resource_id}")
def get_assignment_details(resource_id : int ,current_user = Depends(RoleChecker("Professor")) , db : Session = Depends(get_db)) : 
    row = db.query(Task , Module.title.label("module_title")).join(Module , Task.module_id == Module.id).filter(Module.professor_id == current_user.prof_data.id , Task.id == resource_id).first()
    if not row: 
        raise HTTPException(status_code=404 , detail="Task not found ")
    task, module_title = row
    return {
        "id": task.id,
        "title": task.title,
        "task_type": task.task_type,
        "file_url": task.file_url,
        "estimated_minutes": task.estimated_minutes,
        "module_id": task.module_id,
        "module_title": module_title,
    }

@task_router.put("/update/{resource_id}")
def update_resource(
    resource_id: int,
    title: str = Form(...),
    task_type: str = Form(...),
    estimated_minutes: int = Form(...),
    file_url: Optional[UploadFile] = File(None), 
    current_user = Depends(RoleChecker("Professor")), 
    db: Session = Depends(get_db)
):
    task = db.query(Task).filter(Task.id == resource_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    module = db.query(Module).filter(Module.id == task.module_id).first()
    if not module or module.professor_id != current_user.prof_data.id:
        raise HTTPException(status_code=403, detail="You are not authorized to update this task")

    task.title = title
    task.task_type = task_type
    task.estimated_minutes = estimated_minutes

    if file_url and file_url.filename:
        if task.file_url:
            old_file_path = task.file_url.lstrip("/") 
            if os.path.exists(old_file_path):
                os.remove(old_file_path)

        file_extension = os.path.splitext(file_url.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        new_file_path = os.path.join("uploads", unique_filename)

        with open(new_file_path, "wb") as buffer:
            shutil.copyfileobj(file_url.file, buffer)
        
        task.file_url = f"/uploads/{unique_filename}"

    db.commit()
    db.refresh(task)
    
    return {"message": "Task updated successfully", "task": task}
@task_router.delete("/remove/{resource_id}")
def remove_resource(resource_id : int ,current_user=Depends(RoleChecker("Professor")) , db : Session=Depends(get_db)):
    task = db.query(Task).filter(Task.id == resource_id).first()
    if not task : 
        raise HTTPException(status_code=404 , detail="task not found")

    db.delete(task)
    db.commit()

    return {"message" : "task deleted successfully"}