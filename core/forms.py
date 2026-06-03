from django import forms
from .models import Request


class RequestForm(forms.Form):
    company_name = forms.CharField(
        label='Компания',
        max_length=255,
        widget=forms.TextInput(attrs={'placeholder': 'Название организации'})
    )
    contact_person = forms.CharField(
        label='Контактное лицо',
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Имя контактного лица'})
    )
    phone = forms.CharField(
        label='Телефон',
        max_length=50,
        widget=forms.TextInput(attrs={'placeholder': '+7 (___) ___-__-__'})
    )
    email = forms.EmailField(
        label='E-mail',
        required=False,
        widget=forms.EmailInput(attrs={'placeholder': 'you@company.ru'})
    )
    comment = forms.CharField(
        label='Комментарий',
        required=False,
        widget=forms.Textarea(attrs={
            'placeholder': 'Укажите вид упаковки, объем, сроки и прочие требования',
            'rows': 4,
        })
    )
