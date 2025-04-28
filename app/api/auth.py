from fastapi import Depends, APIRouter, HTTPException, Response, status

from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta


from app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert

from app.models.user import User
from app.schemas.user import CreateUser
from app.api.dependencies import get_token_from_cookie

from typing import Annotated

from app.config import JWT_SECRET_KEY, JWT_ALGORITHM, JWT_ACCESS_TOKEN_EXPIRE_MINUTES


router = APIRouter(prefix="/auth", tags=["auth"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


async def get_access_token(data: dict):
    to_encode = data.copy()
    expires = datetime.now() + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({'exp': expires})
    encode_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encode_jwt


async def verify_access_token(token: str, credentials_exceptions):
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('user_id')
        if username is None:
            raise credentials_exceptions
        return {'id': user_id, 'username': username}
    except JWTError:
        raise credentials_exceptions


async def get_current_user(token: str = Depends(get_token_from_cookie)):
    credentials_exceptions = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    user_data = await verify_access_token(token, credentials_exceptions)
    return user_data


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_user(db: Annotated[AsyncSession, Depends(get_db)], create_user: CreateUser):
    existing_user = await db.execute(select(User).where(User.username == create_user.username))
    existing_user = existing_user.scalar()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    hashed_password = pwd_context.hash(create_user.password)
    new_user = User(username=create_user.username, hashed_password=hashed_password)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user

@router.post('/login')
async def login(db: Annotated[AsyncSession, Depends(get_db)], username: str, password: str, response: Response):
    user = await db.execute(select(User).where(User.username == username))
    user = user.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    if not await verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    access_token = await get_access_token({'sub': str(user.username), 'user_id': user.id})
    response.set_cookie('token', access_token)
    return {'access_token': access_token, 'token_type': 'Bearer'}


@router.get('/read_current_user')
async def read_current_user(user: User = Depends(get_current_user)):
    return user
