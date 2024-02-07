from django.db import models

# Create your models here.
# 导入内建的User模型
from django.contrib.auth.models import User
# timezone用于处理时间相关事务
from django.utils import timezone

from django.urls import reverse
# Django-taggit
from taggit.managers import TaggableManager

from PIL import Image


class ArticleColumn(models.Model):
    """
    栏目的 Model
    """
    # 栏目标题
    title = models.CharField(max_length=100, blank=True)
    # 创建时间
    created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title


# 引入imagekit
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFit


# Django中所有的模型(Model)都必须继承django.db.models.Model模型，即顶部的导入
# 建立博客文章类 class Article，处理与文章有关的数据，它包含需要的字段和保存数据的行为
# 博客文章数据模型
class ArticlePost(models.Model):
    # 文章作者。
    # author通过 models.ForeignKey 外键与内建的User 模型关联在一起
    # 参数on_delete用于指定数据删除的方式
    # 避免两个关联表的数据不一致。
    # 通常设置为CASCADE 级链删除即可
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    # 文章栏目的 “一对多” 外键
    # 一篇文章只有一个栏目，而一个栏目可以对应多篇文章，因此建立“一对多”的关系
    column = models.ForeignKey(
        ArticleColumn,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='article'
    )

    # 文章标签
    tags = TaggableManager(blank=True)

    # 文章标题图
    # 手写的
    avatar = models.ImageField(
        upload_to='article/%Y%m%d/',
        blank=True
    )
    # 自动的
    # avatar = ProcessedImageField(
    #     upload_to='article/%Y%m%d',
    #     processors=[ResizeToFit(width=400)],
    #     format='JPEG',
    #     options={'quality': 100},
    # )

    # 文章标题。
    # models.CharField为字符串字段，用于保存较短的字符串，比如标题
    # CharField 有一个必填参数 max_length。 他规定字符的最大长度
    title = models.CharField(max_length=100)

    # 文章正文。
    # 保存大量文本使用TextField
    body = models.TextField()

    # 文章创建时间。
    # DateTimeField 为一个日期字段
    # 参数default=timezone.now指定其在创建数据时默认写入当前时间
    created = models.DateTimeField(default=timezone.now)

    # 文章更新时间。
    # 参数auto_now=True指定每次数据更新时自动写入当前时间
    updated = models.DateTimeField(auto_now=True)

    # 统计文章浏览量
    # PositiveIntegerField是用于存储正整数的字段
    # default = 0 设定初始值从0开始
    total_views = models.PositiveIntegerField(default=0)

    # 新增点赞数统计
    likes = models.PositiveIntegerField(default=0)

    # 内部类class Meta用于给model定义元数据
    # 元数据：不是一个字段的任何数据
    class Meta:
        # ordering指定模型返回的数据的排列顺序
        # -created表明数据应该以倒序排序
        ordering = ('-created',)

    # 函数__str__定义当调用对象的str()方法时返回值内容
    # 它最常见的就是在Django管理后台中做为对象的显示值。
    # 因此应该总是为 __str__ 返回一个友好易读的字符串
    def __str__(self):
        # return self.title将文章标题返回
        return self.title

    # 获取文章地址
    def get_absolute_url(self):
        return reverse('article:article_detail', args=[self.id])

    # 保存时处理图片
    def save(self, *args, **kwargs):
        # 调用原有的 save() 的功能
        # 在model实例每次保存时调用。这里改写它，将处理图片的逻辑“塞进去”。
        # 作用是调用父类中原有的save() 方法，即将model中的字段数据保存到数据库中。因为图片处理是基于已经保存的图片的，所以这句一定要在处理图片之前执行，
        article = super(ArticlePost, self).save(*args, **kwargs)

        # 固定宽度缩放图片大小
        # 剔除掉没有标题图的文章，这些文章不需要处理图片。
        # article_detail()视图中为了统计浏览量而调用了save(update_fields=['total_views'])
        # 就是为了排除掉统计浏览量调用的save()，免得每次用户进入文章详情页面都要处理标题图，太影响性能了。
        if self.avatar and not kwargs.get('update_fields'):
            image = Image.open(self.avatar)
            (x, y) = image.size
            new_x = 400
            new_y = int(new_x * (y / x))
            resized_image = image.resize((new_x, new_y), Image.ANTIALIAS)
            resized_image.save(self.avatar.path)

        return article

# 有bug 未来的不行
    def was_created_recently(self):
        # 若文章是"最近"发表的，则返回 True
        diff = timezone.now() - self.created
        # if diff.days <= 0 and diff.seconds < 60:
        if diff.days == 0 and 0 <= diff.seconds < 60:
            return True
        else:
            return False