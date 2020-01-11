from django.db import models
from django.utils import timezone


class Notice(models.Model):
    title = models.CharField('公告标题', max_length=30)
    body = models.TextField('公告内容')
    publish = models.DateTimeField('发表时间', default=timezone.now())

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "公告"
        verbose_name_plural = verbose_name