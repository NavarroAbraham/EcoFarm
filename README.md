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

| Método | URL                  | Descripción                                   |
|--------|----------------------|-----------------------------------------------|
| POST   | `/core/api/orders/`  | Crear `Order` + `Payment`. Retorna 201 con el objeto creado y el pago asociado. Se esperan los campos `customer_name`, `customer_email`, `total_amount` y `provider` (cadena libre; si el proveedor no es reconocido el endpoint responde 409).\
| GET    | `/core/api/orders/<id>/` | Obtener los datos de una orden existente (incluye pagos). 404 si no existe.

Los errores de validación devuelven 400, y si se solicita un `provider` no soportado se responde con 409.

