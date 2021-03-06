# Generated by Django 2.1.5 on 2019-01-12 14:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accountbook', '0031_auto_20190111_1624'),
    ]

    operations = [
        migrations.AlterField(
            model_name='package',
            name='price',
            field=models.PositiveIntegerField(default=1, verbose_name='금액'),
        ),
        migrations.AlterField(
            model_name='package',
            name='quantity',
            field=models.PositiveIntegerField(default=1, verbose_name='수량'),
        ),
        migrations.AlterField(
            model_name='wealth',
            name='price',
            field=models.PositiveIntegerField(default=0, verbose_name='획득 금액'),
        ),
    ]
