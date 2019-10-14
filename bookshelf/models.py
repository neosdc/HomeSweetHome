import os

from django.db import models

from taggit.managers import TaggableManager

class Book(models.Model):
    BOOKS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'medias', 'books')

    idx = models.AutoField(primary_key=True, verbose_name='식별자')
    name = models.CharField(max_length=255, verbose_name='도서명')
    path = models.TextField(verbose_name='경로')
    md5 = models.CharField(max_length=255, verbose_name='MD5 해시')
    size = models.IntegerField(default=0, verbose_name='파일크기')    
    updDate = models.DateTimeField(auto_now_add=True, verbose_name='기록 일시')
    tags = TaggableManager(blank=True)
    
    def __str__(self):
        return "{}".format(self.name)

    def fullpath(self):
        return "{}".format(os.path.join(Book.BOOKS_PATH, self.path, self.name))

    # def thumbnail_image(self):
        # fname, ext = os.path.splitext(self.name)
        # return format_html('<img src="{}" />'.format('/images/mediafile/' + str(self.idx) + ext))
