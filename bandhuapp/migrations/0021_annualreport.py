from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bandhuapp', '0020_restore_staff_experience'),
    ]

    operations = [
        migrations.CreateModel(
            name='AnnualReport',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.PositiveIntegerField(help_text='Financial / report year (e.g. 2024 for FY 2023–24).', unique=True)),
                ('title', models.CharField(blank=True, help_text='Optional label shown in the footer. Defaults to “Annual Report {year}”.', max_length=200)),
                ('pdf_file', models.FileField(blank=True, help_text='Upload a PDF. Leave empty if you only use an external link.', null=True, upload_to='bandhuapp/annual_reports/')),
                ('external_url', models.URLField(blank=True, help_text='Google Drive or other public link to the PDF.', max_length=500)),
                ('is_published', models.BooleanField(default=True, help_text='Show this report in the site footer.')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Annual report',
                'verbose_name_plural': 'Annual reports',
                'ordering': ['-year'],
            },
        ),
    ]
