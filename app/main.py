from fastapi import FastAPI

from app.api import auth, task


app = FastAPI()

app.include_router(auth.router)
app.include_router(task.router)