from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, Text, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class OCRDocument(Base):
    __tablename__ = "ocr_documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    media_id: Mapped[int] = mapped_column(
        ForeignKey("media.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="processed",
        index=True,
    )

    extracted_text: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    processed_by: Mapped[int | None] = mapped_column(
        ForeignKey("usuarios.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    processed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    media = relationship(
        "Media",
        foreign_keys=[media_id],
    )

    processed_by_user = relationship(
        "User",
        foreign_keys=[processed_by],
    )