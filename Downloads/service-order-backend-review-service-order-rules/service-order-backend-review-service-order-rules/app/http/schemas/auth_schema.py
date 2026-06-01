from pydantic import BaseModel, EmailStr


class UserRegisterSchema(BaseModel):
    email: EmailStr
    password: str
    full_name: str = None


class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str


class TokenSchema(BaseModel):
    access_token: str
    token_type: str = "bearer"


class PasswordRecoveryRequestSchema(BaseModel):
    email: EmailStr


class PasswordRecoveryConfirmSchema(BaseModel):
    email: EmailStr
    code: str
    new_password: str


class UserResponseSchema(BaseModel):
    id: str
    email: str
    full_name: str = None
    role: str

    class Config:
        from_attributes = True


class LoginResponseSchema(BaseModel):
    user: UserResponseSchema
    access_token: str
    token_type: str = "bearer"

