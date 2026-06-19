import logging

import requests
from django.conf import settings
from django.urls import reverse

logger = logging.getLogger(__name__)

PAYDUNYA_API = 'https://app.paydunya.com/api/v1'
PAYDUNYA_API_TEST = 'https://app.paydunya.com/sandbox-api/v1'


def _api_base():
    return PAYDUNYA_API_TEST if settings.PAYDUNYA_MODE == 'test' else PAYDUNYA_API


def _headers():
    return {
        'PAYDUNYA-MASTER-KEY': settings.PAYDUNYA_MASTER_KEY,
        'PAYDUNYA-PRIVATE-KEY': settings.PAYDUNYA_PRIVATE_KEY,
        'PAYDUNYA-TOKEN': settings.PAYDUNYA_TOKEN,
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }


def create_invoice(montant, description, custom_data=None):
    base_url = settings.BASE_URL.rstrip('/')
    logger.info(
        'PayDunya keys: MASTER_KEY=%s..., PRIVATE_KEY=%s..., TOKEN=%s..., MODE=%s',
        settings.PAYDUNYA_MASTER_KEY[:10] if settings.PAYDUNYA_MASTER_KEY else 'EMPTY',
        settings.PAYDUNYA_PRIVATE_KEY[:10] if settings.PAYDUNYA_PRIVATE_KEY else 'EMPTY',
        settings.PAYDUNYA_TOKEN[:10] if settings.PAYDUNYA_TOKEN else 'EMPTY',
        settings.PAYDUNYA_MODE,
    )
    data = {
        'invoice': {
            'items': [
                {
                    'name': description,
                    'quantity': 1,
                    'unit_price': str(int(montant)),
                    'total_price': str(int(montant)),
                }
            ],
            'total_amount': str(int(montant)),
            'description': description,
        },
        'store': {
            'name': 'AMEEK',
            'website_url': base_url,
        },
        'actions': {
            'cancel_url': f'{base_url}{reverse("payments:paydunya_cancel")}',
            'return_url': f'{base_url}{reverse("payments:paydunya_success")}',
            'callback_url': f'{base_url}{reverse("payments:paydunya_ipn")}',
        },
        'custom_data': custom_data or {},
    }

    try:
        resp = requests.post(
            f'{_api_base()}/checkout-invoice/create',
            json=data,
            headers=_headers(),
            timeout=15,
        )
        if resp.ok:
            result = resp.json()
            if result.get('response_text') == 'success' and result.get('invoice'):
                return result['invoice']['token'], result['response_text']
            logger.error('PayDunya create_invoice failed: %s', result)
        else:
            logger.error('PayDunya API error [%s]: %s', resp.status_code, resp.text)
    except requests.RequestException as e:
        logger.exception('PayDunya request failed: %s', e)
    return None, None


def get_invoice_url(invoice_token):
    mode = 'sandbox' if settings.PAYDUNYA_MODE == 'test' else 'app'
    return f'https://{mode}.paydunya.com/checkout/{invoice_token}'


def verify_invoice(invoice_token):
    try:
        resp = requests.get(
            f'{_api_base()}/checkout-invoice/confirm/{invoice_token}',
            headers=_headers(),
            timeout=15,
        )
        if resp.ok:
            result = resp.json()
            if result.get('response_text') == 'success':
                invoice = result.get('invoice', {})
                return {
                    'status': invoice.get('status'),
                    'montant': invoice.get('total_amount'),
                    'method': invoice.get('payment_method', ''),
                    'reference': invoice.get('transaction_id', ''),
                    'custom_data': result.get('custom_data', {}),
                }
        logger.error('PayDunya verify failed [%s]: %s', resp.status_code, resp.text)
    except requests.RequestException as e:
        logger.exception('PayDunya verify request failed: %s', e)
    return None
