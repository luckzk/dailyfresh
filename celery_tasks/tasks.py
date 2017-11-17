# 使用celery实现异步发送邮件
from celery import Celery
from django.conf import settings
from django.core.mail import send_mail
import time

# 其他电脑接受任务执行时会因为没有django环境而报错,需要导入wsgi中的环境
# 命令:celery -A celery_tasks.tasks worker -l info
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dailyfresh.settings")
django.setup()

# 创建一个Celery对象
app = Celery('celery_tasks.tasks', broker='redis://127.0.0.1:6379/5')


# 创建任务函数
# 任务发布者,中间人,处理者,可以不是一台电脑
@app.task
def send_register_active_email(u_email, u_name, token):
    # 用celery发送邮件
    # 参数1:邮件头,2:正文,3:发送者,4:发送到的邮箱列表,5.html类型参数
    subject = '天天生仙欢饮您'
    message = ''
    html_message = """
                <h1>%s, 欢迎注册成为天天生仙会员</h1>
                请点击下面链接激活账户</br>
                <a href='http://127.0.0.1:8000/user/active/%s'>
                http://127.0.0.1:8000/user/active/%s</a>
            """ % (u_name, token, token)
    from_email = settings.EMAIL_FROM
    recipient_list = [u_email]
    send_mail(subject, message, from_email, recipient_list, html_message=html_message)
    # 模拟用时5s
    time.sleep(5)
