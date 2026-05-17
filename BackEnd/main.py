from fastapi import FastAPI
from controllers.notificationController import notification_router
from database.connexion import engine, Base
from controllers import authController
from models import notification
import models.user
import models.student
import models.professor
import models.subscription
import models.completedTask
import models.task
import models.module
import models.notification
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from controllers.moduleController import module_router
from controllers.subscriptionsController import subscription_router
from controllers.professorController import professor_router
from controllers.taskController import task_router
from controllers.studentController import student_router
from controllers.completedTaskController import completed_task_router
from controllers.notificationController import notification_router
from controllers.adminController import admin_router
from controllers.userController import user_router
Base.metadata.create_all(bind=engine)

app = FastAPI()
origins = [
    "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
   
if not os.path.exists("uploads"):
    os.makedirs("uploads")

app.mount("/uploads" , StaticFiles(directory="uploads") , name="uploads")
app.include_router(authController.auth_router)
app.include_router(module_router)
app.include_router(completed_task_router)
app.include_router(subscription_router)
app.include_router(professor_router)
app.include_router(task_router)
app.include_router(student_router)
app.include_router(notification_router)
app.include_router(admin_router)
app.include_router(user_router)