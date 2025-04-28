from fastapi import APIRouter, Depends, HTTPException, status

from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, delete

from app.database import get_db
from app.models.user import User
from app.models.task import Task
from app.schemas.task import CreateTask, UpdateTask
from app.api.auth import get_current_user


router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get('/')
async def get_tasks(db: Annotated[AsyncSession, Depends(get_db)], user: Annotated[dict, Depends(get_current_user)]):
    tasks = await db.scalar(select(Task).where(Task.user_id == user.get('id')))
    return tasks


@router.post('/')
async def create_task(db: Annotated[AsyncSession, Depends(get_db)], user: Annotated[dict, Depends(get_current_user)], create_task: CreateTask):
    await db.execute(insert(Task).values(title=create_task.title, description=create_task.description, user_id=user.get('id')))
    await db.commit()

    return {'success': True, 'message': 'Task created successfully'}


@router.put('/{task_id}')
async def update_task(task_id: int, update_task: UpdateTask, db: Annotated[AsyncSession, Depends(get_db)], user: Annotated[dict, Depends(get_current_user)]):
    task = await db.scalar(select(Task).where(Task.id == task_id))

    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Task not found')

    if task.user_id == user.get('id'):
        await db.execute(update(Task).where(Task.id == task_id).values(title=update_task.title, description=update_task.description, done=update_task.done,user_id=user.get('id')))
        await db.commit()

        return {'success': True, 'message': 'Task updated successfully'}


@router.delete('/{task_id}')
async def delete_task(task_id: int, db: Annotated[AsyncSession, Depends(get_db)], user: Annotated[dict, Depends(get_current_user)]):
    task = await db.scalar(select(Task).where(Task.id == task_id))

    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Task not found')

    if task.user_id == user.get('id'):
        await db.execute(delete(Task).where(Task.id == task_id))
        await db.commit()

    return {'success': True, 'message': 'Task deleted successfully'}