from django.conf.urls import url
from apps.user import views
from django.contrib.auth.decorators import login_required

urlpatterns = [
    # 注册
    url(r'^register$', views.RegisterView.as_view(), name='register'),
    # 处理注册表单
    # url(r'^register_handle$', views.register_handle),
    # 邮箱激活
    url(r'^active/(?P<token>.*)$', views.ActiveView.as_view(), name='active'),
    # 登录页面
    url(r'^login$', views.LoginView.as_view(), name='login'),
    # 登出
    url(r'^logout$', views.LogoutView.as_view(), name='logout'),
    # 用户信息-信息页
    # url(r'^$', login_required(views.UserInfoView.as_view()), name='user'),
    # url(r'^order$', login_required(views.UserOrderView.as_view()), name='order'),
    # url(r'^address$', login_required(views.AddressView.as_view()), name='address'),
    # #
    url(r'^$', views.UserInfoView.as_view(), name='user'),
    url(r'^order$', views.UserOrderView.as_view(), name='order'),
    url(r'^address$', views.AddressView.as_view(), name='address'),
    #
]
