from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import schemas, models
from ..database import get_db
from ..utils import crypt_context
from ..oauth2 import get_current_user

router = APIRouter(
    tags=['Users'],
    prefix='/users'
)


@router.post('', status_code=status.HTTP_201_CREATED, response_model=schemas.UserResponse)
async def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_username_user = db.query(models.User).filter(
        user.username == models.User.username).first()
    if existing_username_user:
        raise HTTPException(status.HTTP_403_FORBIDDEN,
                            detail=f'Username {user.username} is already in use')
    user.password = crypt_context.hash(user.password)
    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.get('/me', response_model=schemas.UserResponse)
async def get_current_user_data(
    current_user: models.User = Depends(get_current_user)
):
    return current_user


@router.put('/me', response_model=schemas.UserResponse)
async def update_current_user_data(
    user: schemas.UserCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    existing_username_user = db.query(models.User).filter(
        user.username == models.User.username).first()
    if existing_username_user and existing_username_user != current_user:
        raise HTTPException(status.HTTP_403_FORBIDDEN,
                            detail=f'Username {user.username} is already in use')
    users_query = db.query(models.User).filter(
        models.User.id == current_user.id)
    user.password = crypt_context.hash(user.password)
    users_query.update(user.dict(), synchronize_session=False)
    db.commit()
    return current_user


@router.delete('/me', status_code=status.HTTP_204_NO_CONTENT)
async def delete_current_user(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    users_query = db.query(models.User).filter(
        models.User.id == current_user.id)
    users_query.delete()
    db.commit()
    return
