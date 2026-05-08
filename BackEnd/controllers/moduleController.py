from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.connexion import get_db
from middleware.auth import get_current_user
from middleware.role import RoleChecker
from models.module import Module
from validations.moduleSchema import (
    CreateModuleRequest,
    UpdateModuleRequest
)


module_router = APIRouter(
    prefix="/modules",
    tags=["Modules"]
)


@module_router.post("/create")
def create_module(
    request: CreateModuleRequest,
    db: Session = Depends(get_db),
    current_user=Depends(RoleChecker("Professor"))):

    new_module = Module(
        title=request.title,
        description=request.description,
        professor_id=current_user.prof_data.id
    )

    db.add(new_module)
    db.commit()
    db.refresh(new_module)

    return {
        "message": "Module created successfully",
        "module": new_module
    }


@module_router.get("/my-modules")
def get_my_modules(
    db: Session = Depends(get_db),
    current_user=Depends(RoleChecker("Professor"))
):

    modules = db.query(Module).filter(
        Module.professor_id == current_user.prof_data.id
    ).all()

    return modules


@module_router.put("/update/{module_id}")
def update_module(
    module_id: int,
    request: UpdateModuleRequest,
    db: Session = Depends(get_db),
    current_user=Depends(RoleChecker("Professor"))
):

    module = db.query(Module).filter(
        Module.id == module_id,
        Module.professor_id == current_user.prof_data.id
    ).first()

    if not module:
        raise HTTPException(
            status_code=404,
            detail="Module not found"
        )

    if request.title is not None:
        module.title = request.title

    if request.description is not None:
        module.description = request.description

    db.commit()
    db.refresh(module)

    return {
        "message": "Module updated successfully",
        "module": module
    }


@module_router.delete("/delete/{module_id}")
def delete_module(
    module_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(RoleChecker("Professor"))
):

    module = db.query(Module).filter(
        Module.id == module_id,
        Module.professor_id == current_user.prof_data.id
    ).first()

    if not module:
        raise HTTPException(
            status_code=404,
            detail="Module not found"
        )

    db.delete(module)
    db.commit()

    return {
        "message": "Module deleted successfully"
    }