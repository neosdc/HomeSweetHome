"""HomeSweetHome URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path, re_path
from django.conf.urls import url

from django.conf import settings
from django.views.static import serve
from django.views.generic.base import RedirectView

import oauth2_provider.views as oauth2_views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

# OAuth2 provider endpoints
oauth2_endpoint_views = [
    url(r'^authorize/$', oauth2_views.AuthorizationView.as_view(), name="authorize"),
    url(r'^token/$', oauth2_views.TokenView.as_view(), name="token"),
    url(r'^revoke-token/$', oauth2_views.RevokeTokenView.as_view(), name="revoke-token"),
]

if settings.DEBUG:
    oauth2_endpoint_views += [
        # OAuth2 Application Management endpoints
        url(r'^applications/$', oauth2_views.ApplicationList.as_view(), name="list"),
        url(r'^applications/register/$', oauth2_views.ApplicationRegistration.as_view(), name="register"),
        url(r'^applications/(?P<pk>\d+)/$', oauth2_views.ApplicationDetail.as_view(), name="detail"),
        url(r'^applications/(?P<pk>\d+)/delete/$', oauth2_views.ApplicationDelete.as_view(), name="delete"),
        url(r'^applications/(?P<pk>\d+)/update/$', oauth2_views.ApplicationUpdate.as_view(), name="update"),
        # OAuth2 Token Management endpoints
        url(r'^authorized-tokens/$', oauth2_views.AuthorizedTokensListView.as_view(), name="authorized-token-list"),
        url(r'^authorized-tokens/(?P<pk>\d+)/delete/$', oauth2_views.AuthorizedTokenDeleteView.as_view(),
            name="authorized-token-delete"),
    ]

urlpatterns = [
    path('admin/', admin.site.urls),
    # OAuth 2 endpoints:
    url(r'^o/', include(oauth2_endpoint_views)),
    path('', RedirectView.as_view(url='/static/index.html', permanent=True)),
    re_path(r'^favicon.ico', RedirectView.as_view(url='/static/favicon.ico', permanent=True)),
    re_path(r'^static/(?P<path>.*)$', serve, {
        'document_root': settings.STATIC_ROOT,
    }),

    path('admin/doc/', include('django.contrib.admindocs.urls')),
    re_path(r'^images/(?P<path>.*)$', serve, {
        'document_root': settings.IMAGE_ROOT,
    }),
    path('accountbook/', include('accountbook.urls')),
    path('xbmccontrol/', include('xbmccontrolroom.urls')),
    path('bookshelf/', include('bookshelf.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
]

if settings.DEBUG == True:
    urlpatterns += staticfiles_urlpatterns()