from datetime import datetime

from sqlalchemy import (ForeignKey, String, UniqueConstraint, func,)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from xshared.db import BaseIsActive, SharedBase


class Role(BaseIsActive):
    __tablename__ = "roles"

    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(String(255))

    role_permissions: Mapped[list["RolePermission"]] = relationship(
        back_populates="role", cascade="all, delete-orphan"
    )
    user_company_roles: Mapped[list["UserCompanyRole"]] = relationship(
        back_populates="role"
    )


class Permission(BaseIsActive):
    __tablename__ = "permissions"

    code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(String(255))

    role_permissions: Mapped[list["RolePermission"]] = relationship(
        back_populates="permission", cascade="all, delete-orphan"
    )


class RolePermission(SharedBase):
    __tablename__ = "role_permissions"

    role_id: Mapped[int] = mapped_column(
        ForeignKey("shared.roles.id", ondelete="CASCADE"), primary_key=True
    )
    permission_id: Mapped[int] = mapped_column(
        ForeignKey("shared.permissions.id", ondelete="CASCADE"), primary_key=True
    )

    role: Mapped["Role"] = relationship(back_populates="role_permissions")
    permission: Mapped["Permission"] = relationship(back_populates="role_permissions")


class UserCompanyRole(BaseIsActive):
    __tablename__ = "user_company_roles"
    __table_args__ = (
        UniqueConstraint("user_id", "company_id", name="uq_user_company_role"),
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("shared.users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    company_id: Mapped[int] = mapped_column(
        ForeignKey("shared.companies.id", ondelete="CASCADE"), nullable=False, index=True
    )
    role_id: Mapped[int] = mapped_column(
        ForeignKey("shared.roles.id", ondelete="RESTRICT"), nullable=False, index=True
    )

    user: Mapped["User"] = relationship(foreign_keys=[user_id])
    company: Mapped["Company"] = relationship()
    role: Mapped["Role"] = relationship(back_populates="user_company_roles")
