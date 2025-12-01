from django.http import HttpResponse


def index(request):
    return HttpResponse("<h1>FoodPack</h1><p>Django работает на VPS</p>")
