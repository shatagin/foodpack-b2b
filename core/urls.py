from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),

    path('about/', views.about, name='about'),
    path('contacts/', views.contacts, name='contacts'),

    # Плёнки ПВХ пищевые
    path('films-pvc/', views.films_pvc, name='films_pvc'),
    path('films-pvc/horeca/', views.films_pvc_horeca, name='films_pvc_horeca'),
    path('films-pvc/hand-cast/', views.films_pvc_hand_cast, name='films_pvc_hand_cast'),
    path('films-pvc/home/', views.films_pvc_home, name='films_pvc_home'),
    path('films-pvc/jumbo/', views.films_pvc_jumbo, name='films_pvc_jumbo'),

    # Перчатки
    path('gloves/', views.gloves, name='gloves'),
    path('gloves/pe/', views.gloves_pe, name='gloves_pe'),
    path('gloves/vinyl/', views.gloves_vinyl, name='gloves_vinyl'),

    # Упаковка Комус
    path('komus-packaging/', views.komus_packaging, name='komus_packaging'),
]
