from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ArticleBlock(Base):
    __tablename__ = "articulo_bloques"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    article_id: Mapped[int] = mapped_column(
        ForeignKey("articulos.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    block_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    position: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    data: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    article = relationship(
        "Article",
        back_populates="blocks",
    )