from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ArticleTag(Base):
    __tablename__ = "articulos_tags"

    article_id: Mapped[int] = mapped_column(
        ForeignKey("articulos.id", ondelete="CASCADE"),
        primary_key=True,
    )

    tag_id: Mapped[int] = mapped_column(
        ForeignKey("tags.id", ondelete="CASCADE"),
        primary_key=True,
    )