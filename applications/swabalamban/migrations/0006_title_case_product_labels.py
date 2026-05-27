from django.db import migrations


def title_case_product_labels(apps, schema_editor):
    Product = apps.get_model('swabalamban', 'Product')

    def format_label(value):
        text = (value or '').strip()
        if not text:
            return text
        return text.lower().title()

    for product in Product.objects.all().iterator():
        new_label = format_label(product.label)
        if new_label and new_label != product.label:
            product.label = new_label
            product.save(update_fields=['label'])


class Migration(migrations.Migration):

    dependencies = [
        ('swabalamban', '0005_capitalize_product_labels'),
    ]

    operations = [
        migrations.RunPython(title_case_product_labels, migrations.RunPython.noop),
    ]
