# 文件路径：blog/urls.py
from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    # CBV：类后面加 .as_view() 把它变成视图函数
    path('', views.PostListView.as_view(), name='index'),
    path('post/<int:pk>/', views.PostDetailView.as_view(), name='post_detail'),

    # 收藏（POST）：文章详情页和列表页都指向它
    path('post/<int:pk>/favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('favorites/', views.FavoritesView.as_view(), name='favorites'),

    # 认证：注册自己写，登录 / 登出用 Django 内置视图
    path('register/', views.register, name='register'),
    path(
        'login/',
        auth_views.LoginView.as_view(
            template_name='blog/login.html',
            redirect_authenticated_user=True,
        ),
        name='login',
    ),
    # 注意：Django 5.0 起 LogoutView 只接受 POST，模板里必须用表单提交
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
