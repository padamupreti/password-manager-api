from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from .. import schemas, models
from ..database import get_db
from ..hashutils import crypt_context
from ..oauth2 import create_access_token

router = APIRouter(
    tags=['Authentication']
)


@router.post('/login', response_model=schemas.TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user_on_db = db.query(models.User).filter(
        form_data.username == models.User.username).first()
    if not user_on_db:
        raise HTTPException(status.HTTP_403_FORBIDDEN,
                            detail='Invalid credentials')
    verified = crypt_context.verify(form_data.password, user_on_db.password)
    if not verified:
        raise HTTPException(status.HTTP_403_FORBIDDEN,
                            detail='Invalid credentials')
    token = create_access_token({'user_id': user_on_db.id})
    return {'access_token': token, 'token_type': 'bearer'}
