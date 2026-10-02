from sqlalchemy import select

from app.core.database import SessionLocal
from app.models.role import Role
from app.models.user import User


def main():

    db = SessionLocal()

    try:

        user = db.scalar(
            select(User).where(
                User.username == "admin"
            )
        )

        if user is None:
            print("ERROR: El usuario admin no existe.")
            return

        role = db.scalar(
            select(Role).where(
                Role.name == "administrador"
            )
        )

        if role is None:
            print("ERROR: El rol administrador no existe.")
            return

        if role not in user.roles:
            user.roles.append(role)
            db.commit()

            print("Rol administrador asignado correctamente.")

        else:
            print("El usuario admin ya tiene el rol administrador.")

        db.refresh(user)

        print()
        print(f"Usuario: {user.username}")
        print("Roles:")

        for user_role in user.roles:
            print(f"  - {user_role.name}")

    finally:
        db.close()


if __name__ == "__main__":
    main()