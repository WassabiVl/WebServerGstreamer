#  this is the simplest view possible in Django. To call the view, we need to map it to a URL - and for this we need a URLconf

from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
]