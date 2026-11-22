# 文件路径：blog/admin.py
from django.contrib import admin
from django.db.models import Count
from django_summernote.admin import SummernoteModelAdmin

from .models import Category, Post


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    # 列表页显示的列
    list_display = ['name', 'slug', 'post_count']
    search_fields = ['name']

    def get_queryset(self, request):
        # 一次 annotate 出文章数，避免 list_display 里逐行再查
        return super().get_queryset(request).annotate(
            post_count=Count('posts', distinct=True)
        )

    @admin.display(description='文章数')
    def post_count(self, obj):
        return obj.post_count

    def get_form(self, request, obj=None, **kwargs):
        """slug 允许留空：留空时模型会按分类名自动生成。"""
        form = super().get_form(request, obj, **kwargs)
        if 'slug' in form.base_fields:
            form.base_fields['slug'].required = False
            form.base_fields['slug'].help_text = '留空时会根据分类名自动生成'
        return form


@admin.register(Post)
class PostAdmin(SummernoteModelAdmin):
    list_display = ['title', 'category', 'favorite_count', 'created_at']
    list_filter = ['category', 'created_at']
    search_fields = ['title', 'summary']
    summernote_fields = ['content']          # content 字段使用富文本编辑器
    date_hierarchy = 'created_at'
    list_select_related = ['category']

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            favorite_count=Count('favorites', distinct=True)
        )

    @admin.display(description='收藏数')
    def favorite_count(self, obj):
        return obj.favorite_count

    def get_form(self, request, obj=None, **kwargs):
        """slug 允许留空：留空时模型会按标题自动生成。"""
        form = super().get_form(request, obj, **kwargs)
        if 'slug' in form.base_fields:
            form.base_fields['slug'].required = False
            form.base_fields['slug'].help_text = '留空时会根据标题自动生成'
        return form
