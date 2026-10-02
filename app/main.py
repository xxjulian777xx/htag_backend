from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.users import router as users_router
from app.api.routes.roles import router as roles_router
from app.api.routes.auth import router as auth_router
from app.api.routes.categories import router as categories_router
from app.api.routes.tags import router as tags_router
from app.api.routes.articles import router as articles_router
from app.api.routes.media import router as media_router
from app.api.routes.ocr import router as ocr_router
from app.api.routes.notifications import router as notifications_router
from app.api.routes.public import router as public_router
from app.api.routes.reader_preferences import (
    router as reader_preferences_router,
)
from app.api.routes.favorites import router as favorites_router
from app.api.routes.reader_notifications import (
    router as reader_notifications_router,
)
from app.api.routes.fcm import router as fcm_router


from app.core.config import settings
from app.core.database import Base, engine

from app.models import (
    Permission,
    Role,
    RolePermission,
    Session,
    User,
    UserRole,
    Category,
    Tag,
    Article,
    ArticleBlock,
    ArticleTag,
    Media,
    OCRDocument,
    ArticleHistory,
    ReaderPreference,
    Favorite,
)


@asynccontextmanager
async def lifespan(app: FastAPI):

    Base.metadata.create_all(bind=engine)

    yield


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    lifespan=lifespan,
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# ROUTES
# ============================================================

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(roles_router)
app.include_router(categories_router)
app.include_router(tags_router)
app.include_router(articles_router)
app.include_router(media_router)
app.include_router(ocr_router)
app.include_router(notifications_router)
app.include_router(public_router)
app.include_router(reader_preferences_router)
app.include_router(favorites_router)
app.include_router(reader_notifications_router)
app.include_router(fcm_router)


# ============================================================
# HEALTH
# ============================================================

@app.get("/v1/health")
def health():

    return {
        "status": "ok",
        "service": settings.app_name,
        "environment": settings.app_env,
    }