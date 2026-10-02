from sqlalchemy import select

from app.core.database import Base, SessionLocal, engine
from app.core.security import hash_password
from app.models.user import User


def main():

    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:

        username = "admin"
        email = "monitoresplus@gmail.com"
        password = "M0nit0resPlu$"

        existing_user = db.scalar(
            select(User).where(
                User.username == username
            )
        )

        if existing_user:
            print("El usuario admin ya existe.")
            return

        user = User(
            username=username,
            email=email,
            password_hash=hash_password(password),
            is_active=True,
            token_version=1,
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        print("Usuario creado correctamente.")
        print(f"ID: {user.id}")
        print(f"Username: {user.username}")

    finally:
        db.close()


if __name__ == "__main__":
    main()