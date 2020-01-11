from django import forms
from .models import UserProfile


class ProfileForm(forms.Form):
    first_name = forms.CharField(label='姓', max_length=50, required=False)
    last_name = forms.CharField(label='名', max_length=50, required=False)
    org = forms.CharField(label='组织', max_length=50, required=False)
    telephone = forms.CharField(label='电话', max_length=50, required=False)


class SignupForm(forms.Form):
    def signup(self, request, user):
        user_profile = UserProfile()
        user_profile.user = user
        user.save()
        user_profile.save()