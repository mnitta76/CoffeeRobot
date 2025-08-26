from django.urls import path
from . import views

urlpatterns = [
    path('x/likefollows/', views.likeFollws_to_x, name='likeFollws_to_x'),
]