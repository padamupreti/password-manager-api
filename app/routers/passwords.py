from typing import List

from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import schemas, models
from ..database import get_db
from ..oauth2 import get_current_user
from ..pwutils import encrypt, decrypt

router = APIRouter(
    tags=['Passwords'],
    prefix='/passwords'
)


@router.post('', status_code=status.HTTP_201_CREATED, response_model=schemas.PasswordResponse)
async def create_password(
    entry_schema: schemas.PasswordCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    entry_schema.login = encrypt(entry_schema.login)
    entry_schema.password = encrypt(entry_schema.password)
    new_entry = models.Password(user_id=current_user.id, **entry_schema.dict())
    db.add(new_entry)
    db.commit()
    db.refresh(new_entry)
    new_entry.login = decrypt(new_entry.login)
    new_entry.password = decrypt(new_entry.password)
    return new_entry


@router.get('', response_model=List[schemas.PasswordResponse])
async def get_passwords(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    entries_on_db = db.query(models.Password).filter(
        models.Password.user_id == current_user.id).all()
    if len(entries_on_db) == 0:
        raise HTTPException(status.HTTP_404_NOT_FOUND,
                            detail='No password entries yet')
    for entry in entries_on_db:
        entry.login = decrypt(entry.login)
        entry.password = decrypt(entry.password)
    return entries_on_db


@router.put('/{id}', response_model=schemas.PasswordResponse)
async def update_password(
    id: int,
    entry_schema: schemas.PasswordCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    passwords_query = db.query(models.Password).filter(
        models.Password.id == id)
    password_on_db = passwords_query.first()
    if not password_on_db:
        raise HTTPException(status.HTTP_404_NOT_FOUND,
                            detail=f'Password entry with id of {id} was not found')
    if password_on_db.user_id != current_user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN,
                            detail='Not authorized to perform requested action')
    entry_schema.login = encrypt(entry_schema.login)
    entry_schema.password = encrypt(entry_schema.password)
    passwords_query.update(entry_schema.dict(), synchronize_session=False)
    db.commit()
    password_on_db.login = decrypt(password_on_db.login)
    password_on_db.password = decrypt(password_on_db.password)
    return password_on_db


@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_password(
    id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    passwords_query = db.query(models.Password).filter(
        models.Password.id == id)
    password_on_db = passwords_query.first()
    if not password_on_db:
        raise HTTPException(status.HTTP_404_NOT_FOUND,
                            detail=f'Password entry with id of {id} was not found')
    if password_on_db.user_id != current_user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN,
                            detail='Not authorized to perform requested action')
    passwords_query.delete()
    db.commit()
    return
