# Generated by Django 2.2 on 2020-06-23 15:43

from django.db import migrations, models
import django.db.models.deletion


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
                ('activity_date', models.DateField()),
            ],
            options={
                'verbose_name_plural': 'Activities',
            },
        ),
        migrations.CreateModel(
            name='ActivityCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('category', models.CharField(choices=[('Cultural', 'Cultural'), ('Sports', 'Sports'), ('Debate', 'Debate')], max_length=100)),
            ],
            options={
                'verbose_name_plural': 'Activity Categories',
            },
        ),
        migrations.CreateModel(
            name='Ankurayan',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.IntegerField(unique=True)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('theme', models.TextField(max_length=250)),
                ('description', models.TextField(max_length=1000)),
                ('logo', models.ImageField(upload_to='ankurayan/logo')),
                ('slug', models.SlugField()),
                ('admin', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='bandhuapp.Profile')),
            ],
            options={
                'verbose_name_plural': 'Ankurayan',
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
        migrations.AddField(
            model_name='activity',
            name='ankurayan',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ankurayan.Ankurayan'),
        ),
        migrations.AddField(
            model_name='activity',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='ankurayan.ActivityCategory'),
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