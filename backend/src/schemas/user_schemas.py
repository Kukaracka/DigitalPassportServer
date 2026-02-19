from typing import Optional
from pydantic import BaseModel, EmailStr, Field, computed_field, field_validator
from services.storage_service import StorageService


class UserSchema(BaseModel):
    username: str = Field(max_length=20, min_length=5)

    class Config:
        from_attributes = True


class UserLoginSchema(BaseModel):
    username: str
    password: str


class UserCreateSchema(BaseModel):
    username: str
    password: str
    email: EmailStr
    first_name: str
    last_name: str
    father_name: str

    @field_validator("password")
    def password_complexity(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        if len(v) < 8:
            raise ValueError("The password must consist of at least 8 characters")
        return v


class UserReadSchema(UserSchema):
    def __init__(self):
        self.storage_service = StorageService

    id: int
    username: str
    email: EmailStr
    first_name: str
    last_name: str
    father_name: str
    phone_number: str
    avatar_url: Optional[str] = None

    # computed field — будет включено в сериализацию
    @computed_field
    @property
    def avatar_upload_url(self) -> Optional[str]:
        if self.storage_service:
            return self.storage_service.get_upload_url(f"avatars/{self.id}.png")
        return None

class UserUpdateSchema(BaseModel):
    username: str
    email: EmailStr
    first_name: str
    last_name: str
    father_name: str
    phone_number: str


class TokenResponseSchema(BaseModel):
    access_token: str

    class Config:
        schema_extra = {"example": {"access_token": "string"}}
