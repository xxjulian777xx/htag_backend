from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class UserRole(Base):
    __tablename__ = "usuario_roles"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        primary_key=True,
    )

    role_id: Mapped[int] = mapped_column(
        ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
    )