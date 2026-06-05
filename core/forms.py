from django import forms
from email_validator import EmailNotValidError, validate_email
import phonenumbers

from .models import Category


class RequestForm(forms.Form):
    category = forms.ModelChoiceField(
        label='Категория продукции',
        queryset=Category.objects.none(),
        required=False,
        empty_label='Другое / не знаю',
    )
    company_name = forms.CharField(label='Компания', max_length=255)
    contact_person = forms.CharField(label='Контактное лицо', max_length=255, required=False)
    phone = forms.CharField(label='Телефон', max_length=50)
    email = forms.EmailField(label='E-mail', required=False)
    inn = forms.CharField(label='ИНН', max_length=20, required=False)
    kpp = forms.CharField(label='КПП', max_length=20, required=False)
    address = forms.CharField(
        label='Адрес',
        required=False,
        widget=forms.Textarea(attrs={'rows': 2})
    )
    comment = forms.CharField(
        label='Комментарий',
        required=False,
        widget=forms.Textarea(attrs={
            'placeholder': 'Укажите вид упаковки, объем, сроки или дополнительные требования',
            'rows': 4,
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(
            is_active=True
        ).order_by('sort_order', 'name')

    def clean_phone(self):
        phone = self.cleaned_data['phone'].strip()

        try:
            parsed = phonenumbers.parse(phone, 'RU')
        except phonenumbers.NumberParseException:
            raise forms.ValidationError('Введите корректный номер телефона.')

        if not phonenumbers.is_possible_number(parsed):
            raise forms.ValidationError('Такой номер телефона невозможен.')

        if not phonenumbers.is_valid_number(parsed):
            raise forms.ValidationError('Введите существующий номер телефона.')

        return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip()
        if not email:
            return ''

        try:
            result = validate_email(email, check_deliverability=True)
        except EmailNotValidError:
            raise forms.ValidationError('Введите существующий e-mail с корректным доменом.')

        return result.normalized

    def clean_inn(self):
        inn = self.cleaned_data.get('inn', '').strip()
        if inn and (not inn.isdigit() or len(inn) not in (10, 12)):
            raise forms.ValidationError('ИНН должен содержать 10 или 12 цифр.')
        return inn

    def clean_kpp(self):
        kpp = self.cleaned_data.get('kpp', '').strip()
        if kpp and (not kpp.isdigit() or len(kpp) != 9):
            raise forms.ValidationError('КПП должен содержать 9 цифр.')
        return kpp