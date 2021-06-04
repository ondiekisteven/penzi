# Generated by Django 3.2.4 on 2021-06-04 07:34

from django.db import migrations, models
import django.db.models.deletion
import web.models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0002_auto_20210603_2206'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commandtrack',
            name='command',
            field=models.IntegerField(choices=[(1, 'SERVICE_ACTIVATION'), (2, 'SERVICE_REGISTRATION'), (3, 'DETAILS_REGISTRATION'), (4, 'SELF_DESCRIPTION'), (5, 'MATCH_REQUEST'), (6, 'SUBSEQUENT_MATCH'), (7, 'MORE_DETAILS'), (8, 'DESCRIPTION_REQUEST'), (9, 'NOTICE_CONFIRMATION'), (10, 'RE_ACTIVATION')], default=web.models.MessageCategory['SERVICE_REGISTRATION']),
        ),
        migrations.AlterField(
            model_name='commandtrack',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='web.user', unique=True),
        ),
        migrations.AlterField(
            model_name='commandtrack',
            name='user_reply',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='matchrequest',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='web.user'),
        ),
    ]
