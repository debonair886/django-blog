# 文件路径：blog/tests.py
"""blog 应用的自动化测试。

运行：python manage.py test blog -v 2
"""

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Category, Post


class BlogTestDataMixin:
    """各测试类共用的初始化数据。"""

    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name='Django', slug='django')
        cls.other_category = Category.objects.create(name='Python', slug='python')
        cls.post = Post.objects.create(
            title='第一篇 Django 文章',
            slug='first-post',
            summary='这是摘要',
            content='<p>这是正文</p>',
            category=cls.category,
        )
        cls.user = User.objects.create_user(
            'tester', email='tester@example.com', password='test-pass-123'
        )
        cls.other_user = User.objects.create_user('other', password='test-pass-123')


class PostListViewTests(BlogTestDataMixin, TestCase):
    def test_index_renders_list(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/index.html')
        self.assertContains(response, '第一篇 Django 文章')

    def test_search_filters_title_and_summary(self):
        response = self.client.get(reverse('index'), {'q': 'Django'})
        self.assertContains(response, '第一篇 Django 文章')

        response = self.client.get(reverse('index'), {'q': '不存在的关键词'})
        self.assertNotContains(response, '第一篇 Django 文章')
        self.assertContains(response, '没有找到匹配的文章')

    def test_category_filter(self):
        response = self.client.get(reverse('index'), {'category': 'python'})
        self.assertNotContains(response, '第一篇 Django 文章')

        response = self.client.get(reverse('index'), {'category': 'django'})
        self.assertContains(response, '第一篇 Django 文章')

    def test_pagination(self):
        for i in range(14):
            Post.objects.create(
                title=f'批量文章 {i}',
                slug=f'bulk-{i}',
                content='正文',
                category=self.category,
            )

        first_page = self.client.get(reverse('index'))
        self.assertEqual(len(first_page.context['posts']), 12)   # paginate_by = 12
        self.assertTrue(first_page.context['is_paginated'])

        second_page = self.client.get(reverse('index'), {'page': 2})
        self.assertEqual(len(second_page.context['posts']), 3)

    def test_total_count_in_context(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.context['total_count'], 1)


class PostDetailViewTests(BlogTestDataMixin, TestCase):
    def test_detail_page(self):
        response = self.client.get(self.post.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/post_detail.html')
        self.assertContains(response, '第一篇 Django 文章')
        self.assertEqual(response.context['post'], self.post)

    def test_missing_post_returns_404(self):
        response = self.client.get(reverse('post_detail', args=[9999]))
        self.assertEqual(response.status_code, 404)

    def test_related_posts_only_same_category(self):
        Post.objects.create(
            title='另一篇 Django 文章',
            slug='second-post',
            content='正文',
            category=self.category,
        )
        Post.objects.create(
            title='Python 文章',
            slug='python-post',
            content='正文',
            category=self.other_category,
        )
        response = self.client.get(self.post.get_absolute_url())
        related_titles = [post.title for post in response.context['related_posts']]
        self.assertEqual(related_titles, ['另一篇 Django 文章'])


class RegisterViewTests(BlogTestDataMixin, TestCase):
    def test_register_page_renders_form(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/register.html')
        self.assertIn('email', response.context['form'].fields)

    def test_register_success(self):
        response = self.client.post(
            reverse('register'),
            {
                'username': 'newbie',
                'email': 'newbie@example.com',
                'password1': 'a-very-strong-pass-1',
                'password2': 'a-very-strong-pass-1',
            },
        )
        self.assertRedirects(response, reverse('login'))
        user = User.objects.get(username='newbie')
        self.assertEqual(user.email, 'newbie@example.com')
        # 注册后能用新密码登录
        self.assertTrue(self.client.login(username='newbie', password='a-very-strong-pass-1'))

    def test_register_password_mismatch(self):
        response = self.client.post(
            reverse('register'),
            {
                'username': 'newbie',
                'email': 'newbie@example.com',
                'password1': 'a-very-strong-pass-1',
                'password2': 'different-pass-2',
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='newbie').exists())

    def test_register_duplicate_email_rejected(self):
        response = self.client.post(
            reverse('register'),
            {
                'username': 'newbie',
                'email': 'TESTER@example.com',
                'password1': 'a-very-strong-pass-1',
                'password2': 'a-very-strong-pass-1',
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('email', response.context['form'].errors)

    def test_logged_in_user_redirected_from_register(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('register'))
        self.assertRedirects(response, reverse('index'))


class AuthTests(BlogTestDataMixin, TestCase):
    def test_login_page(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/login.html')

    def test_login_then_logout(self):
        response = self.client.post(
            reverse('login'), {'username': 'tester', 'password': 'test-pass-123'}
        )
        self.assertRedirects(response, reverse('index'))

        # 登出必须是 POST（Django 5.0 起 GET 会返回 405）
        self.assertEqual(self.client.get(reverse('logout')).status_code, 405)
        response = self.client.post(reverse('logout'))
        self.assertRedirects(response, reverse('index'))


class FavoriteTests(BlogTestDataMixin, TestCase):
    def test_anonymous_cannot_favorite(self):
        response = self.client.post(reverse('toggle_favorite', args=[self.post.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)
        self.assertEqual(self.post.favorites.count(), 0)

    def test_toggle_favorite_adds_and_removes(self):
        self.client.force_login(self.user)

        self.client.post(reverse('toggle_favorite', args=[self.post.pk]))
        self.assertTrue(self.post.favorites.filter(pk=self.user.pk).exists())

        self.client.post(reverse('toggle_favorite', args=[self.post.pk]))
        self.assertFalse(self.post.favorites.filter(pk=self.user.pk).exists())

    def test_favorite_redirects_back_to_next(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse('toggle_favorite', args=[self.post.pk]),
            {'next': self.post.get_absolute_url()},
        )
        self.assertRedirects(response, self.post.get_absolute_url())

    def test_toggle_favorite_requires_post(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('toggle_favorite', args=[self.post.pk]))
        self.assertEqual(response.status_code, 405)

    def test_detail_shows_favorite_state(self):
        self.post.favorites.add(self.user)
        self.client.force_login(self.user)
        response = self.client.get(self.post.get_absolute_url())
        self.assertTrue(response.context['is_favorited'])
        self.assertEqual(response.context['favorite_count'], 1)

    def test_favorites_page_lists_only_own(self):
        self.post.favorites.add(self.user)
        self.client.force_login(self.user)

        response = self.client.get(reverse('favorites'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/favorites.html')
        self.assertContains(response, '第一篇 Django 文章')

        self.client.force_login(self.other_user)
        response = self.client.get(reverse('favorites'))
        self.assertNotContains(response, '第一篇 Django 文章')

    def test_favorites_page_requires_login(self):
        response = self.client.get(reverse('favorites'))
        self.assertEqual(response.status_code, 302)


class ModelTests(BlogTestDataMixin, TestCase):
    def test_str_and_absolute_url(self):
        self.assertEqual(str(self.post), '第一篇 Django 文章')
        self.assertEqual(
            self.post.get_absolute_url(),
            reverse('post_detail', kwargs={'pk': self.post.pk}),
        )

    def test_slug_generated_when_missing(self):
        post = Post.objects.create(
            title='中文标题也能自动生成',
            content='正文',
            category=self.category,
        )
        self.assertTrue(post.slug)
        self.assertNotEqual(post.slug, 'first-post')

    def test_duplicate_generated_slug_gets_suffix(self):
        first = Post.objects.create(title='重复标题', content='正文', category=self.category)
        second = Post.objects.create(title='重复标题', content='正文', category=self.category)
        self.assertNotEqual(first.slug, second.slug)

    def test_was_updated_flag(self):
        self.assertFalse(self.post.was_updated)
