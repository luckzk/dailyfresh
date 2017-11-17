from django.shortcuts import render


# Create your views here.
# asd
def index(request):
    return render(request, 'goods/index.html')
