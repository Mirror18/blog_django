# 引入表单类
from django import forms
# 引入 User 模型
from django.contrib.auth.models import User


# 在前面发表文章的模块中，表单类继承了forms.ModelForm，
# 这个父类适合于需要直接与数据库交互的功能，
# 比如新建、更新数据库的字段等。
# 如果表单将用于直接添加或编辑Django模型，
# 则可以使用 ModelForm来避免重复书写字段描述。
#
# 而forms.Form则需要手动配置每个字段，
# 它适用于不与数据库进行直接交互的功能。
# 用户登录不需要对数据库进行任何改动，
# 因此直接继承forms.Form就可以了。

# 登录表单，继承了 forms.Form 类
class UserLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField()


# 验证密码一致性方法不能写def clean_password()，
# 因为如果你不定义def clean_password2()方法，
# 会导致password2中的数据被Django判定为无效数据从而清洗掉，
# 从而password2属性不存在。最终导致两次密码输入始终会不一致，
# 并且很难判断出错误原因。

# 从POST中取值用的data.get('password')是一种稳妥的写法，
# 即使用户没有输入密码也不会导致程序错误而跳出。
# 前面提取POST数据用data['password']，
# 这种取值方式如果data中不包含password，Django会报错。
# 另一种防止用户不输入密码就提交的方式是在表单中插入 required 属性，
# 注册用户表单
class UserRegisterForm(forms.ModelForm):
    # 复写 User 的密码
    password = forms.CharField()
    password2 = forms.CharField()

    class Meta:
        model = User
        fields = ('username', 'email')

    # 对两次输入的密码是否一致进行检查
    # 自动调用
    def clean_password2(self):
        data = self.cleaned_data
        if data.get('password') == data.get('password2'):
            return data.get('password')
        else:
            raise forms.ValidationError("密码输入不一致,请重试。")


# 引入 Profile 模型
from .models import Profile


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('phone', 'avatar', 'bio')
