# Generated by Django 3.2.4 on 2021-06-09 15:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0006_alter_user_phone'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='destination',
            field=models.BigIntegerField(),
        ),
        migrations.AlterField(
            model_name='message',
            name='source',
            field=models.BigIntegerField(),
        ),
    ]
