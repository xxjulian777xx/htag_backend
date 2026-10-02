from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Favorite(Base):
    __tablename__ = "favoritos_lector"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "article_id",
            name="uq_favoritos_lector_user_article",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey(
            "usuarios.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    article_id: Mapped[int] = mapped_column(
        ForeignKey(
            "articulos.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )

    user = relationship(
        "User",
        back_populates="favorites",
    )

    article = relationship(
        "Article",
        back_populates="favorites",
    )