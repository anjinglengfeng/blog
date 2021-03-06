from django.shortcuts import reverse
from .models import UserProfile
from .forms import ProfileForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, HttpResponseRedirect
from blog.models import Post, UserFavorite
from django.contrib.auth.models import User


@login_required
def profile(request):
    user = request.user
    # posts = Post.objects.filter(author=user.id)
    return render(request, 'account/profile.html', {'user':user})


@login_required
def profile_update(request):
    user = request.user
    user_profile = get_object_or_404(UserProfile, user=user)

    if request.method == "POST":
        form = ProfileForm(request.POST)

        if form.is_valid():
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.save()

            user_profile.org = form.cleaned_data['org']
            user_profile.telephone = form.cleaned_data['telephone']
            user_profile.user_img = request.FILES.get('user_img')
            user_profile.save()

            return HttpResponseRedirect(reverse('myaccount:profile'))

    else:
        default_data = {'first_name':user.first_name,
                        'last_name':user.last_name,
                        'org':user_profile.org,
                        'telephone':user_profile.telephone,
                        'user_img':user_profile.user_img}
        form = ProfileForm(default_data)

    return render(request, 'account/profile_update.html', {'form':form, 'user':user})


def my_post(request):
    user = request.user
    posts = Post.objects.filter(author=user)
    return render(request, 'account/my_post.html', {'posts': posts})


def fav_post(request):
    user = request.user
    # fav_id = UserFavorite.objects.filter(user=user)
    # fav_posts = Post.objects.filter(user=user)
    # posts = Post.objects.filter(user=user, id=fav_id)
    # fav_posts = user.userfavorite.filter(user=user)
    # user = UserProfile.objects.filter(user=user)


    # usr = Post.objects.filter(user=user).first()
    post = Post.objects.filter(user=user)
    print(user.id)
    # post = usr.post.all()
    return render(request, 'account/fav_post.html',{'posts': post})