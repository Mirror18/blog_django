from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from article.models import ArticlePost
from .forms import CommentForm

from .models import Comment

from notifications.signals import notify
from django.contrib.auth.models import User
# 引入JsonResponse
from django.http import JsonResponse


# 文章评论
# def post_comment(request, article_id):
@login_required(login_url='/userprofile/login/')
# parent_comment_id=None。此参数代表父评论的id值
def post_comment(request, article_id, parent_comment_id=None):
    article = get_object_or_404(ArticlePost, id=article_id)
    # get_object_or_404()：它和Model.objects.get()的功能基本是相同的
    # 生产环境下，
    # 如果用户请求一个不存在的对象时，Model.objects.get() 会返回Error 500
    # （服务器内部错误），而get_object_or_404()  会返回Error 404

    # 处理 POST 请求
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.article = article
            new_comment.user = request.user
            # 二级回复
            # 如果视图处理的是多级评论，则用MPTT的get_root()
            # 方法将其父级重置为树形结构最底部的一级评论
            if parent_comment_id:
                parent_comment = Comment.objects.get(id=parent_comment_id)
                # 若回复层级超过二级，则转换为二级
                # reply_to中保存实际的被回复人并保存
                new_comment.parent_id = parent_comment.get_root().id
                # 被回复人
                new_comment.reply_to = parent_comment.user
                new_comment.save()

                # 给其他用户发送通知
                # notify.send(actor, recipient, verb, target, action_object)
                # 其中的参数释义：
                # actor：发送通知的对象
                # recipient：接收通知的对象
                # verb：动词短语
                # target：链接到动作的对象（可选）
                # action_object：执行通知的对象（可选）
                # 用户之间可以互相评论，因此需要发送通知。if语句是为了防止管理员收到重复的通知。
                if not parent_comment.user.is_superuser and not parent_comment.user == request.user:
                    notify.send(
                        request.user,
                        recipient=parent_comment.user,
                        verb='回复了你',
                        target=article,
                        action_object=new_comment,
                    )

                # 是HttpResponse字符串
                # return HttpResponse('200 OK')
                # 返回的是json格式的数据，由它将新评论的id传递出去。
                return JsonResponse({"code": "200 OK", "new_comment_id": new_comment.id})

            new_comment.save()

            # 给管理员发送通知
            # 普通用户回复时给管理员发送通知。
            if not request.user.is_superuser:
                notify.send(
                    request.user,
                    recipient=User.objects.filter(is_superuser=1),
                    verb='回复了你',
                    target=article,
                    action_object=new_comment,
                )

            # redirect()：返回到一个适当的url中：
            # 即用户发送评论后，重新定向到文章详情页面。
            # 当其参数是一个Model对象时，
            # 会自动调用这个Model对象的get_absolute_url()
            # 方法。因此接下来马上修改article的模型。

            # 添加锚点
            # get_absolute_url()是之前章节写的方法，用于查询某篇文章的地址。
            redirect_url = article.get_absolute_url() + '#comment_elem_' + str(new_comment.id)
            return redirect(redirect_url)
            # return redirect(article)
        else:
            return HttpResponse("表单内容有误，请重新填写。")
    # 处理 GET 请求
    # 用于给二级回复提供空白的表单。
    elif request.method == 'GET':
        comment_form = CommentForm()
        context = {
            'comment_form': comment_form,
            'article_id': article_id,
            'parent_comment_id': parent_comment_id
        }
        return render(request, 'comment/reply.html', context)
    # 处理错误请求
    else:
        return HttpResponse("发表评论仅接受POST请求。")
