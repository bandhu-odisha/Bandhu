# Generated by Django 2.2.13 on 2020-11-15 06:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('description', models.TextField(max_length=1000)),
                ('date', models.DateField()),
                ('thumb', models.ImageField(default='ankurayan/thumbnails/activity.jpg', upload_to='ankurayan/thumbnails')),
            ],
            options={
                'verbose_name_plural': 'Activities',
            },
        ),
        migrations.CreateModel(
            name='Ankurayan',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.IntegerField(unique=True)),
                ('title', models.CharField(max_length=100)),
                ('theme', models.TextField(max_length=250)),
                ('description', models.TextField(max_length=3000)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('logo', models.ImageField(upload_to='ankurayan/logo')),
                ('slug', models.SlugField()),
            ],
            options={
                'verbose_name_plural': 'Ankurayan',
            },
        ),
        migrations.CreateModel(
            name='HomePage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tagline', models.TextField(max_length=1000, verbose_name='Tagline (Bold)')),
                ('description', models.TextField(max_length=3000)),
                ('picture', models.ImageField(upload_to='ankurayan/index')),
                ('banner_image', models.ImageField(upload_to='ankurayan/banner')),
            ],
            options={
                'verbose_name': 'Ankurayan Home Page',
                'verbose_name_plural': 'Ankurayan Home Page',
            },
        ),
        migrations.CreateModel(
            name='Photo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('picture', models.ImageField(upload_to='ankurayan/%Y')),
                ('approved', models.BooleanField(default=False)),
                ('activity', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='ankurayan.Activity')),
                ('ankurayan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ankurayan.Ankurayan')),
            ],
        ),
        migrations.CreateModel(
            name='Participant',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('gender', models.CharField(choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')], default='M', max_length=1)),
                ('school_class', models.CharField(max_length=50)),
                ('address', models.CharField(max_length=250)),
                ('contact_no', models.CharField(max_length=13, verbose_name='Contact Number')),
                ('ankurayan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ankurayan.Ankurayan')),
            ],
        ),
        migrations.CreateModel(
            name='Guest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('profession', models.CharField(max_length=100)),
                ('about', models.TextField(blank=True, max_length=500, null=True)),
                ('email', models.EmailField(max_length=254)),
                ('contact_no', models.CharField(max_length=13, verbose_name='Contact Number')),
                ('ankurayan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ankurayan.Ankurayan')),
            ],
        ),
        migrations.CreateModel(
            name='ActivityCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('ankurayan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ankurayan.Ankurayan')),
            ],
            options={
                'verbose_name_plural': 'Activity Categories',
            },
        ),
        migrations.AddField(
            model_name='activity',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='activities', to='ankurayan.ActivityCategory'),
        ),
        migrations.AddField(
            model_name='activity',
            name='runner_up1',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='FirstRunnerUp', to='ankurayan.Participant'),
        ),
        migrations.AddField(
            model_name='activity',
            name='runner_up2',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='SecondRunnerUp', to='ankurayan.Participant'),
        ),
        migrations.AddField(
            model_name='activity',
            name='winner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='Winner', to='ankurayan.Participant'),
        ),
    ]