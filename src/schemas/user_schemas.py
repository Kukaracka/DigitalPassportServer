from typing import Optional
from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
)


class UserSchema(BaseModel):
    username: str = Field(max_length=20, min_length=5)

    class Config:
        from_attributes = True


class DeleteUserRequest(BaseModel):
    password: str


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


class UserReadSchema(BaseModel):
    id: int
    username: str
    email: EmailStr
    first_name: str
    last_name: str
    father_name: str
    phone_number: str
    avatar: Optional[str] = None
    avatar_url: Optional[str] = None  # Убедитесь, что это поле есть!
    avatar_upload_url: Optional[str] = None  # И это поле есть!
    # Убираем _storage_service из модели полностью!

    # @computed_field
    # @property
    # def avatar_url(self) -> Optional[str]:
    #     """URL для просмотра аватара"""
    #     # Теперь URL формируется на уровне сервиса, а не в модели
    #     return None  # Будет заполнено в сервисе
    #
    # @computed_field
    # @property
    # def avatar_upload_url(self) -> Optional[str]:
    #     """URL для загрузки аватара"""
    #     return None  # Будет заполнено в сервисе

    model_config = ConfigDict(from_attributes=True)


class ChangePasswordSchema(BaseModel):
    old_password: str
    new_password: str

    @field_validator("new_password")
    def password_complexity(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        if len(v) < 8:
            raise ValueError("The password must consist of at least 8 characters")
        return v


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
        json_schema_extra = {"example": {"access_token": "string"}}
