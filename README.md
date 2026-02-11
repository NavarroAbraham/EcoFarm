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
