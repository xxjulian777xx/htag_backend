from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Article(Base):
    __tablename__ = "articulos"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    title: Mapped[str] = mapped_column(
        String(300),
        nullable=False,
    )

    slug: Mapped[str] = mapped_column(
        String(350),
        unique=True,
        nullable=False,
        index=True,
    )

    excerpt: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="draft",
        index=True,
    )

    author_id: Mapped[int | None] = mapped_column(
        ForeignKey("usuarios.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("categorias.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    cover_media_id: Mapped[int | None] = mapped_column(
        ForeignKey("media.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    scheduled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )

    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )

    is_featured: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    allow_comments: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    seo_title: Mapped[str | None] = mapped_column(
        String(300),
        nullable=True,
    )

    seo_description: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
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

    author = relationship(
        "User",
        foreign_keys=[author_id],
    )

    category = relationship(
        "Category",
        back_populates="articles",
    )

    cover_media = relationship(
        "Media",
        back_populates="articles_as_cover",
        foreign_keys=[cover_media_id],
    )

    blocks = relationship(
        "ArticleBlock",
        back_populates="article",
        cascade="all, delete-orphan",
        order_by="ArticleBlock.position",
    )

    tags = relationship(
        "Tag",
        secondary="articulos_tags",
        back_populates="articles",
    )
    history = relationship(
        "ArticleHistory",
        back_populates="article",
        cascade="all, delete-orphan",
        order_by="ArticleHistory.created_at.desc()",
    )

    favorites = relationship(
        "Favorite",
        back_populates="article",
        cascade="all, delete-orphan",
    )