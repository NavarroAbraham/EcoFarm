from django.core.management.base import BaseCommand
from core.models import Product


class Command(BaseCommand):
    help = 'Crea productos de ejemplo para la tienda EcoFarm'

    def handle(self, *args, **options):
        products_data = [
            {
                'name': 'Tomates Orgánicos',
                'description': 'Tomates frescos cultivados sin pesticidas. Perfectos para ensaladas y salsas.',
                'price': 8.99,
                'category': 'Verduras'
            },
            {
                'name': 'Lechugas Frescas',
                'description': 'Lechuga romana orgánica de hoja tierna. Ideal para ensaladas saludables.',
                'price': 4.49,
                'category': 'Verduras'
            },
            {
                'name': 'Zanahorias Biologicas',
                'description': 'Zanahorias de cultivo ecológico, ricas en vitaminas. Crudas o cocidas.',
                'price': 5.99,
                'category': 'Verduras'
            },
            {
                'name': 'Manzanas de Granja',
                'description': 'Manzanas frescas sin tratamientos químicos. Crujientes y sabrosas.',
                'price': 6.99,
                'category': 'Frutas'
            },
            {
                'name': 'Plátanos Maduros',
                'description': 'Plátanos cultivados de manera sostenible. Ricos en potasio y fibra.',
                'price': 3.99,
                'category': 'Frutas'
            },
            {
                'name': 'Fresas Silvestres',
                'description': 'Fresas frescas y deliciosas. Perfectas para postres y desayunos.',
                'price': 7.99,
                'category': 'Frutas'
            },
        ]

        for product_data in products_data:
            product, created = Product.objects.get_or_create(
                name=product_data['name'],
                defaults={
                    'description': product_data['description'],
                    'price': product_data['price'],
                    'category': product_data['category'],
                }
            )

            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Creado: {product.name} - ${product.price}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'⚠ Ya existe: {product.name}')
                )

        self.stdout.write(self.style.SUCCESS('\n✅ Carga de productos completada'))
