from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='camera_index'),
    path('upload/', views.upload_image, name='upload_image'),
    path('upload_video/', views.upload_video, name='upload_video'),
]
