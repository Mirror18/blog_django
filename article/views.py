from django.shortcuts import render

# Create your views here.

# 导入HttpResponse模块
from django.http import HttpResponse

# 导入数据模型ArticlePost
from .models import ArticlePost

# 引入markdown模块
import markdown

# 引入分页模块
from django.core.paginator import Paginator
# 引入 Q 对象
from django.db.models import Q


# 视图函数
def article_list(request):
    # # 返回一个包含被请求页面内容的HttpResponse对象
    # # 或者抛出一个异常
    # # request 与网页发来的请求有关，里面包含get或者post的内容
    # # 还需配置URLconfs，将用户请求的url链接关联起来
    # # url已经分发给了article应用。所以修改article/urls.py就可以
    #
    # # 取出所有的博客文章
    # # ArticlePost.objects.all()是数据累的方法
    # # 可获得所有的对象-博客文章-，并传递给articles变量
    # # articles = ArticlePost.objects.all()
    #
    # # 修改变量名称（articles -> article_list）
    # # article_list = ArticlePost.objects.all()
    #
    # # 根据GET请求中查询条件
    # # 返回不同排序的对象数组
    # # 前面用过GET请求传递单个参数。
    # # 它也是可以传递多个参数的，
    # # 如?a = 1 & b = 2，参数间用 & 隔开
    # if request.GET.get('order') == 'total_views':
    #     # 视图根据GET参数order的值，判断取出的文章如何排序
    #     # order_by() 方法指定对象如何进行排序。模型中有total_views这个整数字段，
    #     # 因此‘total_views’为正序，‘-total_views’为逆序
    #     article_list = ArticlePost.objects.all().order_by('-total_views')
    #     order = 'total_views'
    # else:
    #     article_list = ArticlePost.objects.all()
    #     order = 'normal'

    # 新增参数search，存放需要搜索的文本。若search不为空，则检索特定文章对象。
    # 从 url 中提取查询参数
    search = request.GET.get('search')
    order = request.GET.get('order')
    column = request.GET.get('column')
    tag = request.GET.get('tag')

    # 初始化查询集
    article_list = ArticlePost.objects.all()

    # 搜索查询集
    if search:
        article_list = article_list.filter(
            Q(title__icontains=search) |
            Q(body__icontains=search)
        )
    else:
        search = ''

    # 栏目查询集
    if column is not None and column.isdigit():
        article_list = article_list.filter(column=column)

    # 标签查询集
    if tag and tag != 'None':
        article_list = article_list.filter(tags__name__in=[tag])

    # 查询集排序
    if order == 'total_views':
        article_list = article_list.order_by('-total_views')

    # # 用户搜索逻辑
    # if search:
    #     if order == 'total_views':
    #         # 用 Q对象 进行联合搜索
    #         article_list = ArticlePost.objects.filter(
    #             # 意思是在模型的title字段查询，
    #             # icontains是不区分大小写的包含，
    #             # 中间用两个下划线隔开。
    #             # search是需要查询的文本。
    #             # 多个Q对象用管道符 | 隔开，
    #             # 就达到了联合查询的目的。
    #             Q(title__icontains=search) |
    #             Q(body__icontains=search)
    #         ).order_by('-total_views')
    #     else:
    #         article_list = ArticlePost.objects.filter(
    #             Q(title__icontains=search) |
    #             Q(body__icontains=search)
    #         )
    # else:
    #     # 将 search 参数重置为空
    #     search = ''
    #     if order == 'total_views':
    #         article_list = ArticlePost.objects.all().order_by('-total_views')
    #     else:
    #         article_list = ArticlePost.objects.all()

    # 每页显示 3 篇文章
    paginator = Paginator(article_list, 3)
    # 获取 url 中的页码
    page = request.GET.get('page')
    # 将导航对象相应的页码内容返回给 articles
    articles = paginator.get_page(page)

    # 需要传递给模板 templates 的对象
    # context定义了需要传递给模板的上下文，这里即是articles
    # context = {'articles': articles}

    # order给模板一个标识，提醒模板下一页应该如何排序
    # 文章需要翻页！
    # context = {'articles': articles, 'order': order}

    # 增加 search 到 context
    context = {
        'articles': articles,
        'order': order,
        'search': search,
        'column': column,
        'tag': tag,
    }

    # render函数:载入模板，并返回context对象
    # 作用是 结合模板和上下文，并返回渲染后的HttpResponse对象
    # 就是把context的内容，加载进模板，并通过浏览器呈现
    # request 是固定的 request对象
    # article/list.html定义了模板文件的位置。名称
    # context定义了需要传入模板文件的上下文
    return render(request, 'article/list.html', context)


from comment.models import Comment
# 引入评论表单
from comment.forms import CommentForm

from django.shortcuts import get_object_or_404


# 文章详情
def article_detail(request, id):
    # 取出相应的文章
    # Django 自动生成的用于索引数据表的主键 primary key 即pk
    # 有了它才知道是取出那篇文章
    # 在所有文章中，取出id 值复合的唯一一篇文章
    # article = ArticlePost.objects.get(id=id)
    article = get_object_or_404(ArticlePost, id=id)

    # 过滤出所有的id比当前文章小的文章
    pre_article = ArticlePost.objects.filter(id__lt=article.id).order_by('-id')
    # 过滤出id大的文章
    next_article = ArticlePost.objects.filter(id__gt=article.id).order_by('id')

    # 取出相邻前一篇文章
    if pre_article.count() > 0:
        pre_article = pre_article[0]
    else:
        pre_article = None

    # 取出相邻后一篇文章
    if next_article.count() > 0:
        next_article = next_article[0]
    else:
        next_article = None

    # 取出文章评论
    # filter()可以取出多个满足条件的对象，而get()只能取出1个
    comments = Comment.objects.filter(article=id)

    # 浏览量 +1
    article.total_views += 1
    update_fields = []
    # 指定了数据库只更新total_views字段，优化执行效率
    article.save(update_fields=['total_views'])

    # 将markdown语法渲染成html样式
    # 接收两个参数
    # 第一个参数是需要 渲染 的文章正文 article.body
    # 第二个参数 载入了常用的语法拓展
    # markdown.extensions.extra 中包含了 缩写， 表格 等拓展
    # markdown.extensions.codehilite 则是代码高亮拓展
    # article.body = markdown.markdown(article.body,
    #                                  extensions=[
    #                                      # 包含 缩写、表格等常用扩展
    #                                      'markdown.extensions.extra',
    #                                      # 语法高亮扩展
    #                                      'markdown.extensions.codehilite',
    #                                      # 目录扩展
    #                                      'markdown.extensions.toc',
    #                                  ]
    #                                  )
    md = markdown.Markdown(
        extensions=[
            'markdown.extensions.extra',
            'markdown.extensions.codehilite',
            'markdown.extensions.toc',
        ]
    )
    # convert()方法将正文渲染为html页面
    article.body = md.convert(article.body)

    # 为评论引入表单
    comment_form = CommentForm()

    # 需要传递给模板的对象
    # context = {'article': article}
    # # 新增了md.toc对象
    # context = {'article': article, 'toc': md.toc}
    # 添加comments上下文
    context = {
        'article': article,
        'toc': md.toc,
        'comments': comments,
        'comment_form': comment_form,

        'pre_article': pre_article,
        'next_article': next_article,
    }

    # 载入模板，并返回context对象
    return render(request, 'article/detail.html', context)


# 当视图函数接受到一个客户端的 request 请求事
# 首先根据 request.method 判断用户是 post 提交数据，还是 get 获取数据
# 用户是提交数据。 将 post 给服务器的表单数据赋予 article_post_form 实例
# is_valid() 判断提交数据是否满足模型的要求
# 如果满足要求，保存表单中的数据 commit=false 暂时不提交数据库， 因为author还未指定
# 指定 author 为 ID=1 的管理员用户
# 提交到数据库，通过 redirect 返回文章列表。 通过url地址的名字， 反向解析到对应的url
# 如果是获取数据， 泽返回一个空的表单类对象， 提供给用户填写

# 引入redirect重定向模块
from django.shortcuts import render, redirect
# 引入HttpResponse
from django.http import HttpResponse
# 引入刚才定义的ArticlePostForm表单类
from .forms import ArticlePostForm
# 引入User模型
from django.contrib.auth.models import User

from django.contrib.auth.decorators import login_required
# 引入栏目Model
from .models import ArticleColumn


# 写文章的视图
# 检查登录
@login_required(login_url='/userprofile/login/')
def article_create(request):
    # 判断用户是否提交数据
    if request.method == "POST":
        # 将提交的数据赋值到表单实例中
        article_post_form = ArticlePostForm(request.POST, request.FILES)
        # 判断提交的数据是否满足模型的要求
        if article_post_form.is_valid():
            # 保存数据，但暂时不提交到数据库中
            new_article = article_post_form.save(commit=False)
            # 指定数据库中 id=1 的用户为作者
            # 如果你进行过删除数据表的操作，可能会找不到id=1的用户
            # 此时请重新创建用户，并传入此用户的id
            # new_article.author = User.objects.get(id=1)
            # 指定目前登录的用户为作者
            new_article.author = User.objects.get(id=request.user.id)

            # 栏目
            # POST：主要考虑某些文章是可以没有栏目的。因此用if语句判断该文章是否有栏目，如果有，则根据表单提交的value值，关联对应的栏目。
            if request.POST['column'] != 'none':
                new_article.column = ArticleColumn.objects.get(id=request.POST['column'])

            # 将新文章保存到数据库中
            new_article.save()
            # 保存 tags 的多对多关系
            article_post_form.save_m2m()
            # 完成后返回到文章列表
            return redirect("article:article_list")
        # 如果数据不合法，返回错误信息
        else:
            return HttpResponse("表单内容有误，请重新填写。")
    # 如果用户请求获取数据
    else:
        # 创建表单类实例
        article_post_form = ArticlePostForm()
        # GET：增加栏目的上下文，以便模板使用。
        columns = ArticleColumn.objects.all()
        # 赋值上下文
        # context = {'article_post_form': article_post_form}
        context = {'article_post_form': article_post_form, 'columns': columns}
        # 返回模板
        return render(request, 'article/create.html', context)

    # form 实例可以绑定到数据
    # 如果绑定导数据， 就能验证该数据 并将表单呈现为 html 并显示数据
    # 如果未绑定，则无法进行验证， 但是仍然可以将空白表但呈现为HTML


# 删文章
@login_required(login_url='/userprofile/login/')
def article_delete(request, id):
    # 根据 id 获取需要删除的文章
    article = ArticlePost.objects.get(id=id)
    # 调用.delete()方法删除文章
    article.delete()
    # 完成删除后返回文章列表
    return redirect("article:article_list")


# 安全删除文章
@login_required(login_url='/userprofile/login/')
def article_safe_delete(request, id):
    if request.method == 'POST':
        article = ArticlePost.objects.get(id=id)
        article.delete()
        return redirect("article:article_list")
    else:
        return HttpResponse("仅允许post请求")


# 更新文章
# 提醒用户登录
# login_required装饰器过滤未登录的用户
# if 语句过滤已登录、但非作者本人的用户
@login_required(login_url='/userprofile/login/')
def article_update(request, id):
    """
    更新文章的视图函数
    通过POST方法提交表单，更新titile、body字段
    GET方法进入初始表单页面
    id： 文章的 id

    文章的 id 作为参数传递进来了
    用户POST提交表单时没有创建新的文章，而是在之前的文章中修改
    redirect函数没有返回文章列表，而是返回到修改后的文章页面去了，因此需要同时把文章的id也打包传递进去，这是url所规定的
    GET获取页面时将article对象也传递到模板中去，以便后续的调用
    """

    # 获取需要修改的具体文章对象
    article = ArticlePost.objects.get(id=id)

    # 过滤非作者的用户
    if request.user != article.author:
        return HttpResponse("抱歉，你无权修改这篇文章。")

    # 判断用户是否为 POST 提交表单数据
    if request.method == "POST":
        # 将提交的数据赋值到表单实例中
        article_post_form = ArticlePostForm(data=request.POST)
        # 判断提交的数据是否满足模型的要求
        if article_post_form.is_valid():
            # 保存新写入的 title、body 数据并保存
            article.title = request.POST['title']
            article.body = request.POST['body']

            if request.POST['column'] != 'none':
                # 保存文章栏目
                article.column = ArticleColumn.objects.get(id=request.POST['column'])
            else:
                article.column = None
            # 缩略图
            if request.FILES.get('avatar'):
                article.avatar = request.FILES.get('avatar')

            article.tags.set(*request.POST.get('tags').split(','), clear=True)
            article.save()
            # 完成后返回到修改后的文章中。需传入文章的 id 值
            return redirect("article:article_detail", id=id)
        # 如果数据不合法，返回错误信息
        else:
            return HttpResponse("表单内容有误，请重新填写。")

    # 如果用户 GET 请求获取数据
    else:
        # 创建表单类实例
        article_post_form = ArticlePostForm()
        # 文章栏目
        columns = ArticleColumn.objects.all()
        # 赋值上下文，将 article 文章对象也传递进去，以便提取旧的内容
        context = {
            'article': article,
            'article_post_form': article_post_form,
            'columns': columns,
            'tags': ','.join([x for x in article.tags.names()]),
        }

        # 将响应返回到模板中
        return render(request, 'article/update.html', context)


# 通用类视图
from django.views import View
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView


# 点赞数 +1
class IncreaseLikesView(View):
    def post(self, request, *args, **kwargs):
        article = ArticlePost.objects.get(id=kwargs.get('id'))
        article.likes += 1
        article.save()
        return HttpResponse('success')
