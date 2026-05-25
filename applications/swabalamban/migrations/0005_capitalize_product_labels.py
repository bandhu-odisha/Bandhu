from django.db import migrations


def capitalize_product_labels(apps, schema_editor):
    Product = apps.get_model('swabalamban', 'Product')
    for product in Product.objects.all().iterator():
        label = (product.label or '').strip()
        if not label:
            continue
        new_label = label[0].upper() + label[1:]
        if new_label != product.label:
            product.label = new_label
            product.save(update_fields=['label'])


class Migration(migrations.Migration):

    dependencies = [
        ('swabalamban', '0004_remove_product_slug'),
    ]

    operations = [
        migrations.RunPython(capitalize_product_labels, migrations.RunPython.noop),
    ]
