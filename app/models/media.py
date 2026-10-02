from datetime import datetime, timezone

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Media(Base):
    __tablename__ = "media"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    original_filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    stored_filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )

    storage_path: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    url: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    mime_type: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    size_bytes: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        default=0,
    )

    title: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    alt_text: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    uploaded_by: Mapped[int | None] = mapped_column(
        ForeignKey("usuarios.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    uploaded_by_user = relationship(
        "User",
        foreign_keys=[uploaded_by],
    )

    articles_as_cover = relationship(
        "Article",
        back_populates="cover_media",
        foreign_keys="Article.cover_media_id",
    )