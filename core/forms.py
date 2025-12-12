from django import forms
from .models import Request

class RequestForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = ('name', 'phone', 'email', 'comment')
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Название вашей организации и имя'}),
            'phone': forms.TextInput(attrs={'placeholder': '+7 (___) ___-__-__'}),
            'email': forms.EmailInput(attrs={'placeholder': 'you@vashsite.ru'}),
            'comment': forms.Textarea(attrs={'placeholder': 'Введите текст запроса: вид упаковки, объёмы.', 'rows': 4}),
        }