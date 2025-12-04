from django.urls import path

from .views import record_blog_view, record_view, trigger_blog_generation_view

urlpatterns = [
    path("view/", record_view),
    path("api/view/", record_blog_view, name="record_blog_view"),
    path("api/generate/", trigger_blog_generation_view, name="trigger_blog_generation"),
]
