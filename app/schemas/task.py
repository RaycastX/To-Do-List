from pydantic import BaseModel


class CreateTask(BaseModel):
    title: str
    description: str


class UpdateTask(CreateTask):
    done: bool = False