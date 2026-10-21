from datetime import datetime
from typing import Annotated, Literal
from uuid import UUID

from pydantic import AfterValidator, BaseModel, ConfigDict, EmailStr, Field, field_validator


class ProjectCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    title: str = Field(min_length=1, max_length=120)
    description: str = Field(min_length=1, max_length=10000)
    workspace_id: UUID


class ProjectRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    title: str
    description: str
    status: Literal["created"]
    created_at: datetime
    updated_at: datetime
    workspace_id: UUID
    creator_id: UUID | None


class ProjectUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    title: str = Field(min_length=1, max_length=120)
    description: str = Field(min_length=1, max_length=10000)


class EmailInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    email: EmailStr

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value):
        return value.strip().casefold() if isinstance(value, str) else value


class LoginInput(EmailInput):
    password: str = Field(min_length=1, max_length=128)


def non_blank_password(value: str) -> str:
    if value.isspace():
        raise ValueError("Choose a password with at least one non-whitespace character.")
    return value


# Credential writes (including future change/reset schemas) use this type.
# Login and eligible hash-parameter upgrades must accept existing credentials.
NewPassword = Annotated[
    str, Field(min_length=15, max_length=128), AfterValidator(non_blank_password)
]


class RegisterInput(LoginInput):
    password: NewPassword
    display_name: str = Field(min_length=1, max_length=80)

    @field_validator("display_name")
    @classmethod
    def name_policy(cls, value):
        if not value.strip():
            raise ValueError("Enter a display name.")
        return value.strip()


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    email: str
    display_name: str


class WorkspaceCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    name: str = Field(min_length=1, max_length=100)


class InvitationCreate(EmailInput):
    role: Literal["admin", "member", "viewer"]


class RoleUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    role: Literal["owner", "admin", "member", "viewer"]


class InvitationAccept(BaseModel):
    model_config = ConfigDict(extra="forbid")
    token: str = Field(min_length=32, max_length=128)
