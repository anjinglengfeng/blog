from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from taggit.managers import TaggableManager
from uuslug import slugify


class PublishedManager(models.Manager):
    def get_queryset(self):
        return super(PublishedManager, self).get_queryset().filter(status='published')


class Category(models.Model):
    name = models.CharField('分类名称', max_length=30)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "类别"
        verbose_name_plural = verbose_name


class Post(models.Model):
    title = models.CharField('标题', max_length=250)
    # slug = models.SlugField(editable=False)
    slug = models.SlugField('唯一标识',max_length=250, unique_for_date='publish')
    author = models.ForeignKey(User, verbose_name='作者', on_delete=models.CASCADE, related_name='blog_posts')
    body = models.TextField()
    publish = models.DateTimeField('发表时间', default=timezone.now())
    created = models.DateTimeField('创建时间', auto_now_add=True)
    updated = models.DateTimeField('更新时间', auto_now=True)
    STATUS_CHOICES = (('published', '发布'),('draft', '不发布'), )
    status = models.CharField('是否显示', max_length=10, choices=STATUS_CHOICES, default='published')
    objects = models.Manager()
    published = PublishedManager()
    tags = TaggableManager()
    category = models.ForeignKey(Category, verbose_name='分类', on_delete=models.CASCADE)
    views = models.PositiveIntegerField(default=0, editable=False)
    is_recommend = models.BooleanField('是否今日推荐', default=False)

    class Meta:
        verbose_name = '文章'
        verbose_name_plural = verbose_name
        ordering = ('-publish',)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse(
            'blog:post_detail',
            args=[
                self.publish.year,
                self.publish.month,
                self.publish.day,
                self.slug
            ]
        )

    def increase_views(self):
        self.views += 1
        self.save(update_fields=['views'])

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Post, self).save(*args, **kwargs)


class Comment(models.Model):
    post = models.ForeignKey(Post, verbose_name='文章', on_delete=models.CASCADE, related_name='comments')
    name = models.ForeignKey(User, verbose_name='评论人',max_length=80, on_delete=models.CASCADE)
    body = models.TextField()
    created = models.DateTimeField('创建时间', auto_now_add=True)
    updated = models.DateTimeField('更新时间', auto_now=True)
    active = models.BooleanField('是否显示', default=True)

    class Meta:
        verbose_name = '评论'
        verbose_name_plural = verbose_name
        ordering = ("created",)

    def __str__(self):
        return 'Comment by {} on {}'.format(self.name, self.post)


