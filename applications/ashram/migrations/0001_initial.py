# Generated by Django 2.2 on 2020-06-23 15:43

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('bandhuapp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('description', models.TextField(max_length=1000)),
                ('activity_date', models.DateField(default=django.utils.timezone.now)),
            ],
            options={
                'verbose_name_plural': 'Activities',
            },
        ),
        migrations.CreateModel(
            name='ActivityCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('category', models.CharField(choices=[('Cultural', 'Cultural'), ('Sports', 'Sports'), ('Debate', 'Debate')], max_length=50)),
            ],
            options={
                'verbose_name_plural': 'Activity Categories',
            },
        ),
        migrations.CreateModel(
            name='Ashram',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('locality', models.CharField(max_length=100)),
                ('description', models.TextField(max_length=1000)),
                ('address', models.CharField(max_length=250)),
                ('slug', models.SlugField(blank=True, null=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='ashram/thumbnails/')),
                ('admin', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='bandhuapp.Profile')),
            ],
        ),
        migrations.CreateModel(
            name='Photo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('picture', models.ImageField(upload_to='ashram/')),
                ('approved', models.BooleanField(default=False)),
                ('activity', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='ashram.Activity')),
                ('ashram', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ashram.Ashram')),
            ],
        ),
        migrations.CreateModel(
            name='Meeting',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('schedule', models.DateTimeField()),
                ('topic', models.CharField(max_length=250)),
                ('location', models.CharField(max_length=100)),
                ('agenda', models.TextField()),
                ('minutes', models.FileField(upload_to='ashram/meeting/%Y-%m-%d')),
                ('ashram', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ashram.Ashram')),
            ],
        ),
        migrations.CreateModel(
            name='Attendee',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('email', models.EmailField(max_length=254)),
                ('contact_no', models.CharField(max_length=13, verbose_name='Contact Number')),
                ('meeting', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ashram.Meeting')),
                ('profile', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='bandhuapp.Profile')),
            ],
        ),
        migrations.AddField(
            model_name='activity',
            name='ashram',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ashram.Ashram'),
        ),
        migrations.AddField(
            model_name='activity',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='ashram.ActivityCategory'),
        ),
    ]