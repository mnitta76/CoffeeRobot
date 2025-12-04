from django.urls import path

from .views import record_blog_view, record_view, trigger_blog_generation_view

urlpatterns = [
    path("view/", record_view),
    path("api/blog/view/", record_blog_view, name="record_blog_view"),
    path("api/blog/generate/", trigger_blog_generation_view, name="trigger_blog_generation"),
]
