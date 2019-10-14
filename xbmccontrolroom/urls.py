from django.urls import path, re_path
from django.views.static import serve
from django.conf.urls import url

from .models import *
from . import views

app_name = 'xbmccontrolroom'
urlpatterns = [    
    url(r'^api/welcome', views.ApiEndpoint_HostWelcome.as_view()),
    url(r'^api/ping', views.ApiEndpoint_HostPing.as_view()),
    url(r'^api/scan', views.ApiEndpoint_ScanMediaFiles.as_view()),
    url(r'^api/mediabunch', views.ApiEndpoint_SyncMediaBunchList.as_view()),
    url(r'^api/mediadownload', views.ApiEndpoint_SyncMediaDownload.as_view()),
    url(r'^api/bye', views.ApiEndpoint_HostByeBye.as_view()),
    url(r'^api/mediastream', views.ApiEndpoint_MediaStream.as_view()),

    url(r'^api/addonversion', views.ApiEndpoint_AddonVersion.as_view()),
    url(r'^api/addondownload', views.ApiEndpoint_AddonDownload.as_view()),

    url(r'^sbaccess', views.StoryBoardAccessView.as_view()),
    url(r'^sbeditor', views.StoryBoardEditorView.as_view()),
    url(r'^sbtempsave', views.StoryNotepadSaveView.as_view(), name="sbtempsave"),
    url(r'^sbtempload', views.StoryNotepadLoadView.as_view(), name="sbtempload"),
    url(r'^sbsave', views.StoryBoardSaveView.as_view(), name="sbsave"),
    url(r'^sbload', views.StoryBoardLoadView.as_view(), name="sbload"),
    url(r'^sbview', views.StoryBoardView.as_view(), name="sbview"),
    re_path(r'^story/(?P<path>.*)$', serve, {
        'document_root': StoryBoard.STORY_PATH,
    }),
]
