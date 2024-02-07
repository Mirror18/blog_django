from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from .forms import UserLoginForm


# Create your views here.

def user_login(request):
    if request.method == 'POST':
        user_login_form = UserLoginForm(data=request.POST)
        # Form对象的主要任务就是验证数据。调用is_valid()
        # 方法验证并返回指定数据是否有效的布尔值。
        if user_login_form.is_valid():
            # .cleaned_data 清洗出合法数据
            # 将其标准化为一致的格式，
            # 这个特性使得它允许以各种方式输入特定字段的数据，
            # 并且始终产生一致的输出。
            data = user_login_form.cleaned_data
            # 检验账号、密码是否正确匹配数据库中的某个用户
            # 如果均匹配则返回这个 user 对象
            # authenticate()方法验证用户名称和密码是否匹配，
            # 如果是，则将这个用户数据返回。
            user = authenticate(username=data['username'], password=data['password'])
            if user:
                # 将用户数据保存在 session 中，即实现了登录动作

                # Session在网络应用中，称为“会话控制”，
                # 它存储特定用户会话所需的属性及配置信息。
                # 当用户在 Web 页之间跳转时，
                # 存储在 Session 对象中的变量将不会丢失，
                # 而是在整个用户会话中一直存在下去。
                # Session 最常见的用法就是存储用户的登录数据。
                login(request, user)
                return redirect("article:article_list")
            else:
                return HttpResponse("账号或密码输入有误。请重新输入~")
        else:
            return HttpResponse("账号或密码输入不合法")
    elif request.method == 'GET':
        user_login_form = UserLoginForm()
        context = {'form': user_login_form}
        return render(request, 'userprofile/login.html', context)
    else:
        return HttpResponse("请使用GET或POST请求数据")


# 引入logout模块
from django.contrib.auth import authenticate, login, logout


# 用户退出
def user_logout(request):
    logout(request)
    return redirect("article:article_list")


# 引入 UserRegisterForm 表单类
from .forms import UserLoginForm, UserRegisterForm


# 用户注册
def user_register(request):
    if request.method == 'POST':
        user_register_form = UserRegisterForm(data=request.POST)
        if user_register_form.is_valid():
            new_user = user_register_form.save(commit=False)
            # 设置密码
            new_user.set_password(user_register_form.cleaned_data['password'])
            new_user.save()
            # 保存好数据后立即登录并返回博客列表页面
            login(request, new_user)
            return redirect("article:article_list")
        else:
            return HttpResponse("注册表单输入有误。请重新输入~")
    elif request.method == 'GET':
        user_register_form = UserRegisterForm()
        context = {'form': user_register_form}
        return render(request, 'userprofile/register.html', context)
    else:
        return HttpResponse("请使用GET或POST请求数据")


from django.contrib.auth.models import User
# 引入验证登录的装饰器
from django.contrib.auth.decorators import login_required


# @login_required要求调用user_delete()函数时，
# 用户必须登录；如果未登录则不执行函数，
# 将页面重定向到/userprofile/login/地址去

# 装饰器确认用户已经登录后，允许调用user_delete()；
# 然后需要删除的用户id通过请求传递到视图中，
# 由if语句确认是否与登录的用户一致，
# 成功后则退出登录并删除用户数据，返回博客列表页面
@login_required(login_url='/userprofile/login/')
def user_delete(request, id):
    if request.method == 'POST':
        user = User.objects.get(id=id)
        # 验证登录用户、待删除用户是否相同
        if request.user == user:
            # 退出登录，删除数据并返回博客列表
            logout(request)
            user.delete()
            return redirect("article:article_list")
        else:
            return HttpResponse("你没有删除操作的权限。")
    else:
        return HttpResponse("仅接受post请求。")



from .forms import ProfileForm
from .models import Profile


# 编辑用户信息
@login_required(login_url='/userprofile/login/')
def profile_edit(request, id):
    user = User.objects.get(id=id)
    # user_id 是 OneToOneField 自动生成的字段
    # 用来表征两个数据表的关联。你可以在SQLiteStudio中查看它。
    # 旧代码
    # profile = Profile.objects.get(user_id=id)
    # 修改后的代码
    if Profile.objects.filter(user_id=id).exists():
        profile = Profile.objects.get(user_id=id)
    else:
        profile = Profile.objects.create(user=user)

    if request.method == 'POST':
        # 验证修改数据者，是否为用户本人
        if request.user != user:
            return HttpResponse("你没有权限修改此用户信息。")

        # 上传的文件保存在 类字典对象 request.FILES 中，通过参数传递给表单类
        profile_form = ProfileForm(request.POST, request.FILES)
        if profile_form.is_valid():
            # 取得清洗后的合法数据
            profile_cd = profile_form.cleaned_data
            profile.phone = profile_cd['phone']
            profile.bio = profile_cd['bio']

            # 如果request.FILES中存在键为avatar的元素，
            # 则将其赋值给profile.avatar（注意保存的是图片地址）；
            # 否则不进行处理。
            if 'avatar' in request.FILES:
                profile.avatar = profile_cd["avatar"]
            profile.save()
            # 带参数的 redirect()
            return redirect("userprofile:edit", id=id)
        else:
            return HttpResponse("注册表单输入有误。请重新输入~")

    elif request.method == 'GET':
        profile_form = ProfileForm()
        context = {'profile_form': profile_form, 'profile': profile, 'user': user}
        return render(request, 'userprofile/edit.html', context)
    else:
        return HttpResponse("请使用GET或POST请求数据")
