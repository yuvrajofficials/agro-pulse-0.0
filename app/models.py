from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    address: str
    phone: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class PhoneLogin(BaseModel):
    phone: str
    password: str
