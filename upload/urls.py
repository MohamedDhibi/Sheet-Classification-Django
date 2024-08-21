from django.urls import path
from django.conf.urls import include
from upload import views
urlpatterns = [
    path('', views.index, name='index'),
    path('upload/', views.index, name='upload'),
    path('home/', views.home, name='home'),
]
