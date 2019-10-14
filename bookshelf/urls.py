from django.urls import path, re_path
from django.views.static import serve
from django.conf.urls import url

from .models import *
from . import views

app_name = 'bookshelf'
urlpatterns = [    
    url(r'^api/search', views.ApiEndpoint_Search.as_view()),
    url(r'^api/upload', views.ApiEndpoint_Upload.as_view()),
    url(r'^api/download', views.ApiEndpoint_Download.as_view(), name="download"),
    url(r'^api/scan', views.ApiEndpoint_Scan.as_view()),
    url(r'^lsview', views.LibrarianView.as_view(), name="librarianview"),
    url(r'^bsview', views.BookStandView.as_view(), name="bookstand"),
]
