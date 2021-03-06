# Generated by Django 2.1.4 on 2019-01-03 11:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('xbmccontrolroom', '0009_auto_20190102_1357'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='mediafile',
            options={'verbose_name': 'Media File', 'verbose_name_plural': 'Media Files'},
        ),
        migrations.AlterModelOptions(
            name='onair',
            options={'verbose_name': 'OnAir Condition', 'verbose_name_plural': 'OnAir Conditions'},
        ),
        migrations.AlterField(
            model_name='onair',
            name='action',
            field=models.CharField(choices=[('downloadAndPlay', '다운로드 및 플레이'), ('quit', '호스트종료'), ('restart', '호스트재시작'), ('reboot', '리부트'), ('powerdown', '전원끄기'), ('update', '업데이트'), ('', '없음')], default='', max_length=64, verbose_name='동작 명령'),
        ),
    ]
