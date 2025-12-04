from django.contrib import admin
from .models import BlogView


@admin.register(BlogView)
class BlogViewAdmin(admin.ModelAdmin):
    list_display = ("slug", "year", "month", "day", "count", "last_viewed")
    search_fields = ("slug", "referrer")
    list_filter = ("year", "month", "day")
