# Generated by Django 3.2.3 on 2021-05-23 07:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0003_auto_20210523_1146'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='transaction_id',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='transaction_type',
            field=models.SmallIntegerField(choices=[(2, 'PURCHASE'), (1, 'REFUND'), (3, 'WITHDRAWAL')]),
        ),
    ]