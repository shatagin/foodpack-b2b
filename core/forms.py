from django import forms
from email_validator import EmailNotValidError, validate_email
import phonenumbers


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
            'placeholder': 'Укажите вид упаковки, объем, сроки или дополнительные требования',
            'rows': 4,
        })
    )

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
