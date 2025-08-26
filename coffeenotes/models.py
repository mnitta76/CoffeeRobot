from django.conf import settings
from django.db import models
from shop.models import Shop

class Coffeenote(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.SET_NULL, null=True)
    bean = models.CharField('豆', max_length=64, blank=True)
    roast_level = models.CharField('焙煎度', max_length=64, blank=True)
    extract_method = models.CharField('抽出方法', max_length=64, blank=True)
    grind_size = models.CharField('挽き方', max_length=64, blank=True)
    memo = models.CharField('メモ', max_length=256, blank=True)
    smell = models.PositiveIntegerField('香り', default=0)
    acdity = models.PositiveIntegerField('酸味', default=0)
    body = models.PositiveIntegerField('コク', default=0)
    aftertaste = models.PositiveIntegerField('後味', default=0)
    bitterness = models.PositiveIntegerField('苦味', default=0)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='作成者', on_delete=models.CASCADE)
    created_at = models.DateTimeField('作成日', auto_now_add=True)
    updated_at = models.DateTimeField('更新日', auto_now=True)

    def __str__(self):
        return self.bean