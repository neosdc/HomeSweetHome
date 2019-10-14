import os

from django.conf import settings
from django.db import models
from django.utils.html import format_html

from taggit.managers import TaggableManager

from django.contrib.auth.models import User

class XbmcMediaHost(models.Model):
    '''XBMC 호스트'''
    idx = models.AutoField(primary_key=True, verbose_name='식별자')
    name = models.CharField(max_length=100, verbose_name='XBMC호스트')
    ipaddress = models.CharField(max_length=50, verbose_name='IP주소')
    macaddress = models.CharField(max_length=17, verbose_name='MAC주소')
    osinfo = models.CharField(max_length=200, verbose_name='운영체제정보')
    appinfo = models.CharField(max_length=200, verbose_name='XBMC정보')
    deviceinfo = models.CharField(max_length=200, verbose_name='장치정보')

    class Meta:
        verbose_name = 'Xbmc Media Host'
        verbose_name_plural = 'Xbmc Media Hosts'

    def __str__(self):
        return self.name

class OnAir(models.Model):
    '''활성 호스트 제어'''
    TYPEACTION_CHOICES = (
        ('downloadAndPlay', '다운로드 및 플레이'),
        ('quit', '호스트종료'),
        ('restart', '호스트재시작'),
        ('reboot', '리부트'),
        ('powerdown', '전원끄기'),
        ('update', '업데이트'),
        ('', '없음')
    )
    xbmcmediahost = models.ForeignKey(XbmcMediaHost, on_delete=models.CASCADE, verbose_name='XBMC호스트')
    action = models.CharField(default='', max_length=64, choices=TYPEACTION_CHOICES, verbose_name='동작 명령')
    action_param = models.CharField(default='', max_length=255, verbose_name='동작 명령 매개변수')
    updDate = models.DateTimeField(auto_now_add=True, verbose_name='활성 일시')

    class Meta:
        verbose_name = 'OnAir Condition'
        verbose_name_plural = 'OnAir Conditions'

    def __str__(self):
        return "({})[{}]".format(self.xbmcmediahost, self.updDate)


class MediaFile(models.Model):
    '''미디어 파일'''
    MEDIAS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'medias')

    TYPEFLAG_THUMBNAIL = (
        (0, '일반'),
        (1, '썸네일용')
    )
    idx = models.AutoField(primary_key=True, verbose_name='식별자')
    name = models.CharField(max_length=255, verbose_name='파일명')
    path = models.TextField(verbose_name='경로')
    md5 = models.CharField(max_length=255, verbose_name='MD5 해시')
    size = models.IntegerField(default=0, verbose_name='파일크기')
    thumbnail = models.IntegerField(default=0, choices=TYPEFLAG_THUMBNAIL, verbose_name='썸네일용', help_text='0 일반, 1 썸네일')
    updDate = models.DateTimeField(auto_now_add=True, verbose_name='기록 일시')
    tags = TaggableManager(blank=True)

    class Meta:
        verbose_name = 'Media File'
        verbose_name_plural = 'Media Files'

    def __str__(self):
        return "{}".format(os.path.join(self.path, self.name).replace(self.MEDIAS_PATH, ''))

    def fullpath(self):
        return "{}".format(os.path.join(MediaFile.MEDIAS_PATH, self.path, self.name))

    def thumbnail_image(self):
        fname, ext = os.path.splitext(self.name)
        return format_html('<img src="{}" />'.format('/images/mediafile/thumbnail/' + str(self.idx) + ext))

class AddonFile(models.Model):
    '''XBMC Addon 파일'''
    version = models.CharField(max_length=32, verbose_name='버전')
    addonfile = models.FileField(upload_to='static/')
    class Meta:
        verbose_name = 'Kodi Addon File'
        verbose_name_plural = 'Kodi Addon Files'

    def __str__(self):
        return "{}".format(self.version)


class StoryBoard(models.Model):
    '''스토리 보드'''
    STORY_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'story')
    idx = models.AutoField(primary_key=True, verbose_name='식별자')
    name = models.CharField(max_length=255, verbose_name='제목')
    content = models.TextField(verbose_name='내용', blank=True)
    serv_file = models.BinaryField(verbose_name='파일', null=True)
    thumbnail_image = models.ForeignKey(MediaFile, on_delete=models.SET_NULL, related_name='%(class)s_relation_thumbnail', blank=True, null=True, verbose_name='썸네일')
    md5 = models.CharField(max_length=255, verbose_name='MD5 해시')
    updDate = models.DateTimeField(auto_now_add=True, verbose_name='기록 일시')
    tags = TaggableManager(blank=True)

    class Meta:
        verbose_name = 'Story Board'
        verbose_name_plural = 'Story Boards'

    def __str__(self):
        return "{}".format(self.name)

class StoryNotepad(models.Model):
    '''스토리 임시 저장'''
    author = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE, verbose_name='작성자')
    content = models.TextField(verbose_name='내용')
    updDate = models.DateTimeField(auto_now_add=True, verbose_name='기록 일시')

    class Meta:
        verbose_name = 'Story Notepad'
        verbose_name_plural = 'Story Notepads'

    def __str__(self):
        return "{}'s story note".format(self.author.username)