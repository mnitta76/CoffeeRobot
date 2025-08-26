from django.urls import path

from chat import views

urlpatterns = [
    path("", views.chat, name="chat"),
    path('clear/', views.clear_chat, name='clear_chat'),
    path('change_mode/', views.change_mode, name='change_mode'),
    path('set_retriever/', views.set_retriever, name='set_retriever'),
    path('upload_file/', views.upload_file, name='upload_file'),
]