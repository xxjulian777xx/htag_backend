from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    users = relationship(
        "User",
        secondary="usuario_roles",
        back_populates="roles",
    )

    permissions = relationship(
        "Permission",
        secondary="rol_permisos",
        back_populates="roles",
        lazy="selectin",
    )