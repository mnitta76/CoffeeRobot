from django.urls import path
from coffeenotes import views

urlpatterns = [
    path("", views.coffeenote, name="coffeenote"),
    path("new/", views.coffeenote_new, name="coffeenote_new"),
    path("<int:coffeenote_id>/", views.coffeenote_detail, name="coffeenote_detail"),
    path("<int:coffeenote_id>/edit/", views.coffeenote_edit, name="coffeenote_edit"),
]
