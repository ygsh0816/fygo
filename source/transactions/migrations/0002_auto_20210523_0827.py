# Generated by Django 3.2.3 on 2021-05-23 02:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='transaction',
            name='modify_date',
        ),
        migrations.RemoveField(
            model_name='user',
            name='is_app_user',
        ),
        migrations.AlterField(
            model_name='transaction',
            name='transaction_type',
            field=models.SmallIntegerField(choices=[(2, 'PURCHASE'), (1, 'REFUND'), (3, 'WITHDRAWAL')]),
        ),
    ]
