# EcoFarm

## Configuración del proyecto

1. Instalar dependencias:
```bash
pip install -r requirements.txt
```

2. Ejecutar migraciones:
```bash
python manage.py makemigrations
python manage.py migrate
```

3. Crear superusuario:
```bash
python manage.py createsuperuser
```

4. Ejecutar servidor:
```bash
python manage.py runserver
```

## Estructura del Proyecto

```
EcoFarm/
├── EcoFarm/          # Configuración principal del proyecto
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── static/           # Archivos estáticos
│   ├── css/
│   ├── js/
│   └── images/
├── media/            # Archivos subidos por usuarios
├── templates/        # Plantillas HTML globales
├── manage.py
└── requirements.txt
```

## API REST (Django REST Framework)

El sistema expone un par de endpoints para crear órdenes y consultar su estado.

| Método | URL                              | Descripción                                   |
|--------|----------------------------------|-----------------------------------------------|
| POST   | `/api/v1/orders/`                | Crear `Order` + `Payment`. Retorna 201 con el objeto creado y el pago asociado. Campos: `customer_name`, `customer_email`, `total_amount`, `provider` (si no es reconocido responde 409). |
| GET    | `/api/v1/orders/<id>/`           | Obtener los datos de una orden existente. 404 si no existe. |
| POST   | `/api/v1/ally/orders/`           | Endpoint para órdenes entrantes de un aliado (contrato externo). |
| GET    | `/api/v1/ally/orders/<external_id>/` | Consulta de una orden externa via adapter stub. |

Los errores de validación devuelven 400, y si se solicita un `provider` no soportado se responde con 409.

### Cuenta y certificados (requiere autenticación)

| Método | URL                                   | Descripción |
|--------|---------------------------------------|-------------|
| GET    | `/api/v1/account/orders/`             | Lista órdenes del usuario autenticado. |
| GET    | `/api/v1/account/orders/<id>/`        | Detalle de orden con pagos. |
| GET    | `/api/v1/certificates/`               | Lista certificados del usuario autenticado. |
| POST   | `/api/v1/certificates/create/`        | Genera certificado para una orden (`order_id`, `course_name`). |
| GET    | `/api/v1/certificates/<id>/`          | Detalle de certificado. |
| GET    | `/api/v1/certificates/<id>/download/` | Descarga PDF del certificado. |

### Integración externa (certificados)

El adapter de certificados consume el servicio Flask usando la variable de entorno `FLASK_CERTIFICATE_URL` (por defecto `http://localhost:5000/`).

