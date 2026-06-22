import logging
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from .models import Request

logger = logging.getLogger(__name__)


def get_manager_name(manager):
    if not manager:
        return 'менеджер отдела продаж'

    return manager.get_full_name().strip() or manager.username


def send_preliminary_offer(request_id):
    request_obj = (
        Request.objects
        .select_related('assigned_manager', 'category', 'product')
        .get(pk=request_id)
    )

    if not request_obj.email:
        return

    manager = request_obj.assigned_manager
    context = {
        'request_obj': request_obj,
        'manager_name': get_manager_name(manager),
        'manager_phone': getattr(
            settings,
            'SALES_MANAGER_PHONE',
            '+7 (111) 222-33-22',
        ),
        'manager_email': (
            getattr(manager, 'email', '')
            or getattr(settings, 'SALES_DEPARTMENT_EMAIL', '')
        ),
        'company_name': getattr(
            settings,
            'COMPANY_NAME',
            'ООО «Кларити упаковка»',
        ),
    }

    subject = f'Предварительное коммерческое предложение по заявке №{request_obj.id}'
    html_message = render_to_string(
        'core/emails/pre_offer.html',
        context,
    )

    message = EmailMultiAlternatives(
        subject=subject,
        body=strip_tags(html_message),
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[request_obj.email],
    )
    message.attach_alternative(html_message, 'text/html')

    try:
        message.send(fail_silently=False)
    except Exception:
        logger.exception(
            'Не удалось отправить предварительное КП по заявке №%s',
            request_obj.id,
        )
