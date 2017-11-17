from django.shortcuts import render, redirect
import re
from django.http import HttpResponse
from apps.user.models import Address, User
from django.core.urlresolvers import reverse
from django.views.generic import View       # 视图基类
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer    # 生成加密链接,避免被捣蛋
from itsdangerous import SignatureExpired   # 捕获邮箱过时异常
from django.conf import settings
# from django.core.mail import send_mail
from celery_tasks.tasks import send_register_active_email
from django.contrib.auth import authenticate, login, logout
from utils.mixin import LoginRequiredMixin
from django_redis import get_redis_connection
from apps.goods.models import GoodsSKU


# 注册页面显示
def register(request):
    # 注册
    print('----->request.method==', request.method)
    if request.method == 'GET':
        return render(request, 'user/register.html')
    else:
        # 接收数据
        post = request.POST
        u_name = post.get('user_name')
        u_pwd = post.get('pwd')
        u_pwd1 = post.get('cpwd')
        u_email = post.get('email')
        u_allow = post.get('allow')
        print(u_allow)
        # 数据校验
        if u_pwd != u_pwd1:
            return render(request, 'user/register.html', {'errmsg': '两次密码不一样'})
        if not all([u_name, u_email, u_pwd, u_pwd1]):
            return render(request, 'user/register.html', {'errmsg': '数据不完整'})
        # if not re.match(r'/^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$/', u_email):
        #     return render(request, 'user/register.html', {'errmsg': '邮箱格式有误'})
        if u_allow != 'on':
            return render(request, 'user/register.html', {'errmsg': '请同意协议'})
        if User.objects.filter(username=u_name) != 0:
            return render(request, 'user/register.html', {'errmsg': '用户名已存在'})
        # 校验完毕，保存用户信息到数据库
        user = User.objects.create_user(u_name, u_email, u_pwd)
        # 修改原始激活状态为0
        user.is_active = 0
        user.save()
        # 返回应答，跳转到首页
        return redirect(reverse('goods:index'))


# 处理注册post表单
# def register_handle(request):
#     # 接收数据
#     post = request.POST
#     u_name = post.get('user_name')
#     u_pwd = post.get('pwd')
#     u_pwd1 = post.get('cpwd')
#     u_email = post.get('email')
#     u_allow = post.get('allow')
#     print(u_allow)
#     # 数据校验
#     if u_pwd != u_pwd1:
#         return render(request, 'user/register.html', {'errmsg': '两次密码不一样'})
#     if not all([u_name, u_email, u_pwd, u_pwd1]):
#         return render(request, 'user/register.html', {'errmsg': '数据不完整'})
#     if not re.match(r'/^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$/', u_email):
#         return render(request, 'user/register.html', {'errmsg': '邮箱格式有误'})
#     if u_allow != 'on':
#         return render(request, 'user/register.html', {'errmsg': '请同意协议'})
#     # 校验完毕，报错用户信息到数据库
#     user = User.objects.create_user(u_name, u_email, u_pwd)
#     # 修改原始激活状态为0
#     user.is_active = 0
#     user.save()
#     # 返回应答，跳转到首页
#     return redirect(reverse('goods:index'))


class RegisterView(View):
    """用注册类"""
    @staticmethod
    def get(request):
        """显示注册页面"""
        return render(request, 'user/register.html')

    @staticmethod
    def post(request):
        """处理注册表单"""
        # 接收数据
        post = request.POST
        u_name = post.get('user_name')
        u_pwd = post.get('pwd')
        u_pwd1 = post.get('cpwd')
        u_email = post.get('email')
        u_allow = post.get('allow')
        # 数据校验
        if u_pwd != u_pwd1:
            return render(request, 'user/register.html', {'errmsg': '两次密码不一样'})
        if not all([u_name, u_email, u_pwd, u_pwd1]):
            return render(request, 'user/register.html', {'errmsg': '数据不完整'})
        if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', u_email):
            return render(request, 'user/register.html', {'errmsg': '邮箱格式有误'})
        if u_allow != 'on':
            return render(request, 'user/register.html', {'errmsg': '请同意协议'})
        # if User.objects.filter(username=u_name) != 0:
        try:
            user = User.objects.get(username=u_name)
        except User.DoesNotExist:
            # 用户不存在
            user = None
        if user:
            return render(request, 'user/register.html', {'errmsg': '用户名已存在'})
        # 校验完毕，保存用户信息到数据库
        user = User.objects.create_user(u_name, u_email, u_pwd)
        # 修改原始激活状态为0
        user.is_active = 0
        user.save()
        # 返回应答，跳转到首页
        # return redirect(reverse('goods:index'))

        # 对用户的身份信息进行加密,生成激活token
        serializer = Serializer(settings.SECRET_KEY, 3600)
        info = {'confirm': user.id}
        token = serializer.dumps(info).decode()   # bytes
        # 用celery发送邮件
        # delay函数将任务放到任务队列
        send_register_active_email.delay(u_email, u_name, token)

        # # 参数1:邮件头,2:正文,3:发送者,4:发送到的邮箱列表
        # subject = '天天生仙欢饮您'
        # message = ''
        # html_message = """
        #     <h1>%s, 欢迎注册成为天天生仙会员</h1>
        #     请点击下面链接激活账户</br>
        #     <a href='http://127.0.0.1:8000/user/active/%s'>http://127.0.0.1:8000/user/active/%s</a>
        # """ % (u_name, token, token)
        # from_email = settings.EMAIL_FROM
        # recipient_list = [u_email]
        # send_mail(subject, message, from_email, recipient_list, html_message=html_message)

        # 返回应答,跳转到首页
        return redirect(reverse('goods:index'))


class ActiveView(View):
    """用户邮箱激活"""
    @staticmethod
    def get(token):
        # 用户激活
        # 解密用户身份信息
        serializer = Serializer(settings.SECRET_KEY, 3360)
        try:
            info = serializer.loads(token)
            # 获取激活用户的id
            user_id = info['confirm']
            # 修改用户激活标记
            user = User.objects.get(id=user_id)
            user.is_active = 1
            user.save()
            # 跳转到登录页面
            return redirect(reverse('user:login'))
        except SignatureExpired:
            # 激活链接已失效
            return HttpResponse('激活链接已失效')


class LoginView(View):
    """登录页面"""
    @staticmethod
    def get(request):
        # 显示登录页面
        # 将cookies用户名,放到页面中去
        if 'username' in request.COOKIES:
            u_name = request.COOKIES.get('username')
            checked = 'checked'
        else:
            u_name = ''
            checked = ''
        # 使用模板
        return render(request, 'user/login.html', {'username': u_name, 'checked': checked})

    @staticmethod
    def post(request):
        # 接收数据
        post = request.POST
        u_name = post.get('username')
        u_pwd = post.get('pwd')
        u_remember = post.get('remember')
        # print(u_name, u_pwd, u_remember)
        # 登录校验
        if not all([u_pwd, u_name]):
            return render(request, {"errmsg": '数据不完整'})

        user = authenticate(username=u_name, password=u_pwd)
        if user is not None:
            # 用户名密码正确
            if user.is_active:
                # 记住用户名登录状态
                login(request, user)
                # 获取登录后跳转的url地址
                # 如果获取不到,默认跳转首页网
                next_url = request.GET.get('next', reverse('goods:index'))
                # 跳转到首页
                response = redirect(next_url)
                # 是否需要记住用户名
                if u_remember == 'on':
                    response.set_cookie('username', u_name)
                else:
                    response.delete_cookie('username')
                    return response
            else:
                # 用户账户未激活
                return render(request, 'user/login.html', {'errmsg': '用户未激活'})
        else:
            # 用户名或密码错误
            return render(request, 'user/login.html', {'errmsg': '用户名或密码错误'})


class LogoutView(View):
    """用户退出"""
    @staticmethod
    def get(request):
        # 自带方法, 清楚session
        logout(request)
        return redirect(reverse('goods:index'))


class UserInfoView(LoginRequiredMixin):
    """用户中心,信息页"""
    @staticmethod
    def get(request):
        """show"""
        # 用户个人信息--->django 会默认将request.user传给模板文件
        user = request.user
        address = Address.objects.get_default_address(user)

        # 用户历史浏览记录
        # 获取redis链接对象－>StrictRedis
        conn = get_redis_connection('default')
        list_key = 'history_%d' % user.id
        # 获取redis中保存的id
        sku_ids = conn.lrange(list_key, 0, 4)   # [3,2,1]
        # 查找出结果集
        goods_li = [GoodsSKU.objects.get(id=goods_id) for goods_id in sku_ids]
        # 组织上下文
        context = {'page': 'user', 'address': address, 'goods_li': goods_li}
        return render(request, 'user/user_center_info.html', context)


class UserOrderView(LoginRequiredMixin):
    """用户中心,订单页"""
    @staticmethod
    def get(request):
        """show"""
        return render(request, 'user/user_center_order.html', {'page': 'order'})


class AddressView(LoginRequiredMixin):
    """用户中心,订单页"""
    @staticmethod
    def get(request):
        """show"""
        # 获取用户中心地址页面
        address = Address.objects.get_default_address(request.user)
        return render(request, 'user/user_center_site.html', {'page': 'address', 'address': address})

    @staticmethod
    def post(request):
        """添加收件人地址"""
        # 接收数据
        post = request.POST
        receiver = post.get('receiver')
        addr = post.get('addr')
        zip_code = post.get('zip_code')
        phone = post.get('phone')
        # 数据校验
        if not all([receiver, addr, zip_code, phone]):
            return render(request, 'user/user_center_site.html', {'error': '数据不完整'})
        # if not re.match(r"^1[3|4|5|7|8][0-9]{9}$", phone):
        #     return render(request, 'user/user_center_site.html', {'error': '联系方式不正确'})
        # 获取用户登录对象
        user = request.user
        # try:
        #     address = Address.objects.get(user=user, is_default=True)
        # except Address.DoesNotExist:
        #     address = None
        address = Address.objects.get_default_address(user)
        if address:
            is_default = False
        else:
            is_default = True
        # 业务处理:地址添加
        Address.objects.create(user=user,
                               receiver=receiver,
                               addr=addr,
                               zip_code=zip_code,
                               phone=phone,
                               is_default=is_default)
        # 返回应答
        return redirect(reverse("user:address"))
