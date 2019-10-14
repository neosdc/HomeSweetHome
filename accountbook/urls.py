from django.urls import path
from django.conf.urls import url

from . import views

app_name = 'accountbook'
urlpatterns = [
    path('', views.HouseholdAccountBookListView.as_view(), name='index'),
    path('deal/<pk>', views.DealView.as_view(), name='dealdetail'),
    url(r'^book/([0-9]+)/$', views.HouseholdAccountBookView.as_view(), name='book'),
    url(r'^packages/([0-9]+)/$', views.PackageListView.as_view(), name='packages'),
    path('package/<pk>', views.PackageView.as_view(), name='packagedetail'),
    url(r'^api/hello', views.ApiEndpoint.as_view()), # an example resource endpoint
    path('thumbnailscan', views.ThumbnailValidationScanView.as_view(), name='thumbnailvalidationscan'),
    
]
