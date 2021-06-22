from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path('', views.main, name='main'),
    path('add_query/', views.upload_query, name='upload_query'),
    path('check/<int:pk>', views.check_document, name='check_document'),
]
