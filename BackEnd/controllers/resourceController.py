import os
import shutil
import uuid
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session
from database.connexion import get_db
from middleware.role import RoleChecker
from models.module import Module
from models.resource import Resource


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
    return {"message" : "file added successfully " , "resource" : new_resource}


@resource_router.delete("/remove/{resource_id}")
def remove_resource(resource_id : int ,current_user=Depends(RoleChecker("Professor")) , db : Session=Depends(get_db)):
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not resource : 
        raise HTTPException(status_code=404 , detail="resource not found")

    db.delete(resource)
    db.commit()

    return {"message" : "resource deleted successfully"}