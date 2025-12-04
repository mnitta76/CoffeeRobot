from django.db import models


class BlogView(models.Model):
    slug = models.CharField(max_length=255, db_index=True)
    year = models.IntegerField(blank=True, null=True, db_index=True)
    month = models.IntegerField(blank=True, null=True, db_index=True)
    day = models.IntegerField(blank=True, null=True, db_index=True)
    count = models.IntegerField(default=0)
    last_viewed = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    referrer = models.CharField(max_length=500, blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=["slug", "year", "month", "day"]),
        ]

    def __str__(self):
        return f"{self.slug} ({self.year}-{self.month}-{self.day}) - {self.count}"
