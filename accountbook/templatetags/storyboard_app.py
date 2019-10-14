from django import template
from django.conf import settings
from oauth2_provider.models import Application

register = template.Library()

@register.simple_tag
def storyboard_app():
    application = Application.objects.filter(name="storyboard").first()
    return None if application is None else "/o/authorize?client_id={}&redirect_uri={}&scope=read write&response_type=code&response_mode=form_post".format(application.client_id, application.redirect_uris)
