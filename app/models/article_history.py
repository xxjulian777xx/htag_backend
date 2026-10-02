from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ArticleHistory(Base):
    __tablename__ = "articulos_historial"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    article_id: Mapped[int] = mapped_column(
        ForeignKey(
            "articulos.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    user_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "usuarios.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    actor_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="user",
    )

    action: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        index=True,
    )

    from_status: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    to_status: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )

    article = relationship(
        "Article",
        back_populates="history",
    )

    user = relationship(
        "User",
    )