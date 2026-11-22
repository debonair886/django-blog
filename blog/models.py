# 文件路径：blog/models.py
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


def _unique_slug(model, base, max_length, pk=None):
    """生成一个在 model 里不重复的 slug（中文标题 slugify 后为空时用默认值）。"""
    base = (base or 'item')[:max_length - 4]
    candidate = base
    suffix = 2
    while model.objects.filter(slug=candidate).exclude(pk=pk).exists():
        candidate = f'{base}-{suffix}'
        suffix += 1
    return candidate


class Category(models.Model):
    """文章分类"""

    name = models.CharField('分类名', max_length=50, unique=True)
    # slug 用于 URL 中的英文标识（如 /?category=django），留空时保存阶段自动生成
    slug = models.SlugField('URL 标识', max_length=50, unique=True)

    class Meta:
        verbose_name = '分类'
        verbose_name_plural = '分类'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = _unique_slug(Category, slugify(self.name) or 'category', 50, self.pk)
        super().save(*args, **kwargs)


class Post(models.Model):
    """博客文章"""

    # 标题：CharField 用于短文本，max_length 必填
    title = models.CharField('标题', max_length=200)

    # slug：文章在 URL 中的英文标识（留空时保存阶段自动生成）
    slug = models.SlugField('URL 标识', max_length=200, unique=True)

    # 摘要：TextField 用于长文本，blank=True 表示可选
    summary = models.TextField('摘要', blank=True)

    # 正文：TextField 不限长度
    content = models.TextField('正文')

    # 分类：ForeignKey 一对多关系，一篇文章属于一个分类
    # on_delete=models.CASCADE：删除分类时，其下所有文章也一并删除
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        verbose_name='分类',
        related_name='posts',    # 反向查询：category.posts.all()
    )

    # auto_now_add：创建时自动填入当前时间
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    # auto_now：每次保存时自动更新为当前时间
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    # 收藏：多对多关系，一个用户可收藏多篇文章
    favorites = models.ManyToManyField(
        User,
        related_name='favorite_posts',  # 反向查询：user.favorite_posts.all()
        verbose_name='收藏者',
        blank=True,
    )

    class Meta:
        verbose_name = '文章'
        verbose_name_plural = '文章'
        # 默认按创建时间倒序排列
        ordering = ['-created_at']

    def __str__(self):
        # 在 Admin 后台和 Shell 中显示对象时，显示标题
        return self.title

    def save(self, *args, **kwargs):
        # 后台 / Shell 里没填 slug 时，根据标题自动生成一个不重复的
        if not self.slug:
            self.slug = _unique_slug(Post, slugify(self.title) or 'post', 200, self.pk)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        # reverse 根据路由名称和参数反查 URL
        return reverse('post_detail', kwargs={'pk': self.pk})

    @property
    def was_updated(self):
        """创建后又改过内容时返回 True（auto_now_add / auto_now 会差几微秒）。"""
        return (self.updated_at - self.created_at).total_seconds() > 1
