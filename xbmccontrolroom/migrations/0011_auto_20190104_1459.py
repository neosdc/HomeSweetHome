# Generated by Django 2.1.4 on 2019-01-04 14:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('xbmccontrolroom', '0010_auto_20190103_1117'),
    ]

    operations = [
        migrations.AlterField(
            model_name='xbmcmediahost',
            name='macaddress',
            field=models.CharField(max_length=17, verbose_name='MAC주소'),
        ),
    ]