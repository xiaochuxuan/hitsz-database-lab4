from django.contrib import messages
from django.shortcuts import redirect, render, reverse
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpRequest

from management.models import User, Manager
from .forms import RegistForm, LoginForm
# Create your views here.

# 定义用户编号位数
user_id_base = 100000

# 获取最大字段长度
user_name_maxlength = User._meta.get_field('user_name').max_length

# 开始视图
def home_view(request):
    return render(request, 'User/index.html')

# 视图：注册用户
def regist(request):
    if request.method == 'POST':
        regist_form = RegistForm(request.POST)

        if regist_form.is_valid():
            user_name = regist_form.cleaned_data['user_name']
            user_sex = regist_form.cleaned_data['user_sex']
            teacher_id = regist_form.cleaned_data['teacher_id']
            user_phone = regist_form.cleaned_data['user_phone']
            user_pwd = regist_form.cleaned_data['password']

            # 在user表中加入相应记录
            print("用户表元组数: " + str(len(User.objects.all())))

            # 生成用户id, 同时判断用户是否重名
            user_id = 0
            for user in User.objects.all():
                if int(user.user_id) > user_id:
                    user_id = int(user.user_id)

                # 重名则直接返回
                if user.user_name == user_name:
                    messages.warning(request, 'user_name already exists!')
                    return render(request, 'Share/form.html', {
                        'form': regist_form, 'title': 'Regist'
                    })

            if user_id < user_id_base:
                user_id = user_id_base + 1
            else:
                user_id = user_id + 1

            # 从对应教师列表中查找是否为管理员
            # 0为普通用户，1为管理员
            character = 0
            if Manager.objects.filter(t_id=teacher_id):
                character = 1

            # 写入数据库
            user = User(user_id=str(user_id), t_id=teacher_id, user_name=user_name,
                        user_sex=user_sex, password=user_pwd, user_phone=user_phone, user_character=character)
            user.save()

            return render(request, 'management/index.html', {'info': 'Success!'})
        else:
            return render(request, 'Share/form.html',
                          {'form': regist_form, 'title': 'Register'})

    form = RegistForm()
    return render(request, 'Share/form.html', {'form': form, 'title': 'Register'})

# 视图：登录
def login(request):
    if request.method == 'POST':
        login_form = LoginForm(request.POST)

        if login_form.is_valid():
            user_name = login_form.cleaned_data['user_name']
            password = login_form.cleaned_data['password']

            user = User.objects.get(user_name=user_name)
            if user and user.password == password:
                # 设置session
                request.session['user_id'] = user.user_id
                request.session['user_name'] = user.user_name
                request.session['teacher_id'] = user.t_id
                request.session['password'] = user.password
                request.session['user_sex'] = user.user_sex
                request.session['user_phone'] = str(user.user_phone)
                request.session['user_character'] = user.user_character

                # 1小时后失效
                request.session.set_expiry(3600)
                return redirect(reverse('management_home'))
            else:
                messages.warning(request, 'Invaild user_name or password!')
                return render(request, 'Share/form.html', {
                    'form': login_form, 'title': 'Login'
                })
        else:
            return render(request, 'Share/form.html', {'form': login_form, 'title': 'Login'})

    form = LoginForm()
    return render(request, 'Share/form.html', {'form': form, 'title': 'Login'})

# 视图：退出登录
def logout(request):
    # 删除session记录
    request.session.flush()
    return render(request, 'management/index.html')