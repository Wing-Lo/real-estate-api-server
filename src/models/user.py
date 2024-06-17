from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Boolean
from marshmallow import fields
from marshmallow.validate import Length
from init import db, ma


class User(db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(200), unique=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(100))
    last_name: Mapped[Optional[str]] = mapped_column(String(100))
    contact_number: Mapped[int] = mapped_column
    password: Mapped[str] = mapped_column(String(200))
    is_admin: Mapped[bool] = mapped_column(Boolean(), server_default="false")


class UserSchema(ma.Schema):
    name = fields.String(required=True)
    email = fields.Email(required=True)
    password = fields.String(required=True, validate=Length(min=8))

    class Meta:
        fields = ('id', 'email', 'first_name', 'last_name', 'contact_number', 'password', 'is_admin')