from django.conf.urls import url
from apps.goods import views


urlpatterns = [
    # 主页
    url(r'^index', views.index, name='index'),

]
