# 文件路径：blog/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class RegisterForm(UserCreationForm):
    """自定义注册表单：在 UserCreationForm 基础上增加邮箱字段。"""

    email = forms.EmailField(
        label='邮箱',
        required=True,
        help_text='请输入有效的邮箱地址，便于以后找回密码。',
        widget=forms.EmailInput(attrs={'autocomplete': 'email'}),
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        labels = {
            'username': '用户名',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 给所有输入框补上占位提示，模板里就不用逐个写 widget
        self.fields['username'].widget.attrs.setdefault(
            'placeholder', '字母、数字或 @/./+/-/_，150 字以内'
        )
        self.fields['password1'].widget.attrs.setdefault('placeholder', '至少 8 位，别用纯数字')
        self.fields['password2'].widget.attrs.setdefault('placeholder', '再输入一次密码')

    def clean_email(self):
        """邮箱不允许重复注册。"""
        email = self.cleaned_data['email'].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('该邮箱已被注册，请更换一个。')
        return email
