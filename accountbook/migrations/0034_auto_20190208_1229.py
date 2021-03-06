# Generated by Django 2.1.5 on 2019-02-08 12:29

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accountbook', '0033_auto_20190113_1614'),
    ]

    operations = [
        migrations.AlterField(
            model_name='asset',
            name='idx',
            field=models.AutoField(primary_key=True, serialize=False, verbose_name='식별자'),
        ),
        migrations.AlterField(
            model_name='deal',
            name='idx',
            field=models.AutoField(primary_key=True, serialize=False, verbose_name='식별자'),
        ),
        migrations.AlterField(
            model_name='deal',
            name='latitude',
            field=models.DecimalField(blank=True, decimal_places=18, max_digits=20, null=True, validators=[django.core.validators.MaxValueValidator(90), django.core.validators.MinValueValidator(-90)], verbose_name='위도'),
        ),
        migrations.AlterField(
            model_name='deal',
            name='longitude',
            field=models.DecimalField(blank=True, decimal_places=17, max_digits=20, null=True, validators=[django.core.validators.MaxValueValidator(180), django.core.validators.MinValueValidator(-180)], verbose_name='경도'),
        ),
        migrations.AlterField(
            model_name='event',
            name='idx',
            field=models.AutoField(primary_key=True, serialize=False, verbose_name='식별자'),
        ),
        migrations.AlterField(
            model_name='householdaccountbook',
            name='idx',
            field=models.AutoField(primary_key=True, serialize=False, verbose_name='식별자'),
        ),
        migrations.AlterField(
            model_name='package',
            name='idx',
            field=models.AutoField(primary_key=True, serialize=False, verbose_name='식별자'),
        ),
        migrations.AlterField(
            model_name='paymentmethod',
            name='idx',
            field=models.AutoField(primary_key=True, serialize=False, verbose_name='식별자'),
        ),
        migrations.AlterField(
            model_name='person',
            name='idx',
            field=models.AutoField(primary_key=True, serialize=False, verbose_name='식별자'),
        ),
        migrations.AlterField(
            model_name='product',
            name='idx',
            field=models.AutoField(primary_key=True, serialize=False, verbose_name='식별자'),
        ),
        migrations.AlterField(
            model_name='product',
            name='type_flag',
            field=models.IntegerField(choices=[(0, '정상'), (1, '부족'), (2, '카트')], default=0, help_text='0 정상, 1 부족, 2 카트', verbose_name='상태'),
        ),
        migrations.AlterField(
            model_name='wealth',
            name='idx',
            field=models.AutoField(primary_key=True, serialize=False, verbose_name='식별자'),
        ),
    ]
