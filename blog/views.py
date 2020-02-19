from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from .models import Post, Comment, Category, UserFavorite
from notice.models import Notice
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from .forms import EmailPostForm, PostForm
from django.core.mail import send_mail
from taggit.models import Tag
from django.db.models import Count
from uuslug import slugify
from datetime import datetime
from django.contrib import messages

from django.contrib.auth.models import User


def post_share(request, post_id):
    # 通过id 获取 post 对象
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False
    if request.method == 'POST':
        # 表单被提交
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # 验证表单数据
            cd = form.cleaned_data
            # 发送邮件......
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = '() ({}) recommends you reading "{}"'.format(cd['name'], cd['email'], post.title)
            message = 'Read "{}" at {}\n\n{}\'s comments:{}'.format(post.title, post_url, cd['name'], cd['comments'])
            send_mail(subject, message, 'liu1xufeng@gmail.com', [cd['to']])
            sent = True
    else:
        form = EmailPostForm()
    return render(request, 'blog/static/share.html', {'post':post, "form":form, 'sent':sent})


class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/static/index.html'


def post_list(request, tag_slug=None, category_slug=None):
    object_list = Post.published.all()
    tag = None
    notices = Notice.objects.all().order_by('-publish')
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])
    if category_slug:
        category = get_object_or_404(Tag, slug=category_slug)
        object_list = object_list.filter(category__in=[category])
    categories = Category.objects.all()
    # 获取推荐文章
    recommend_post_list = object_list.filter(is_recommend=1)
    if recommend_post_list:
        recommend_post = recommend_post_list[0]
    else:
        recommend_post = []

    paginator = Paginator(object_list, 3)  # 每页显示5篇文章
    page = request.GET.get('page', 1)  # 获取当前页的页码，默认为第一页
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # 如果page参数不是一个整数就返回第一页
        posts = paginator.page(1)
    except EmptyPage:
        # 如果页数超出总页数就返回最后一页
        posts = paginator.page(paginator.num_pages)
    return render(request, 'blog/static/index.html',{'page': page, 'posts': posts, 'tag':tag,"categories":categories, 'notices':notices, 'recommend_post':recommend_post})


def post_detail(request,year, month, day, post):
    post = get_object_or_404(Post,slug=post,
                             status='published',
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)
    comments = post.comments.filter(active=True)
    post.increase_views()   # 浏览次数加1
    # 判断是否是ajax提交数据
    if request.is_ajax():
        body = request.POST.get('body')
        print(body)
        new_comment = Comment.objects.create(name=request.user, body=body, post=post)
        new_comment.save()
        return HttpResponse('评论成功')
        # else:
        #     return HttpResponse("还未登录")
    # paginator = Paginator(comments, 5)  # 每页显示5篇文章
    # page = request.GET.get('page')
    # try:
    #     comments = paginator.page(page)
    # except PageNotAnInteger:
    #     # 如果page参数不是一个整数就返回第一页
    #     comments = paginator.page(1)
    # except EmptyPage:
    #     # 如果页数超出总页数就返回最后一页
    #     comments = paginator.page(paginator.num_pages)
    tags = post.tags.all()
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_tags = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
    similar_posts = similar_tags.annotate(same_tags=Count('tags')).order_by('-same_tags','-publish')[:4]

    has_fav = False
    if request.user.is_authenticated:
        if UserFavorite.objects.filter(user=request.user, post=post.id, fav_type=2):
            has_fav = True
    context = {'post': post, 'comments': comments, 'similar_posts': similar_posts, 'tags': tags, 'has_fav':has_fav}
    return render(request, 'blog/static/detail.html', context)


def tag_list(request):
    # tag_list = Tag.objects.all()
    # return render(request, 'blog/static/tags.html',{'tag_list':tag_list,})
    tag_list = Tag.objects.annotate(num_posts=Count('post')).filter(num_posts__gt=0)
    # return {'category_list': tag_list,}
    return render(request,'blog/static/tags.html',{'tag_list': tag_list,})


def links(request):
    return render(request, 'blog/static/links.html')


def readers(request):
    return render(request, 'blog/static/readers.html')


def search(request):
    posts = ''
    msg = ''
    if request.method == 'POST':
        q = request.POST.get('q')
        posts = Post.published.filter(title__icontains=q)
        if not posts:
            msg = '没有搜索到符合条件的文章!'
        else:
            msg = '为您搜索到以下文章:'
    return render(request, 'blog/static/search.html', {'msg': msg, 'posts': posts})


# class AddCommentView(View):
#     def post(self, request):
#         comment_form = CommentForm(request.POST)
#         if comment_form.is_valid():
#             comment_form.save()
#             return HttpResponse('{"status": "success"}', content_type='application/json')
#         else:
#             return HttpResponse('{"status": "fail"}', content_type='application/json')


# @receiver(post_save)
# def callback(sender, **kwargs):
#     messages.success(sender, "文章发表成功")



@csrf_exempt
def add_post(request):
    if request.method == 'POST':
        add_post_form = PostForm(request.POST, request.FILES)
        title = request.POST.get('title')
        slug = slugify(title)
        is_exsit = Post.objects.filter(slug=slug,created__date=datetime.now().date())
        if is_exsit:
            return HttpResponse('今日已有重复标题的文章了,请返回修改')
        if add_post_form.is_valid():
            add_post_form.save()
            messages.info(request, '文章发表成功')
            return redirect('myaccount:my_post')
        else:
            return HttpResponse('表单内容有误，请重新填写，请返回修改')
    else:
        add_post_form = PostForm()
        categories = Category.objects.all()
        tags = Tag.objects.all()
        context = {'add_post_form': add_post_form, 'categories':categories, 'tags':tags}
        return render(request, 'blog/static/add_post.html', context)


def update_post(request, id):
    post = Post.objects.get(id=id)
    if request.method == 'POST':
        update_post_form = PostForm(request.POST, request.FILES)
        if update_post_form.is_valid():
            # post.title = request.POST['title']
            # post.body = request.POST['body']
            # post.category = request.POST['category']
            # post.tags = request.POST['tags']
            # post.status = request.POST['status']
            # post.post_img = request.POST['post_img']

            post.title = update_post_form.cleaned_data['title']
            post.body = update_post_form.cleaned_data['body']
            post.category = update_post_form.cleaned_data['category']
            post.tags = update_post_form.cleaned_data['tags']
            post.status = update_post_form.cleaned_data['status']
            post.post_img = update_post_form.cleaned_data['post_img']



            post.save()
            return HttpResponse('文章更新成功')
        else:
            return HttpResponse('表单内容有误，请重新填写')
    else:
        update_post_form = PostForm()
        categories = Category.objects.all()
        tags = Tag.objects.all()
        str_tags = ''
        for tag in post.tags.all():
            str_tags += (str(tag ) + ',')
        context = {'post': post, 'update_post_form': update_post_form, 'categories': categories, 'tags': tags, 'str_tags': str_tags}
        return render(request, 'blog/static/update_post.html', context)


@login_required(login_url='/account/login')
@require_POST
@csrf_exempt
def delete_post(request):
    post_id = request.POST['post_id']
    try:
        post = Post.objects.get(id=post_id)
        post.delete()
        return HttpResponse("1")
    except:
        return HttpResponse("2")


# 收藏的函数
class AddFavView(View):
    def post(self, request):
        # 收藏都是记录他们的id，如果没取到把它设置未0，避免查询时异常
        post_id = request.POST.get('post_id', 0)
        # 表明收藏的类别
        fav_type = request.POST.get('fav_type', 0)

        # 收藏与已收藏取消收藏
        # 判断用户是否登录:即使没登录会有一个匿名的user
        if not request.user.is_authenticated:
            # 未登录时返回json提示未登录，跳转到登录页面是在ajax中做的
            return HttpResponse('{"fav_status":"fail", "fav_msg":"用户未登录"}', content_type='application/json')

        exist_records = UserFavorite.objects.filter(user=request.user, post=post_id, fav_type=fav_type)

        if exist_records:
            # 如果已经存在，表明用户取消收藏
            exist_records.delete()
            # 模型中存储的收藏数减1
            Post.objects.get(id=post_id).change_fav_nums(add=-1)
            return HttpResponse('{"fav_status":"success", "fav_msg":"添加收藏"}', content_type='application/json')
        else:
            user_fav = UserFavorite()
            # 如果取到了id值才进行收藏
            if int(post_id) > 0 and int(fav_type) > 0:
                user_fav.post_id = post_id
                user_fav.fav_type = fav_type
                user_fav.user = request.user
                user_fav.save()
                # 机构模型中存储的收藏数加1
                Post.objects.get(id=post_id).change_fav_nums(add=1)
                return HttpResponse('{"fav_status":"success", "fav_msg":"取消收藏"}', content_type='application/json')
            else:
                return HttpResponse('{"fav_status":"fail", "fav_msg":"收藏出错"}', content_type='application/json')