from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ankurayan', '0013_guest_photo_and_avatar'),
    ]

    operations = [
        migrations.CreateModel(
            name='AnkurayanInvitationLetter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(help_text='Single-page invitation letter (PDF or image).', upload_to='ankurayan/invitation_letters/')),
                ('uploaded_at', models.DateTimeField(auto_now=True)),
                ('ankurayan', models.OneToOneField(db_constraint=False, on_delete=django.db.models.deletion.CASCADE, related_name='invitation_letter', to='ankurayan.Ankurayan')),
            ],
            options={
                'verbose_name': 'Invitation letter',
                'verbose_name_plural': 'Invitation letters',
            },
        ),
    ]
