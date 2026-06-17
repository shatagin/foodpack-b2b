import re

from django import forms
import dns.exception
import dns.resolver
from email_validator import EmailNotValidError, EmailUndeliverableError, validate_email
import phonenumbers

from .models import Category


def normalize_inn(value):
    value = (value or '').strip().replace('\xa0', ' ')
    value = re.sub(r'[A-Za-zА-Яа-яЁё]', '', value)

    return re.sub(r'[\s-]+', '', value)


def validate_inn_ul(value):
    if len(value) != 10 or not value.isdigit():
        return False
    weights = (2, 4, 10, 3, 5, 9, 4, 6, 8)
    total = sum(int(digit) * weight for digit, weight in zip(value, weights))
    control_digit = total % 11 % 10

    return control_digit == int(value[9])


def validate_inn_fl(value):
    if len(value) != 12 or not value.isdigit():
        return False

    weights_11 = (7, 2, 4, 10, 3, 5, 9, 4, 6, 8)
    weights_12 = (3, 7, 2, 4, 10, 3, 5, 9, 4, 6, 8)

    digit_11 = sum(int(digit) * weight for digit, weight in zip(value, weights_11)) % 11 % 10
    digit_12 = sum(int(digit) * weight for digit, weight in zip(value, weights_12)) % 11 % 10

    return digit_11 == int(value[10]) and digit_12 == int(value[11])


def validate_inn(value):
    inn = normalize_inn(value)
    if len(inn) == 10:
        return validate_inn_ul(inn)
    if len(inn) == 12:
        return validate_inn_fl(inn)

    return False


KPP_PATTERN = re.compile(r'^\d{4}[0-9A-Z]{2}\d{3}$')


def normalize_kpp(value):
    value = (value or '').strip().replace('\xa0', ' ')
    value = re.sub(r'[\s-]+', '', value)
    return value.upper()


def validate_kpp(value):
    kpp = normalize_kpp(value)

    if not kpp:
        return False

    return bool(KPP_PATTERN.match(kpp))


def is_dns_check_failure(error):
    cause = error.__cause__

    if isinstance(cause, (
        dns.exception.Timeout,
        dns.resolver.NoNameservers,
        dns.resolver.LifetimeTimeout,
    )):
        return True

    return 'There was an error while checking' in str(error)


def validate_email_dns_records(domain):
    try:
        mx_records = list(dns.resolver.resolve(domain, 'MX', lifetime=5))
    except dns.resolver.NXDOMAIN:
        raise forms.ValidationError('Домен e-mail не существует.')
    except dns.resolver.NoAnswer:
        raise forms.ValidationError('У домена e-mail нет MX-записей для приема почты.')
    except (dns.resolver.NoNameservers, dns.exception.Timeout, dns.exception.DNSException):
        return False

    if not mx_records:
        raise forms.ValidationError('У домена e-mail нет MX-записей для приема почты.')

    return True


class RequestForm(forms.Form):
    category = forms.ModelChoiceField(
        label='Категория продукции',
        queryset=Category.objects.none(),
        required=True,
        empty_label='Выберите категорию',
        widget=forms.Select()
    )
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
    inn = forms.CharField(
        label='ИНН',
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': '10 или 12 цифр'})
    )
    kpp = forms.CharField(
        label='КПП',
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': '9 цифр'})
    )
    address = forms.CharField(
        label='Адрес',
        required=False,
        widget=forms.Textarea(attrs={
            'placeholder': 'Адрес доставки или юридический адрес',
            'rows': 2,
        })
    )
    comment = forms.CharField(
        label='Комментарий',
        required=False,
        widget=forms.Textarea(attrs={
            'placeholder': 'Укажите вид упаковки, объем, сроки или дополнительные требования',
            'rows': 4,
        })
    )
    middle_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'autocomplete': 'off',
            'tabindex': '-1',
            'class': 'form-extra-input',
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
            result = validate_email(email, check_deliverability=False)
        except EmailNotValidError:
            raise forms.ValidationError('Введите корректный e-mail.')

        validate_email_dns_records(result.domain)

        return result.normalized

    def clean_inn(self):
        inn = self.cleaned_data.get('inn', '').strip()
        if inn and (not inn.isdigit() or len(inn) not in (10, 12)):
            raise forms.ValidationError('ИНН должен содержать 10 или 12 цифр.')
        return inn

    def clean_kpp(self):
        kpp = normalize_kpp(self.cleaned_data.get('kpp', ''))
        if not kpp:
            return ''
        if not validate_kpp(kpp):
            raise forms.ValidationError(
                'Введите корректный КПП: 9 символов'
            )

        return kpp
