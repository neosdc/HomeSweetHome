# Generated by Django 2.1 on 2018-12-10 10:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accountbook', '0023_merge_20180911_1458'),
    ]

    operations = [
        migrations.RenameField(
            model_name='deal',
            old_name='longuitude',
            new_name='longitude',
        ),
    ]
