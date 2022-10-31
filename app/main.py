from fastapi import FastAPI

from . import models
from .database import engine
from .routers import users, auth, passwords, import_export

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(users.router)
app.include_router(auth.router)
app.include_router(passwords.router)
app.include_router(import_export.router)


@app.get('/')
async def home():
    return {'detail': 'Hello, World! The Password Manager API is functional'}
