from tempfile import NamedTemporaryFile
from csv import DictReader

from fastapi import APIRouter, UploadFile, status, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from .. import models
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
    real_file_size = 0
    temp = NamedTemporaryFile(delete=False)
    for chunk in upload_file.file:
        real_file_size += len(chunk)
        if real_file_size > 20_000:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Import too large"
            )
        temp.write(chunk)
    temp.close()
    with open(temp.name, 'r') as f:
        csv_reader = DictReader(f)
        if csv_reader.fieldnames != ['title', 'url', 'login', 'password']:
            raise improper_import_exception
        for row in csv_reader:
            row['login'] = encrypt(row['login'])
            row['password'] = encrypt(row['password'])
            new_entry = models.Password(user_id=current_user.id, **row)
            db.add(new_entry)
    db.commit()
    return {'detail': 'Successfully imported passwords'}


@router.get('', response_class=FileResponse)
async def export_csv(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    entries_on_db = db.query(models.Password).filter(
        models.Password.user_id == current_user.id).all()
    if len(entries_on_db) == 0:
        raise HTTPException(status.HTTP_404_NOT_FOUND,
                            detail='No password entries yet')
    temp = NamedTemporaryFile(delete=False)
    temp.write('title,url,login,password\n'.encode())
    for entry in entries_on_db:
        entry.login = decrypt(entry.login)
        entry.password = decrypt(entry.password)
        entry_string = f'{entry.title},{entry.url},{entry.login},{entry.password}\n'
        temp.write(entry_string.encode())
    temp.close()
    return FileResponse(temp.name, filename=f'{current_user.username}_passwords.csv')
