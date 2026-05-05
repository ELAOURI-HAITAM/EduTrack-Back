from fastapi import FastAPI
from database.connexion import engine, Base
from controllers import authController
import models.user
import models.student
import models.professor
import models.subscription
import models.task
import models.resource
import models.module
from fastapi.middleware.cors import CORSMiddleware
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
   
app.include_router(authController.auth_router)