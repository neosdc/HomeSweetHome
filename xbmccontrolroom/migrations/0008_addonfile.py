# Generated by Django 2.1.4 on 2019-01-02 10:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('xbmccontrolroom', '0007_mediafile_thumbnail'),
    ]

    operations = [
        migrations.CreateModel(
            name='AddonFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('version', models.CharField(max_length=32, verbose_name='버전')),
                ('addonfile', models.FileField(upload_to='static/')),
            ],
        ),
    ]
