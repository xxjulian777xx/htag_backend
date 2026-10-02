from sqlalchemy import select

from app.core.database import SessionLocal
from app.models.permission import Permission
from app.models.role import Role


PERMISSION_NAME = "articles.archive"

EDITOR_ROLE = "editor"
ADMIN_ROLE = "administrador"


def main() -> None:
    db = SessionLocal()

    try:
        permission = db.execute(
            select(Permission).where(
                Permission.name == PERMISSION_NAME
            )
        ).scalar_one_or_none()

        if permission is None:
            permission = Permission(
                name=PERMISSION_NAME,
                description="Archivar artículos",
            )
            db.add(permission)
            db.flush()

            print(
                f"Permiso creado: {PERMISSION_NAME}"
            )
        else:
            print(
                f"Permiso ya existe: {PERMISSION_NAME}"
            )

        for role_name in [EDITOR_ROLE, ADMIN_ROLE]:
            role = db.execute(
                select(Role).where(
                    Role.name == role_name
                )
            ).scalar_one_or_none()

            if role is None:
                print(
                    f"Rol no encontrado: {role_name}"
                )
                continue

            if permission not in role.permissions:
                role.permissions.append(permission)

                print(
                    f"Permiso asignado a rol: {role_name}"
                )
            else:
                print(
                    f"Permiso ya asignado a rol: {role_name}"
                )

        db.commit()

        print("RBAC actualizado correctamente.")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()