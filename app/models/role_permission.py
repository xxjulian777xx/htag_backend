from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class RolePermission(Base):
    __tablename__ = "rol_permisos"

    role_id: Mapped[int] = mapped_column(
        ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
    )

    permission_id: Mapped[int] = mapped_column(
        ForeignKey("permisos.id", ondelete="CASCADE"),
        primary_key=True,
    )