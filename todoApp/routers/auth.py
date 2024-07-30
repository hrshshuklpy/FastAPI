from datetime import timedelta, datetime, timezone
from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, Response, Form
from sqlalchemy.orm import Session

from starlette import status
from starlette.responses import RedirectResponse

from ..database import SessionLocal
from ..models import Users
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(
    prefix="/auth",
    tags=['auth']
)

SECRET_KEY = 'b5ad038b0ab9e1947f50e9c6de1359fe8bc6a532ba788879f542df879024b359'
ALGORITHM = 'HS256'

templates = Jinja2Templates(directory="todoApp/templates")

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')


class LoginForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.username: Optional[str] = None
        self.password: Optional[str] = None

    async def create_oauth_form(self):
        form = await self.request.form()
        self.username = form.get("email")
        self.password = form.get("password")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


def authenticate_user(username: str, password: str, db):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user


def create_access_token(username: str, user_id: int, user_role: str, expires_delta: timedelta):
    encode = {'sub': username, 'id': user_id, 'role': user_role}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(request: Request):
    try:
        token = request.cookies.get("access_token")
        if token is None:
            return await logout(request)
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: str = payload.get('id')
        user_role: str = payload.get('role')
        if username is None or user_id is None:
            return await logout(request)
        return {'username': username, 'id': user_id, 'role': user_role}
    except JWTError:
        return await logout(request)
        # raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user')


@router.post("/register", response_class=HTMLResponse)
async def register_user(request: Request, db: db_dependency, email: str = Form(...), username: str = Form(...),
                        firstname: str = Form(...), lastname: str = Form(...), password: str = Form(...),
                        password2: str = Form(...)):

    validation1 = db.query(Users).filter(Users.username == username).first()
    validation2 = db.query(Users).filter(Users.email == email).first()

    if password != password2 or validation2 is not None or validation1 is not None:
        msg = 'Invalid registration request'
        return templates.TemplateResponse('register.html', {'request': request, 'msg': msg})

    user_model = Users()
    user_model.username = username
    user_model.firstname = firstname
    user_model.lastname = lastname
    user_model.email = email
    hash_pass = bcrypt_context.hash(password)
    user_model.hashed_password = hash_pass
    user_model.is_active = True
    user_model.role = 'admin'
    user_model.phone_number = 'null'

    db.add(user_model)
    db.commit()

    msg = "User successfully created"
    return templates.TemplateResponse('login.html', {'request': request, 'msg': msg})


@router.post("/", response_class=HTMLResponse)
async def login(request: Request, db: db_dependency):
    try:
        form = LoginForm(request)
        await form.create_oauth_form()
        response = RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)
        validate_user_cookie = await login_for_access_token(response=response, form_data=form, db=db)

        if not validate_user_cookie:
            msg = "Incorrect Username or Password"
            return templates.TemplateResponse("login.html", {"request": request, "msg": msg})
        return response
    except HTTPException:
        msg = "Unknown Error"
        return templates.TemplateResponse("login.html", {"request": request, "msg": msg})


@router.get('/logout')
async def logout(request: Request):
    msg = 'Logout Successful'
    response = templates.TemplateResponse('login.html', {'request': request, 'msg': msg})
    response.delete_cookie(key='access_token')
    return response


@router.post("/token")
async def login_for_access_token(response: Response, db: db_dependency,
                                 form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        return False
    token = create_access_token(user.username,
                                user.id, user.role,
                                timedelta(minutes=60))
    response.set_cookie(key="access_token", value=token, httponly=True)
    return True


@router.get("/register", response_class=HTMLResponse)
async def register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.get("/", response_class=HTMLResponse)
async def authentication_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})
