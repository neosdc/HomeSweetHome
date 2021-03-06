# Generated by Django 2.0.7 on 2019-01-03 23:13

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accountbook', '0028_auto_20190103_1117'),
    ]

    operations = [
        migrations.AddField(
            model_name='deal',
            name='address',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='주소'),
        ),
        migrations.AlterField(
            model_name='deal',
            name='latitude',
            field=models.DecimalField(blank=True, decimal_places=18, max_digits=20, null=True, validators=[django.core.validators.MaxValueValidator(90), django.core.validators.MinValueValidator(-90)]),
        ),
        migrations.AlterField(
            model_name='deal',
            name='longitude',
            field=models.DecimalField(blank=True, decimal_places=17, max_digits=20, null=True, validators=[django.core.validators.MaxValueValidator(180), django.core.validators.MinValueValidator(-180)]),
        ),
    ]
