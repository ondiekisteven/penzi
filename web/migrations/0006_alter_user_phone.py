# Generated by Django 3.2.4 on 2021-06-09 15:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0005_commandtrack_date_created'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='phone',
            field=models.BigIntegerField(unique=True),
        ),
    ]
