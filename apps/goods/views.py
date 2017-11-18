from django.shortcuts import render
from django.views.generic import View


class GoodsIndex(View):
    """商品索引页"""
    @staticmethod
    def get(request):
        return render(request, 'goods/index.html')


class GoodsDetail(View):
    """商品详情"""
    @staticmethod
    def get(request):
        return render(request, 'goods/detail.html')

    @staticmethod
    def post(request):
        return render(request, 'goods/detail.html')

