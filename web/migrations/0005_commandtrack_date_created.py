# Generated by Django 3.2.4 on 2021-06-04 11:59

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0004_alter_commandtrack_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='commandtrack',
            name='date_created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
