from io import StringIO
from csv import DictReader

from fastapi import APIRouter, UploadFile, status, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import schemas, models
from ..database import get_db
from ..oauth2 import get_current_user
from ..pwutils import encrypt, decrypt

router = APIRouter(
    tags=['Import/Export CSV'],
    prefix='/csv'
)


@router.post('', status_code=status.HTTP_201_CREATED)
async def import_csv(
    upload_file: UploadFile,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    improper_import_exception = HTTPException(
        status.HTTP_400_BAD_REQUEST, detail='Invalid password import')
    if upload_file.filename.endswith('.csv') == False:
        raise improper_import_exception
    contents = await upload_file.read()
    file_obj = StringIO(contents.decode())
    csv_reader = DictReader(file_obj)
    if csv_reader.fieldnames != ['title', 'url', 'login', 'password']:
        raise improper_import_exception
    for row in csv_reader:
        row['login'] = encrypt(row['login'])
        row['password'] = encrypt(row['password'])
        new_entry = models.Password(user_id=current_user.id, **row)
        db.add(new_entry)
    db.commit()
    return {'detail': 'Successfully imported passwords'}
