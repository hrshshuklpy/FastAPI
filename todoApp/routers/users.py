from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.params import Form
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import HTMLResponse, RedirectResponse

from ..models import Todos, Users
from ..database import SessionLocal
from .auth import get_current_user, bcrypt_context, logout
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(
    prefix='/user',
    tags=['user']
)

templates = Jinja2Templates(directory="todoApp/templates")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class UserVerification(BaseModel):
    password: str
    new_password: str = Field(min_length=6)


class PhoneNumberVerification(BaseModel):
    old_number: str
    new_number: str


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get('/', status_code=status.HTTP_200_OK)
async def get_user(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User not found')
    return db.query(Users).filter(Users.id == user.get('id')).first()


# change_password(request: Request, user: user_dependency,db: db_dependency, user_verification: UserVerification):

@router.post('/password', response_class=HTMLResponse)
async def change_password(request: Request, db: db_dependency, username: str = Form(...), password: str = Form(...),
                          new_password: str = Form(...)):
    user = db.query(Users).filter(Users.username == username).first()
    if user is None:
        return await logout(request)
    user_model = db.query(Users).filter(Users.id == user.get('id')).first()
    if user_model is None:
        msg = 'Session expired'
        return templates.TemplateResponse('login.html', {'request': request, 'msg': msg})
    if not bcrypt_context.verify(password, user_model.hashed_password):
        msg = 'Password match failed'
        return templates.TemplateResponse('password.html', {'request': request, 'msg': msg})
    user_model.hashed_password = bcrypt_context.hash(new_password)
    db.add(user_model)
    db.commit()
    return RedirectResponse(url='/todos', status_code=status.HTTP_302_FOUND)


@router.put('/phone_number', status_code=status.HTTP_204_NO_CONTENT)
async def change_phone_number(user: user_dependency, db: db_dependency, user_verification: PhoneNumberVerification):
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    user_model = db.query(Users).filter(Users.id == user.get('id')).first()
    if user_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    if not (user_verification.old_number != user_model.phone_number):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Incorrect phone number')
    user_model.phone_number = user_verification.new_number
    db.add(user_model)
    db.commit()


@router.get("/password_change", response_class=HTMLResponse)
async def password_change(request: Request):
    return templates.TemplateResponse("password.html", {"request": request})
