from django.contrib import admin

# Register your models here.

from .models import ArticlePost

# 注册ArticlePost到admin中
# 就是告诉Django，后台需要添加ArticlePost这个数据表供于管理
admin.site.register(ArticlePost)

# 。由于还没有写视图，因此需要善加利用Django自带的后台。
from .models import ArticleColumn

# 注册文章栏目
admin.site.register(ArticleColumn)
