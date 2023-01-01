from django.urls import path, include

import User.views

# 配置路由
urlpatterns = [
    path('', User.views.home_view, name='home'),
    path('regist/', User.views.regist, name='regist'),
    path('login/', User.views.login, name='login'),
    path('logout', User.views.logout, name='logout'),
]