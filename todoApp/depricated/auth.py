# class CreateUserRequest(BaseModel):
#     username: str
#     email: str
#     first_name: str
#     last_name: str
#     password: str
#     role: str
#     phone_number: int
#
#
# class Token(BaseModel):
#     access_token: str
#     token_type: str


# @router.post("/create/user", status_code=status.HTTP_201_CREATED)
# async def create_user(db: db_dependency, create_user_request: CreateUserRequest):
#     create_user_model = Users(
#         username=create_user_request.username,
#         email=create_user_request.email,
#         firstname=create_user_request.first_name,
#         lastname=create_user_request.last_name,
#         hashed_password=bcrypt_context.hash(create_user_request.password),
#         role=create_user_request.role,
#         is_active=True,
#         phone_number=create_user_request.phone_number
#     )
#     db.add(create_user_model)
#     db.commit()