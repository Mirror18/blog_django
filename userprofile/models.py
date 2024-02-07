from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True)
    # upload_to指定了图片上传的位置，
    # 即/media/avatar/%Y%m%d/。%Y%m%d是日期格式化的写法，
    # 最终格式化为系统时间。
    # ImageField字段不会存储图片本身，而仅仅保存图片的地址。
    avatar = models.ImageField(upload_to='avatar/%Y%m%d/', blank=True)
    bio = models.TextField(max_length=500, blank=True)

    def __str__(self):
        return 'user {}'.format(self.user.username)

# User和Profile的同步创建，但是也产生了一个BUG：
# 在后台中创建User时如果填写了Profile任何内容，
# 则系统报错且保存不成功；其他情况下均正常。
# **BUG产生原因：**在后台中创建并保存User时调用了信号接收函数，
# 创建了Profile表；
# 但如果此时管理员填写了内联的Profile表，会导致此表也会被创建并保存。
# 最终结果就是同时创建了两个具有相同User的Profile表，违背了”一对一“外键的原则。

# from django.db import models
# from django.contrib.auth.models import User
# # 引入内置信号
# from django.db.models.signals import post_save
# # 引入信号接收器的装饰器
# from django.dispatch import receiver


# # 用户扩展信息
# class Profile(models.Model):
#     # 与 User 模型构成一对一的关系
#     # 每个Profile模型对应唯一的一个User模型，
#     # 形成了对User的外接扩展，
#     # 因此你可以在Profile添加任何想要的字段。
#     # 这种方法的好处是不需要对User进行任何改动，
#     # 从而拥有完全自定义的数据表。
#     user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
#     # 电话号码字段
#     phone = models.CharField(max_length=20, blank=True)
#     # 头像
#     avatar = models.ImageField(upload_to='avatar/%Y%m%d/', blank=True)
#     # 个人简介
#     bio = models.TextField(max_length=500, blank=True)
#
#     def __str__(self):
#         return 'user {}'.format(self.user.username)
#
#
# # 信号接收函数，每当新建 User 实例时自动调用
# @receiver(post_save, sender=User)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         Profile.objects.create(user=instance)
#
#
# # Django包含一个“信号调度程序”，
# # 它可以在框架中的某些位置发生操作时，通知其他应用程序。
# # 简而言之，信号允许某些发送者通知一组接收器已经发生了某个动作。
# # 当许多代码可能对同一事件感兴趣时，信号就特别有用。
# # 这里引入的post_save就是一个内置信号，它可以在模型调用save()方法后发出信号。
# # 有了信号之后还需要定义接收器，
# # 告诉Django应该把信号发给谁。
# # 装饰器receiver就起到接收器的作用。
# # 每当User有更新时，
# # 就发送一个信号启动post_save相关的函数。
# # 通过信号的传递，实现了每当User创建/更新时，Profile也会自动的创建/更新。
# # 信号接收函数，每当更新 User 实例时自动调用
# @receiver(post_save, sender=User)
# def save_user_profile(sender, instance, **kwargs):
#     instance.profile.save()
