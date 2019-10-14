from django import template
from xbmccontrolroom.models import MediaFile

register = template.Library()

@register.filter
def replace_mediapath(value):
    return value.replace(MediaFile.MEDIAS_PATH, '') if value is not None else value
