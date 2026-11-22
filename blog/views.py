# 文件路径：blog/views.py
"""blog 应用的视图。

包含：
    PostListView    文章列表（分类筛选 + 关键词搜索 + 分页）
    PostDetailView  文章详情
    FavoritesView   我的收藏
    register        注册
    toggle_favorite 收藏 / 取消收藏
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, ListView

from .forms import RegisterForm
from .models import Category, Post


def _with_meta(queryset):
    """统一补上分类和收藏数，避免模板里对每篇文章再查一次数据库。

    注意：annotate 会引入 GROUP BY，Django 就不再认为查询集「有排序」，
    分页时可能顺序错乱并抛出 UnorderedObjectListWarning，所以这里显式排序。
    """
    return (
        queryset.select_related('category')
        .annotate(favorite_count=Count('favorites', distinct=True))
        .order_by('-created_at')
    )


def _favorite_ids(request, posts):
    """当前用户在「本页这些文章」里收藏过的文章 ID 集合。"""
    if not request.user.is_authenticated:
        return set()
    return set(
        request.user.favorite_posts.filter(pk__in=[post.pk for post in posts])
        .values_list('pk', flat=True)
    )


def _redirect_back(request, fallback_url):
    """安全地跳回来源页：优先表单里的 next，其次 Referer。"""
    for candidate in (request.POST.get('next'), request.META.get('HTTP_REFERER')):
        if candidate and url_has_allowed_host_and_scheme(
            candidate,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure(),
        ):
            return redirect(candidate)
    return redirect(fallback_url)


class PostListView(ListView):
    """博客首页：继承 ListView，展现文章列表。"""

    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'posts'
    paginate_by = 12

    def get_queryset(self):
        """重写查询方法：支持分类筛选 + 关键词搜索。"""
        queryset = _with_meta(super().get_queryset())

        self.category_slug = self.request.GET.get('category', '').strip()
        if self.category_slug:
            queryset = queryset.filter(category__slug=self.category_slug)

        self.keyword = self.request.GET.get('q', '').strip()
        if self.keyword:
            queryset = queryset.filter(
                Q(title__icontains=self.keyword)
                | Q(summary__icontains=self.keyword)
            )

        return queryset

    def get_context_data(self, **kwargs):
        """重写上下文方法：往模板中注入额外数据。"""
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['category_slug'] = self.category_slug
        context['keyword'] = self.keyword
        context['title'] = 'RUNOOB 博客 - 首页'
        # paginator 只有分页生效时才存在；没有分页时直接数本次结果
        context['total_count'] = (
            context['paginator'].count if context.get('paginator') else len(context['posts'])
        )
        context['favorite_ids'] = _favorite_ids(self.request, context['posts'])
        return context


class PostDetailView(DetailView):
    """文章详情页：继承 DetailView。"""

    model = Post
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'

    def get_queryset(self):
        return super().get_queryset().select_related('category')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.object

        context['title'] = post.title
        context['favorite_count'] = post.favorites.count()
        context['is_favorited'] = (
            self.request.user.is_authenticated
            and post.favorites.filter(pk=self.request.user.pk).exists()
        )
        # 同分类下的其他文章，顺便引导读者继续看
        context['related_posts'] = (
            Post.objects.filter(category=post.category)
            .exclude(pk=post.pk)
            .select_related('category')[:3]
        )
        return context


class FavoritesView(LoginRequiredMixin, ListView):
    """我的收藏：只列出当前登录用户收藏过的文章。"""

    template_name = 'blog/favorites.html'
    context_object_name = 'posts'
    paginate_by = 12

    def get_queryset(self):
        return _with_meta(self.request.user.favorite_posts.all())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = '我的收藏 - RUNOOB 博客'
        context['total_count'] = (
            context['paginator'].count if context.get('paginator') else len(context['posts'])
        )
        # 这一页的文章全部是当前用户收藏的
        context['favorite_ids'] = {post.pk for post in context['posts']}
        return context


def register(request):
    """用户注册：GET 渲染表单，POST 校验并创建用户。"""
    if request.user.is_authenticated:
        messages.info(request, '你已经登录，无需重复注册。')
        return redirect('index')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'注册成功，{user.username}！请使用新账号登录。')
            return redirect('login')
        messages.error(request, '注册信息有误，请根据下方提示修改。')
    else:
        form = RegisterForm()

    return render(request, 'blog/register.html', {'form': form, 'title': '注册 - RUNOOB 博客'})


@login_required
@require_POST
def toggle_favorite(request, pk):
    """收藏 / 取消收藏：同一个地址，点一下切换状态。"""
    post = get_object_or_404(Post, pk=pk)

    if post.favorites.filter(pk=request.user.pk).exists():
        post.favorites.remove(request.user)
        messages.info(request, f'已取消收藏《{post.title}》')
    else:
        post.favorites.add(request.user)
        messages.success(request, f'已收藏《{post.title}》')

    return _redirect_back(request, post.get_absolute_url())
