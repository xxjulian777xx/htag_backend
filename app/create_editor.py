from sqlalchemy import select

from app.core.database import Base, SessionLocal, engine
from app.core.security import hash_password
from app.models.role import Role
from app.models.user import User


def main():

    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:

        username = "editor"
        email = "editor@localhost"
        password = "editor"

        existing_user = db.scalar(
            select(User).where(
                User.username == username
            )
        )

        if existing_user:
            print("El usuario editor ya existe.")
            print(f"ID: {existing_user.id}")
            print(f"Username: {existing_user.username}")
            return

        editor_role = db.scalar(
            select(Role).where(
                Role.name == "editor"
            )
        )

        if editor_role is None:
            print("El rol editor no existe.")
            print("Ejecuta primero:")
            print("python -m app.create_roles")
            return

        user = User(
            username=username,
            email=email,
            password_hash=hash_password(password),
            is_active=True,
            token_version=1,
        )

        user.roles = [editor_role]

        db.add(user)
        db.commit()
        db.refresh(user)

        print("Usuario editor creado correctamente.")
        print(f"ID: {user.id}")
        print(f"Username: {user.username}")
        print(f"Email: {user.email}")
        print(f"Rol: {editor_role.name}")

    finally:
        db.close()


if __name__ == "__main__":
    main()