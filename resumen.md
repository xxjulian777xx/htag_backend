# RBAC Blog Informativo

## Arquitectura general

```text
                         RBAC BLOG INFORMATIVO
                                  │
             ┌────────────────────┼────────────────────┐
             │                    │                    │
             ▼                    ▼                    ▼
       APP EDITOR            APP LECTOR            WEB LECTOR
       Flutter               Flutter              Web
             │                    │                    │
             └────────────────────┼────────────────────┘
                                  │
                                  ▼
                         FASTAPI BACKEND
                                  │
        ┌─────────────────────────┼─────────────────────────┐
        │                         │                         │
        ▼                         ▼                         ▼
      AUTH/RBAC              CMS EDITORIAL             READER API
        │                         │                         │
        ├─ Usuarios               ├─ Artículos              ├─ Artículo del día
        ├─ Roles                  ├─ Categorías             ├─ Histórico
        ├─ Permisos              ├─ Tags                   ├─ Búsqueda
        ├─ Sesiones              ├─ Media                  ├─ Categorías
        └─ JWT                   ├─ OCR                    ├─ Tags
                                ├─ Programación            ├─ Favoritos
                                ├─ Publicación             ├─ Notificaciones
                                └─ Historial               └─ Preferencias
                                      │
                                      ▼
                               WORKERS / SERVICIOS
                                      │
                         ┌────────────┴────────────┐
                         ▼                         ▼
                  Publication Worker       Notification Worker
                         │                         │
                         ▼                         ▼
                    Publicación                 FCM
                    automática
                         │
                         ▼
                       MinIO

1. Estado actual del Backend
Autenticación

/v1/auth
│
├── POST /login
├── POST /refresh
├── POST /logout
├── GET  /me
├── POST /logout-all
├── POST /change-password
└── GET  /test-admin

JWT

Login
  │
  ▼
Access Token + Refresh Token
  │
  ├── Access Token
  │      └── API protegida
  │
  └── Refresh Token
         └── Renovación de sesión

El backend ya maneja:

    JWT

    Access Token

    Refresh Token

    Sesiones

    Revocación

    token_version

    Logout individual

    Logout de todas las sesiones

    Cambio de contraseña

    Usuario activo/inactivo

2. RBAC

USUARIO
   │
   ▼
ROLES
   │
   ▼
PERMISOS

Roles actuales

administrador
    │
    └── Todos los permisos

editor
    │
    ├── articles.*
    ├── categories.*
    ├── tags.*
    ├── media.*
    ├── ocr.*
    └── notifications.*

operador
    │
    ├── cameras.read
    ├── cameras.control
    └── configuration.read

    El rol operador pertenece a la arquitectura anterior y se conserva.
    Para el Blog CMS el rol importante actualmente es editor y administrador.

Permisos CMS

articles.read
articles.create
articles.update
articles.delete
articles.schedule
articles.publish
articles.archive

categories.read
categories.create
categories.update
categories.delete

tags.read
tags.create
tags.update
tags.delete

media.read
media.upload
media.update
media.delete

ocr.read
ocr.process

notifications.read
notifications.manage

3. CMS Editorial

                     ARTÍCULO
                        │
          ┌─────────────┼─────────────┐
          ▼             ▼             ▼
       Categoría       Tags          Media
          │             │             │
          └─────────────┼─────────────┘
                        ▼
                      Blocks
                        │
                        ▼
                    Artículo
                        │
            ┌───────────┼───────────┐
            ▼           ▼           ▼
          Draft      Scheduled   Published
                        │
                        ▼
                 Publication Worker
                        │
                        ▼
                   Notification
                        │
                        ▼
                       FCM

4. Estados de un artículo

                 ┌──────────────┐
                 │    DRAFT     │
                 └──────┬───────┘
                        │
              Programar │
                        ▼
                 ┌──────────────┐
                 │  SCHEDULED  │
                 └──────┬───────┘
                        │
                  fecha/hora
                        │
                        ▼
                 ┌──────────────┐
                 │  PUBLISHED   │
                 └──────┬───────┘
                        │
                     archivar
                        │
                        ▼
                 ┌──────────────┐
                 │  ARCHIVED    │
                 └──────────────┘

Estados implementados:

draft
scheduled
published
archived

5. Artículos
Endpoints CMS

/v1/articles
│
├── GET
├── POST
├── GET /{article_id}
├── PUT /{article_id}
├── DELETE /{article_id}
├── POST /{article_id}/schedule
├── POST /{article_id}/publish
├── POST /{article_id}/archive
└── GET /{article_id}/history

Estructura conceptual

Article
│
├── id
├── title
├── slug
├── excerpt
├── status
├── author
├── category
├── cover
├── scheduled_at
├── published_at
├── is_featured
├── allow_comments
├── seo_title
├── seo_description
│
├── blocks[]
│
└── tags[]

6. Editor de contenido

Los artículos utilizan bloques.

ARTICLE
   │
   └── blocks[]
          │
          ├── position
          ├── block_type
          └── data

Ejemplo conceptual:

Artículo
│
├── Block 0
│     └── title
│
├── Block 1
│     └── paragraph
│
├── Block 2
│     └── image
│
├── Block 3
│     └── paragraph
│
└── Block 4
      └── quote

El Frontend debe tratar los bloques como contenido dinámico.
7. Categorías

/v1/categories
│
├── GET
├── POST
├── PUT /{category_id}
└── DELETE /{category_id}

API pública:

/v1/public/categories
/v1/public/categories/{slug}

Actualmente existe:

Noticias
slug: noticias

8. Tags

/v1/tags
│
├── GET
├── POST
├── PUT /{tag_id}
└── DELETE /{tag_id}

API pública:

/v1/public/tags
/v1/public/tags/{slug}

9. Media / imágenes

Flutter Editor
      │
      │ upload
      ▼
   FastAPI
      │
      ▼
    MinIO
      │
      └── storage_path

La base de datos guarda:

Media
│
├── id
├── original_filename
├── stored_filename
├── storage_path
├── url
├── mime_type
├── size_bytes
├── title
├── alt_text
├── description
└── uploaded_by

Importante:

storage_path = ubicación interna en MinIO

url = URL pública que consumirá Flutter/Web

El Backend no debe utilizar su filesystem local como almacenamiento permanente.
10. OCR

Imagen / Documento
        │
        ▼
       OCR
        │
        ▼
Texto extraído
        │
        ▼
Editor de artículo

Endpoints:

/v1/ocr

Permisos:

ocr.read
ocr.process

11. Historial editorial

Cada cambio importante de estado puede quedar registrado.

ARTÍCULO
   │
   ├── create
   ├── update
   ├── schedule
   ├── publish
   └── archive
          │
          ▼
   articulos_historial

Información registrada:

article_id
user_id
actor_type
action
from_status
to_status
created_at

Esto permitirá posteriormente que el App Editor muestre:

Historial del artículo

24/09 10:30  Juan     Creó artículo
24/09 10:45  Juan     Modificó contenido
24/09 11:00  Juan     Programó publicación
24/09 15:00  Sistema  Publicó artículo

12. Publication Worker

Ya existe.

              SCHEDULED ARTICLE
                      │
                      ▼
             Publication Worker
                      │
             scheduled_at <= NOW
                      │
                      ▼
                 PUBLISHED
                      │
             ┌────────┴────────┐
             ▼                 ▼
       Public API          Notificación
                               │
                               ▼
                              FCM

El Worker revisa periódicamente los artículos programados.

Configuración:

PUBLICATION_WORKER_INTERVAL

Valor actual por defecto:

30 segundos

13. Reader API pública

Esta es la parte MÁS IMPORTANTE para Flutter Lector.

/v1/public
│
├── /articles
│
├── /articles/today
│
├── /articles/{slug}
│
├── /categories
│
├── /categories/{slug}
│
├── /tags
│
├── /tags/{slug}
│
└── /search

14. Lista de artículos

GET /v1/public/articles

Parámetros:

page
page_size
category_id
tag_id

Ejemplo:

/v1/public/articles?page=1&page_size=20

Respuesta conceptual:

{
    items: [],
    total: 10,
    page: 1,
    page_size: 20,
    pages: 1
}

La lista devuelve:

id
title
slug
excerpt
published_at
category
cover
tags

No devuelve los bloques completos.

Esto está pensado para:

HOME
HISTÓRICO
CATEGORÍA
LISTADOS

15. Artículo del día

GET /v1/public/articles/today

Obtiene el artículo publicado marcado como:

is_featured = true

Orden:

published_at DESC
id DESC

El Front puede utilizarlo para:

┌───────────────────────────────┐
│       ARTÍCULO DEL DÍA        │
│                               │
│       Imagen                  │
│       Título                  │
│       Extracto                │
│       Categoría               │
│       Fecha                   │
│                               │
│       LEER ARTÍCULO           │
└───────────────────────────────┘

16. Artículo completo

GET /v1/public/articles/{slug}

Ejemplo:

/v1/public/articles/primera-noticia-rbac-blog

Devuelve:

Artículo
│
├── información general
├── category
├── cover
├── tags
└── blocks[]

Esto alimentará directamente la pantalla:

LECTURA DEL ARTÍCULO

17. Búsqueda

GET /v1/public/search?q=texto

La búsqueda contempla:

Título
Slug
Extracto
SEO title
SEO description
Contenido de bloques
Categoría
Tags

Frontend:

┌──────────────────────────────┐
│ 🔎 Buscar                   │
└──────────────────────────────┘
              │
              ▼
       Resultados
              │
              ├── Artículo
              ├── Artículo
              └── Artículo

18. Favoritos

API para el lector autenticado:

/v1/reader/favorites

Funciones:

GET     favoritos
POST    agregar favorito
DELETE  eliminar favorito

Reglas actuales:

Solo artículos publicados
Un artículo no puede estar dos veces
El favorito pertenece al usuario

Flutter utilizará esto para:

♡ No favorito

♥ Favorito

19. Preferencias del lector

API:

/v1/reader/preferences

Preferencias actuales:

font_size
theme
voice_enabled

Valores:

font_size:
    small
    medium
    large
    xlarge

theme:
    light
    dark
    system

voice_enabled:
    true / false

Esto alimentará:

Configuración del lector
│
├── Tamaño de texto
├── Tema
└── Lectura por voz

20. Notificaciones internas

API:

/v1/reader/notifications
│
├── GET / 
├── GET /{notification_id}
├── PUT /{notification_id}/read
└── DELETE /{notification_id}

Actualmente existe:

notificaciones

Esta tabla representa el:

INBOX INTERNO DE LA APP

No debe confundirse con FCM.
21. FCM

Pendiente de integración final.

Arquitectura prevista:

                 PUBLICACIÓN
                      │
                      ▼
               Notification Event
                      │
                      ▼
              Notification Worker
                      │
                      ▼
                    FCM
                      │
          ┌───────────┼───────────┐
          ▼           ▼           ▼
       Android     Android      Web/etc.
        móvil       móvil
          │           │
          └───────────┴───────────┘
                      │
                      ▼
                Flutter Lector

Payload previsto:

{
    "type": "new_article",
    "article_id": "2",
    "slug": "primera-noticia-del-rbac-blog"
}

La aplicación Flutter podrá recibir:

Nuevo artículo
      │
      ▼
Usuario toca notificación
      │
      ▼
Flutter obtiene slug
      │
      ▼
GET /v1/public/articles/{slug}
      │
      ▼
Pantalla del artículo

22. Flutter Editor

El App Editor deberá consumir principalmente:

/v1/auth
/v1/articles
/v1/categories
/v1/tags
/v1/media
/v1/ocr
/v1/notifications

Pantallas previstas

LOGIN
  │
  ▼
DASHBOARD
  │
  ├── Calendario
  │
  ├── Artículos
  │     ├── Crear
  │     ├── Editar
  │     ├── Programar
  │     ├── Publicar
  │     ├── Archivar
  │     └── Historial
  │
  ├── Categorías
  │
  ├── Tags
  │
  ├── Media
  │
  ├── OCR
  │
  └── Administración

23. Flutter Lector

El App Lector deberá consumir principalmente:

/v1/auth
/v1/public
/v1/reader/favorites
/v1/reader/preferences
/v1/reader/notifications
FCM

Pantallas previstas

SPLASH
  │
  ▼
HOME
  │
  ├── Artículo del día
  │
  ├── Últimos artículos
  │
  ├── Categorías
  │
  ├── Búsqueda
  │
  └── Favoritos
        │
        ▼
     ARTÍCULO
        │
        ├── Texto
        ├── Imágenes
        ├── Tags
        ├── Categoría
        ├── Favorito
        └── Lectura por voz

MENÚ
  │
  ├── Histórico
  ├── Categorías
  ├── Favoritos
  ├── Notificaciones
  └── Preferencias
         │
         ├── Tamaño texto
         ├── Tema
         └── Voz

24. Web Lector

La Web utilizará principalmente:

/v1/public/articles
/v1/public/articles/today
/v1/public/articles/{slug}
/v1/public/search
/v1/public/categories
/v1/public/tags

Orientada a:

SEO
Artículos
Búsqueda
Categorías
Histórico
Compartir enlaces

25. Mapa de responsabilidades

┌─────────────────────────────────────────────────────────────┐
│                         BACKEND                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Auth / JWT / RBAC                                           │
│                                                             │
│ CMS                                                         │
│ ├── Articles                                                │
│ ├── Categories                                              │
│ ├── Tags                                                    │
│ ├── Media                                                   │
│ ├── OCR                                                     │
│ └── History                                                 │
│                                                             │
│ Reader                                                      │
│ ├── Public Articles                                         │
│ ├── Search                                                  │
│ ├── Favorites                                               │
│ ├── Preferences                                             │
│ └── Notifications                                           │
│                                                             │
│ Workers                                                     │
│ ├── Publication                                             │
│ └── Notification / FCM                                     │
│                                                             │
│ Storage                                                     │
│ └── MinIO                                                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ REST / JSON
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                         FLUTTER                             │
├───────────────────────────────┬─────────────────────────────┤
│           EDITOR              │           LECTOR            │
├───────────────────────────────┼─────────────────────────────┤
│ Login                         │ Login                       │
│ Dashboard                    │ Home                        │
│ Artículos                    │ Artículo del día             │
│ Crear                        │ Histórico                   │
│ Editar                       │ Categorías                  │
│ Programar                    │ Búsqueda                    │
│ Publicar                     │ Favoritos                   │
│ Categorías                   │ Notificaciones              │
│ Tags                         │ Preferencias                │
│ Media                        │ Lectura por voz             │
│ OCR                          │ Temas                       │
└───────────────────────────────┴─────────────────────────────┘

26. Estado del proyecto
Backend

[✓] Auth
[✓] JWT
[✓] Refresh Token
[✓] Sesiones
[✓] RBAC
[✓] Usuarios
[✓] Roles
[✓] Permisos

[✓] Articles CRUD
[✓] Article Blocks
[✓] Categories
[✓] Tags
[✓] Media
[✓] OCR
[✓] Article History

[✓] Scheduling
[✓] Publication Worker

[✓] Public Reader API
[✓] Article of the Day
[✓] Public Search
[✓] Public Categories
[✓] Public Tags

[✓] Reader Preferences
[✓] Favorites
[✓] Reader Notifications

[~] FCM
[~] Notification Worker
[~] Registro de dispositivos FCM

Flutter Editor

[ ] Proyecto Flutter
[ ] Login
[ ] Manejo JWT
[ ] Dashboard
[ ] Calendario
[ ] Lista artículos
[ ] Crear artículo
[ ] Editor de bloques
[ ] Media
[ ] OCR
[ ] Categorías
[ ] Tags
[ ] Programación
[ ] Publicación
[ ] Historial
[ ] Administración

Flutter Lector

[ ] Proyecto Flutter
[ ] Login
[ ] Home
[ ] Artículo del día
[ ] Histórico
[ ] Categorías
[ ] Búsqueda
[ ] Detalle artículo
[ ] Favoritos
[ ] Notificaciones
[ ] Preferencias
[ ] Tema oscuro/claro
[ ] Tamaño de texto
[ ] Lectura por voz
[ ] Firebase / FCM

Web Lector

[ ] Proyecto Web
[ ] Home
[ ] Artículo
[ ] Categorías
[ ] Búsqueda
[ ] Histórico
[ ] SEO

27. Regla para continuar el proyecto

Antes de desarrollar Flutter:

NO REDISEÑAR BACKEND
        │
        ▼
CONSUMIR LOS CONTRATOS EXISTENTES
        │
        ▼
CREAR MODELOS DTO EN FLUTTER
        │
        ▼
CREAR SERVICES API
        │
        ▼
CREAR STATE MANAGEMENT
        │
        ▼
CREAR PANTALLAS

El Frontend debe considerar al Backend como la fuente oficial de los contratos.

Flutter
   │
   ├── AuthService
   ├── ArticleService
   ├── CategoryService
   ├── TagService
   ├── MediaService
   ├── OCRService
   ├── FavoriteService
   ├── ReaderPreferenceService
   ├── NotificationService
   └── FCMService

28. Flujo completo del sistema

                    EDITOR
                      │
                      ▼
               Crear artículo
                      │
                      ▼
                 Guardar DRAFT
                      │
             ┌────────┴────────┐
             │                 │
             ▼                 ▼
          PUBLICAR          PROGRAMAR
             │                 │
             ▼                 ▼
        PUBLISHED          SCHEDULED
             │                 │
             │          Publication Worker
             │                 │
             │                 ▼
             │             PUBLISHED
             │                 │
             └────────┬────────┘
                      ▼
               Notification Event
                      │
                      ▼
                     FCM
                      │
                      ▼
                   LECTOR
                      │
                      ▼
              Abre notificación
                      │
                      ▼
             GET /public/articles
                      │
                      ▼
                 Leer artículo
                      │
             ┌────────┼────────┐
             ▼        ▼        ▼
          Favorito  Compartir  Voz

29. Principio principal del Frontend

                  BACKEND
                     │
              API CONTRACT
                     │
                     ▼
                 FLUTTER
                     │
          ┌──────────┴──────────┐
          ▼                     ▼
       EDITOR                  LECTOR
          │                     │
          ▼                     ▼
       CMS UI                Reader UI

No debemos duplicar lógica editorial importante en Flutter.

El Backend decide:

    autenticación

    permisos

    estados

    publicación

    programación

    disponibilidad de artículos

    favoritos válidos

    preferencias persistidas

    contenido publicado

Flutter decide:

    presentación

    navegación

    interacción

    estado visual

    cache local

    experiencia de usuario

    recepción de FCM


### Y este es el mapa que yo tomaría como referencia al empezar Flutter

```text
                         ┌──────────────────────┐
                         │   RBAC BLOG          │
                         │   INFORMÁTIVO        │
                         └──────────┬───────────┘
                                    │
                     ┌──────────────┴──────────────┐
                     │                             │
                     ▼                             ▼
              ┌─────────────┐               ┌─────────────┐
              │ APP EDITOR  │               │ APP LECTOR  │
              └──────┬──────┘               └──────┬──────┘
                     │                             │
          ┌──────────┼──────────┐       ┌──────────┼──────────┐
          ▼          ▼          ▼       ▼          ▼          ▼
       Auth/CMS    Media/OCR  Admin   Home      Lectura   Perfil
          │          │          │       │          │          │
          └──────────┴──────────┘       ├── Search │          │
                     │                  ├── Cats   ├── Fav.   │
                     ▼                  ├── Tags   ├── Notif. │
                FASTAPI                 └── Today  └── Prefs. │
                     │                             │
        ┌────────────┼─────────────┐               │
        ▼            ▼             ▼               ▼
    PostgreSQL     MinIO       Workers           FCM
        │                          │               │
        │                    Publication           │
        │                    Notification          │
        │                          │               │
        └──────────────────────────┴───────────────┘