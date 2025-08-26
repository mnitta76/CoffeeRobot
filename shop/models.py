from django.conf import settings
from django.db import models

class Shop(models.Model):
    name = models.CharField('名称', max_length=128)
    address = models.CharField('住所', max_length=256, blank=True)
    created_at = models.DateTimeField('作成日', auto_now_add=True)
    updated_at = models.DateTimeField('更新日', auto_now=True)

    def __str__(self):
        return self.name