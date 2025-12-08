from django.http import HttpResponse
from django.shortcuts import render


def index(request):
    return render(request, 'core/index.html')


def about(request):
    return render(request, 'core/about.html')


def contacts(request):
    return render(request, 'core/contacts.html')


# Плёнки ПВХ
def films_pvc(request):
    return render(request, 'core/films_pvc/index.html')


def films_pvc_horeca(request):
    return render(request, 'core/films_pvc/horeca.html')


def films_pvc_hand_cast(request):
    return render(request, 'core/films_pvc/hand_cast.html')


def films_pvc_home(request):
    return render(request, 'core/films_pvc/home.html')


def films_pvc_jumbo(request):
    return render(request, 'core/films_pvc/jumbo.html')


# Перчатки
def gloves(request):
    return render(request, 'core/gloves/index.html')


def gloves_pe(request):
    return render(request, 'core/gloves/pe.html')


def gloves_vinyl(request):
    return render(request, 'core/gloves/vinyl.html')


# Упаковка Комус
def komus_packaging(request):
    return render(request, 'core/komus_packaging.html')