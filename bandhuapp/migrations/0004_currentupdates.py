# Generated by Django 2.2.13 on 2022-12-03 19:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bandhuapp', '0003_urldata'),
    ]

    operations = [
        migrations.CreateModel(
            name='CurrentUpdates',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('desc', models.CharField(max_length=255)),
                ('url', models.CharField(blank=True, max_length=100, null=True)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
