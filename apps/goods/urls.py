from django.conf.urls import url
from apps.goods import views


urlpatterns = [
    # 主页
    url(r'^index$', views.GoodsIndex.as_view(), name='index'),
    url(r'^detail$', views.GoodsDetail.as_view(), name='detail'),

]
