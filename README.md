# RUNOOB 博客（Django 练习项目）

一个用 Django 写的简易博客：文章列表、分类筛选、关键词搜索、分页、文章详情、
富文本编辑、用户注册 / 登录 / 登出、文章收藏。

## 环境

- Python 3.12（虚拟环境 `C:\Users\debonair\venv`）
- Django 6.1.3
- django-summernote 0.8.20（后台富文本编辑器）
- whitenoise 6.12（生产环境静态文件）
- gunicorn（Railway 上的 WSGI 服务器）

> ⚠️ 机器上还有一套全局 Python `D:\python`（Django 6.0.4，**没装 django-summernote**）。
> 用它跑本项目会报 `ModuleNotFoundError: No module named 'django_summernote'`。
> 所以下面所有命令都必须用虚拟环境里的解释器。

## 启动

### 最省事：一条命令

```powershell
cd C:\Users\debonair\blog_project
.\run.ps1              # = venv 里的 python manage.py runserver
.\run.ps1 check        # 也能传任意 manage.py 子命令
.\run.ps1 test blog
```

`run.ps1` 会自己找到同级目录的 `venv`，不依赖 activate，永远不会认错解释器。

### 手动激活（PowerShell 里必须用 `Activate.ps1`）

```powershell
cd C:\Users\debonair\blog_project
C:\Users\debonair\venv\Scripts\Activate.ps1
```

激活成功的两个标志：

1. 提示符前面出现 `(venv)`；
2. `Get-Command python` 指向 `C:\Users\debonair\venv\Scripts\python.exe`。

⚠️ **不要**写成 `...\Scripts\activate`（无扩展名）。那是给 bash 用的脚本，
PowerShell 会报 `Cannot run a document in the middle of a pipeline`，
而且**虚拟环境不会生效**，`python` 仍指向 `D:\python`，于是又报 summernote 找不到。

然后：

```powershell
python manage.py migrate
python manage.py runserver
```

### 不想改执行策略时，直接指定解释器

```powershell
C:\Users\debonair\venv\Scripts\python.exe manage.py runserver
```

### 首次安装 / 换机器

```powershell
cd C:\Users\debonair\blog_project
C:\Users\debonair\venv\Scripts\python.exe -m pip install -r requirements.txt
C:\Users\debonair\venv\Scripts\python.exe manage.py migrate
C:\Users\debonair\venv\Scripts\python.exe manage.py createsuperuser
```

打开 <http://127.0.0.1:8000/> 即可，后台在 <http://127.0.0.1:8000/admin/>。

## 路由一览

| 路径 | 名称 | 说明 |
| --- | --- | --- |
| `/` | `index` | 文章列表，支持 `?q=关键词`、`?category=slug`、`?page=n` |
| `/post/<id>/` | `post_detail` | 文章详情 |
| `/post/<id>/favorite/` | `toggle_favorite` | 收藏 / 取消收藏（仅 POST） |
| `/favorites/` | `favorites` | 我的收藏（需登录） |
| `/register/` | `register` | 注册 |
| `/login/` | `login` | 登录 |
| `/logout/` | `logout` | 登出（仅 POST） |
| `/admin/` | — | 管理后台 |
| `/summernote/` | — | 富文本编辑器上传接口 |

## 目录结构

```
blog_project/
├── blog/
│   ├── admin.py            # 后台注册（Summernote 富文本、收藏数统计）
│   ├── forms.py            # RegisterForm：注册表单 + 邮箱查重
│   ├── models.py           # Category / Post（含自动 slug、收藏多对多）
│   ├── urls.py             # 应用路由
│   ├── views.py            # 列表 / 详情 / 收藏 / 注册 / 收藏切换
│   ├── tests.py            # 26 个视图与模型测试
│   ├── migrations/
│   └── templates/blog/     # base / index / post_detail / login / register / favorites
├── blog_project/
│   ├── settings.py         # 配置（环境变量、数据库、静态文件、安全项）
│   └── urls.py             # 根路由 + 开发环境媒体文件服务
├── static/css/style.css    # 全站样式
├── staticfiles/            # collectstatic 产物（已 gitignore）
├── db.sqlite3              # 本地开发库（已 gitignore）
├── manage.py
├── run.ps1                 # 启动脚本（锁定 venv 解释器）
├── requirements.txt
├── Procfile                # Railway 启动命令
├── runtime.txt             # 指定 Python 3.12
├── .env.example            # 环境变量模板
└── .gitignore
```

## 自测

```powershell
.\run.ps1 check                              # 应输出 no issues
.\run.ps1 makemigrations --check --dry-run   # 应输出 No changes detected
.\run.ps1 test blog                          # 26 个测试，应输出 OK
```

## 推送到 GitHub

> 下面这些命令要敲进 **PowerShell 或 cmd 的窗口**里。
> 网上的教程常带 `$` 前缀（bash 提示符），**不要连 `$` 一起复制**。

### 1. 在项目里初始化仓库

```powershell
cd C:\Users\debonair\blog_project
git init
git add .
git status                # 确认没有 db.sqlite3 / staticfiles/ / venv/ / .env
git commit -m "初始化 Django 博客项目"
git branch -M main
```

### 2. 在 GitHub 上建一个空仓库

浏览器打开 <https://github.com/new>：

- Repository name：`django-blog`（或你喜欢的名字）
- **不要**勾选 “Add a README file”、也不要选 .gitignore / license（本地已经有了）

创建后拿到地址：`https://github.com/<你的用户名>/django-blog.git`

### 3. 关联远程并推送

```powershell
git remote add origin https://github.com/<你的用户名>/django-blog.git
git push -u origin main
```

第一次推送会弹出浏览器窗口让主人登录 GitHub（Git Credential Manager），
登录授权后就会自动上传并记住凭据。

> 小提示：当前 git 全局邮箱是 `debonair@localhost`，GitHub 不会把它算成主人贡献。
> 想让它显示成自己的账号，先执行：
> `git config --global user.email "你的GitHub邮箱"`，再 `git commit --amend --reset-author`。

### 4. 之后日常提交

```powershell
git add .
git commit -m "说明这次改了什么"
git push
```

## 部署到 Railway

### 1. 创建项目

1. 打开 <https://railway.app>，用 **GitHub 账号**登录；
2. `New Project` → `Deploy from GitHub repo` → 授权并选择刚推上去的 `django-blog`；
3. Railway 用 Nixpacks 自动识别 Python 项目，读取 `requirements.txt` 装依赖，
   启动命令来自 `Procfile`：
   `collectstatic` → `migrate` → `gunicorn blog_project.wsgi:application`。

### 2. 加一个 PostgreSQL 数据库（重要）

Railway 的容器文件系统是**临时的**，`db.sqlite3` 每次部署都会被清空，所以必须换成 Postgres：

1. 项目页面 → `+ New` → `Database` → `Add PostgreSQL`；
2. 回到 Web 服务 → `Variables` → `New Variable` → `Add Reference` → 选 `Postgres` → `DATABASE_URL`。

`settings.py` 检测到 `DATABASE_URL` 就会自动切到 Postgres，本地没这个变量时仍用 sqlite。

### 3. 设置环境变量

Web 服务 → `Variables`：

| 变量 | 值 | 说明 |
| --- | --- | --- |
| `DJANGO_DEBUG` | `0` | 关掉调试模式，必须设 |
| `DJANGO_SECRET_KEY` | 一长串随机字符 | 见下面生成方法 |
| `DJANGO_SECURE_COOKIES` | `1` | 走 HTTPS 时保持 1 |
| `DJANGO_ALLOWED_HOSTS` | 留空 | Railway 会自动注入 `RAILWAY_PUBLIC_DOMAIN`；用自定义域名时才填 |
| `DATABASE_URL` | Reference → Postgres | 上一步配好 |

生成随机密钥（本地 PowerShell 里跑）：

```powershell
C:\Users\debonair\venv\Scripts\python.exe -c "import secrets; print(secrets.token_urlsafe(50))"
```

### 4. 生成域名并部署

服务 → `Settings` → `Networking` → `Generate Domain`，拿到类似
`django-blog-production-xxxx.up.railway.app` 的地址；`Deploy` 完成后访问它即可。

### 5. 创建管理员账号

部署完成后，在服务页面用 `Shell`（或本地装 Railway CLI 后 `railway run ...`）执行：

```bash
python manage.py createsuperuser
```

然后访问 `https://<你的域名>/admin/` 登录后台发文章。

### 部署注意事项

- `media/`（Summernote 上传的插图）在 Railway 上也是临时的，重启会丢；
  正式用请接 S3 / Cloudinary 等对象存储。
- `staticfiles/` 不入库，构建/启动时由 `collectstatic` 生成，WhiteNoise 负责分发。
- `DEBUG=0` 时 Django 要求 `ALLOWED_HOSTS` 正确，否则会返回 400；
  Railway 域名自动注入，自定义域名记得加进 `DJANGO_ALLOWED_HOSTS`。
- 如果构建时 `pip` 报找不到 `Django==6.1.3`，把 `requirements.txt` 里的版本号放宽
  成 `Django>=5.2,<7` 再推一次。

## 常见报错速查

| 报错 | 原因 | 解决 |
| --- | --- | --- |
| `'$' 不是内部或外部命令` | 把 bash 提示符 `$` 一起复制进 cmd 了 | 只复制 `$` 后面的内容 |
| `'staticfiles' 不是内部或外部命令` | 把 `.gitignore` 的内容当命令敲进终端了 | 那些行要写进 `.gitignore` 文件，不是命令 |
| `ModuleNotFoundError: No module named 'django_summernote'` | 用了 `D:\python` 的全局 Python | 用 `.\run.ps1`，或先 `Activate.ps1` |
| `You are trying to add a non-nullable field` | 改了模型没生成迁移 | `.\run.ps1 makemigrations` + `migrate` |
| `DisallowedHost` / 400 | `ALLOWED_HOSTS` 没包含访问的域名 | 加 `DJANGO_ALLOWED_HOSTS` 或设 `RAILWAY_PUBLIC_DOMAIN` |
