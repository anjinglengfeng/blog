from django.db import models
from django.contrib.auth.models import User
from allauth.account.models import EmailAddress


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    user_img = models.ImageField(upload_to='user_img', blank=True)
    org = models.CharField('组织', max_length=128, blank=True)
    telephone = models.CharField('手机号码', max_length=50, blank=True)
    mod_date = models.DateTimeField('上次修改时间', auto_now=True)

    class Meta:
        verbose_name = '个人资料'

    def __str__(self):
        return "{}的个人资料".format(self.user_img)

    def account_verified(self):
        if self.user.is_authenticated:
            result = EmailAddress.objects.filter(email=self.user.email)
            if len(result):
                return result[0].verified
        return False