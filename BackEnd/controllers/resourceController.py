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
from models.resource import Resource
from models.subscription import Subscription


resource_router = APIRouter(
    prefix="/resources"
)

@resource_router.post("/upload")
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
        raise HTTPException(status_code=404 , detail="You are not authorized to add resources to this module")
    file_extension = os.path.splitext(file_url.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join("uploads" , unique_filename)

    with open(file_path , "wb") as buffer : 
        shutil.copyfileobj(file_url.file , buffer)


    new_resource = Resource(
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
            user_id = student_user_id,
            title = "New Resource Added",
            message = f"New Assignment Added From {professor_name}"
        )
        db.add(new_notification)
    db.commit()

    return {"message" : "file added successfully " , "resource" : new_resource , "notification" : "notifications sent to students"}

@resource_router.get("/my-resources")
def get_all_assignments(current_user = Depends(RoleChecker("Professor")) , db : Session = Depends(get_db)) : 
    resources = db.query(Resource , Module.title.label("module_title")).join(Module , Resource.module_id == Module.id).filter(Module.professor_id == current_user.prof_data.id).all();
    result = []
    for resource,module_title in resources : 
        result.append({
            "id": resource.id,
            "title": resource.title,
            "task_type": resource.task_type,
            "file_url": resource.file_url,
            "estimated_minutes": resource.estimated_minutes,
            "module_id": resource.module_id,
            "module_title": module_title
        })
    return result

    
@resource_router.get("/{resource_id}")
def get_assignment_details(resource_id : int ,current_user = Depends(RoleChecker("Professor")) , db : Session = Depends(get_db)) : 
    row = db.query(Resource , Module.title.label("module_title")).join(Module , Resource.module_id == Module.id).filter(Module.professor_id == current_user.prof_data.id , Resource.id == resource_id).first()
    if not row: 
        raise HTTPException(status_code=404 , detail="Resource not found ")
    resource, module_title = row
    return {
        "id": resource.id,
        "title": resource.title,
        "task_type": resource.task_type,
        "file_url": resource.file_url,
        "estimated_minutes": resource.estimated_minutes,
        "module_id": resource.module_id,
        "module_title": module_title,
    }

@resource_router.put("/update/{resource_id}")
def update_resource(
    resource_id: int,
    title: str = Form(...),
    task_type: str = Form(...),
    estimated_minutes: int = Form(...),
    file_url: Optional[UploadFile] = File(None), 
    current_user = Depends(RoleChecker("Professor")), 
    db: Session = Depends(get_db)
):
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")

    module = db.query(Module).filter(Module.id == resource.module_id).first()
    if not module or module.professor_id != current_user.prof_data.id:
        raise HTTPException(status_code=403, detail="You are not authorized to update this resource")

    resource.title = title
    resource.task_type = task_type
    resource.estimated_minutes = estimated_minutes

    if file_url and file_url.filename:
        if resource.file_url:
            old_file_path = resource.file_url.lstrip("/") 
            if os.path.exists(old_file_path):
                os.remove(old_file_path)

        file_extension = os.path.splitext(file_url.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        new_file_path = os.path.join("uploads", unique_filename)

        with open(new_file_path, "wb") as buffer:
            shutil.copyfileobj(file_url.file, buffer)
        
        resource.file_url = f"/uploads/{unique_filename}"

    db.commit()
    db.refresh(resource)
    
    return {"message": "Resource updated successfully", "resource": resource}
@resource_router.delete("/remove/{resource_id}")
def remove_resource(resource_id : int ,current_user=Depends(RoleChecker("Professor")) , db : Session=Depends(get_db)):
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not resource : 
        raise HTTPException(status_code=404 , detail="resource not found")

    db.delete(resource)
    db.commit()

    return {"message" : "resource deleted successfully"}