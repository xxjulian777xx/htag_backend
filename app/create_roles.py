from sqlalchemy import select

from app.core.database import Base, SessionLocal, engine
from app.models.permission import Permission
from app.models.role import Role


PERMISSIONS = [
    # =========================
    # USUARIOS
    # =========================
    (
        "users.read",
        "Consultar usuarios",
    ),
    (
        "users.create",
        "Crear usuarios",
    ),
    (
        "users.update",
        "Modificar usuarios",
    ),
    (
        "users.disable",
        "Desactivar usuarios",
    ),
    (
        "users.sessions.revoke",
        "Revocar sesiones de otros usuarios",
    ),
    (
        "users.password.reset",
        "Restablecer contraseñas de otros usuarios",
    ),

    # =========================
    # ROLES
    # =========================
    (
        "roles.read",
        "Consultar roles",
    ),
    (
        "roles.manage",
        "Administrar roles y permisos",
    ),

    # =========================
    # ARTICULOS
    # =========================
    (
        "articles.read",
        "Consultar artículos",
    ),
    (
        "articles.create",
        "Crear artículos",
    ),
    (
        "articles.update",
        "Modificar artículos",
    ),
    (
        "articles.delete",
        "Eliminar artículos",
    ),
    (
        "articles.schedule",
        "Programar artículos",
    ),
    (
        "articles.publish",
        "Publicar artículos",
    ),
    (
        "articles.archive",
        "Archivar artículos",
    ),

    # =========================
    # CATEGORIAS
    # =========================
    (
        "categories.read",
        "Consultar categorías",
    ),
    (
        "categories.create",
        "Crear categorías",
    ),
    (
        "categories.update",
        "Modificar categorías",
    ),
    (
        "categories.delete",
        "Eliminar categorías",
    ),

    # =========================
    # TAGS
    # =========================
    (
        "tags.read",
        "Consultar etiquetas",
    ),
    (
        "tags.create",
        "Crear etiquetas",
    ),
    (
        "tags.update",
        "Modificar etiquetas",
    ),
    (
        "tags.delete",
        "Eliminar etiquetas",
    ),

    # =========================
    # MEDIA
    # =========================
    (
        "media.read",
        "Consultar archivos multimedia",
    ),
    (
        "media.upload",
        "Subir archivos multimedia",
    ),
    (
        "media.update",
        "Modificar información de archivos multimedia",
    ),
    (
        "media.delete",
        "Eliminar archivos multimedia",
    ),

    # =========================
    # OCR
    # =========================
    (
        "ocr.read",
        "Consultar procesos OCR",
    ),
    (
        "ocr.process",
        "Procesar documentos mediante OCR",
    ),

    # =========================
    # NOTIFICACIONES
    # =========================
    (
        "notifications.read",
        "Consultar notificaciones",
    ),
    (
        "notifications.manage",
        "Administrar notificaciones",
    ),
]


ROLES = {
    "administrador": {
        "description": "Administrador del sistema",
        "permissions": [
            # Usuarios
            "users.read",
            "users.create",
            "users.update",
            "users.disable",
            "users.sessions.revoke",
            "users.password.reset",

            # Roles
            "roles.read",
            "roles.manage",

            # Artículos
            "articles.read",
            "articles.create",
            "articles.update",
            "articles.delete",
            "articles.schedule",
            "articles.publish",
            "articles.archive",

            # Categorías
            "categories.read",
            "categories.create",
            "categories.update",
            "categories.delete",

            # Tags
            "tags.read",
            "tags.create",
            "tags.update",
            "tags.delete",

            # Media
            "media.read",
            "media.upload",
            "media.update",
            "media.delete",

            # OCR
            "ocr.read",
            "ocr.process",

            # Notificaciones
            "notifications.read",
            "notifications.manage",
        ],
    },

    "editor": {
        "description": "Editor de contenido del blog",
        "permissions": [
            # Artículos
            "articles.read",
            "articles.create",
            "articles.update",
            "articles.delete",
            "articles.schedule",
            "articles.publish",
            "articles.archive",

            # Categorías
            "categories.read",
            "categories.create",
            "categories.update",
            "categories.delete",

            # Tags
            "tags.read",
            "tags.create",
            "tags.update",
            "tags.delete",

            # Media
            "media.read",
            "media.upload",
            "media.update",
            "media.delete",

            # OCR
            "ocr.read",
            "ocr.process",

            # Notificaciones
            "notifications.read",
            "notifications.manage",
        ],
    },
}


def main():
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        permission_objects = {}

        for permission_name, description in PERMISSIONS:
            permission = db.scalar(
                select(Permission).where(
                    Permission.name == permission_name
                )
            )

            if permission is None:
                permission = Permission(
                    name=permission_name,
                    description=description,
                )

                db.add(permission)
                db.flush()

            else:
                permission.description = description

            permission_objects[permission_name] = permission

        for role_name, role_data in ROLES.items():
            role = db.scalar(
                select(Role).where(
                    Role.name == role_name
                )
            )

            if role is None:
                role = Role(
                    name=role_name,
                    description=role_data["description"],
                )

                db.add(role)
                db.flush()

            else:
                role.description = role_data["description"]

            role.permissions = [
                permission_objects[permission_name]
                for permission_name in role_data["permissions"]
            ]

        db.commit()

        print("Roles y permisos creados correctamente.")
        print()

        roles = db.scalars(
            select(Role).order_by(Role.id)
        ).all()

        for role in roles:
            print(f"Rol: {role.name}")
            print(f"Descripción: {role.description}")

            for permission in role.permissions:
                print(f"  - {permission.name}")

            print()

    finally:
        db.close()


if __name__ == "__main__":
    main()