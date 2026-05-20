# EcoFarm

Proyecto Django + servicio Flask para generación de certificados.

## Requisitos

- Python 3.10+ (o el que use su entorno virtual)
- `pip`
- Docker (opcional, para despliegue con `docker-compose`)

## Instalación rápida

1. Crear y activar un entorno virtual.

```bash
python -m venv .venv
source .venv/bin/activate   # PowerShell: .\.venv\Scripts\Activate.ps1
```

2. Instalar dependencias principales:

```bash
pip install -r requirements.txt
```

3. Ejecutar migraciones y crear superusuario:

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

4. Ejecutar servidor de desarrollo Django:

```bash
python manage.py runserver
```

## Servicio de certificados (Flask)

El proyecto incluye un microservicio Flask en la carpeta `flask_service` que genera/depura certificados. Para ejecutarlo localmente:

```bash
cd flask_service
pip install -r requirements.txt
python app.py
```

El adaptador de certificados en `core/adapters/external` usa la variable de entorno `FLASK_CERTIFICATE_URL` (por defecto `http://localhost:5000/`).

## Docker / Docker Compose

Hay un `Dockerfile` y `docker-compose.yml` en la raíz para orquestar la aplicación y el servicio Flask (y nginx si está configurado). Para levantar en modo contenedores:

```bash
docker-compose up --build
```

## Estructura principal del proyecto

```
./
├── Dockerfile
├── docker-compose.yml
├── manage.py
├── requirements.txt
├── db.sqlite3
├── EcoFarm/             # Configuración del proyecto (settings, urls, wsgi, asgi)
├── core/                # Aplicación principal (modelos, vistas, api, adapters)
├── flask_service/       # Servicio Flask para certificados
├── static/              # Archivos estáticos
└── templates/           # Plantillas globales
```

## Endpoints principales (resumen)

- `POST /api/v1/orders/` — Crear `Order` y `Payment`. Campos: `customer_name`, `customer_email`, `total_amount`, `provider`.
- `GET /api/v1/orders/<id>/` — Obtener orden por id.
- `POST /api/v1/ally/orders/` — Endpoint para órdenes entrantes desde aliados.
- `GET /api/v1/ally/orders/<external_id>/` — Consulta de orden externa.

Rutas relacionadas a cuenta y certificados (requieren autenticación):

- `GET /api/v1/account/orders/` — Órdenes del usuario autenticado.
- `GET /api/v1/account/orders/<id>/` — Detalle de orden con pagos.
- `GET /api/v1/certificates/` — Lista certificados del usuario autenticado.
- `POST /api/v1/certificates/create/` — Genera certificado (`order_id`, `course_name`).
- `GET /api/v1/certificates/<id>/download/` — Descargar PDF del certificado.

## Variables de entorno importantes

- `FLASK_CERTIFICATE_URL` — URL base del servicio Flask (por defecto `http://localhost:5000/`).

## Tests

- Ejecutar tests Django:

```bash
python manage.py test
```

- Tests en el servicio Flask (si aplica):

```bash
cd flask_service
pytest
```

## Notas

- Si el `provider` no es reconocido por la API de órdenes, el servicio responde con 409.
- Los errores de validación devuelven 400.
- Para producción, configure una base de datos externa y ajuste `EcoFarm/settings.py`.

Si quieres, puedo también:

- Ejecutar la suite de tests ahora.
- Preparar un `docker-compose.override.yml` para desarrollo.
- Añadir instrucciones de despliegue paso a paso.


