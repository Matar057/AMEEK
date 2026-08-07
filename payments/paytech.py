import base64
import hashlib
import hmac
import json
import logging

import requests
from django.conf import settings
from django.urls import reverse

logger = logging.getLogger(__name__)

PAYTECH_API = 'https://paytech.sn/api'

PAYTECH_METHODS = {
    'wave': 'Wave',
    'orange_money': 'Orange Money',
    'free_money': 'Free Money',
    'carte': 'Carte Bancaire',
}


def _headers():
    return {
        'API_KEY': settings.PAYTECH_API_KEY,
        'API_SECRET': settings.PAYTECH_API_SECRET,
        'Accept': 'application/json',
        'Content-Type': 'application/json',
    }


def _env():
    return 'test' if settings.PAYTECH_MODE == 'test' else 'prod'


def create_payment(montant, description, ref_command, custom_data=None, method=''):
    base_url = settings.BASE_URL.rstrip('/')
    target_payment = PAYTECH_METHODS.get(method, '')
    data = {
        'item_name': description,
        'item_price': int(montant),
        'currency': 'XOF',
        'ref_command': ref_command,
        'command_name': description,
        'env': _env(),
        'ipn_url': f'{base_url}{reverse("payments:paytech_ipn")}',
        'success_url': f'{base_url}{reverse("payments:paytech_success")}',
        'cancel_url': f'{base_url}{reverse("payments:paytech_cancel")}',
        'custom_field': json.dumps(custom_data or {}),
    }
    if target_payment:
        data['target_payment'] = target_payment

    try:
        resp = requests.post(
            f'{PAYTECH_API}/payment/request-payment',
            json=data,
            headers=_headers(),
            timeout=15,
        )
        if resp.status_code in (200, 201):
            result = resp.json()
            if result.get('success') == 1 and result.get('token'):
                return result['token'], result.get('redirect_url')
            logger.error('PayTech create_payment failed: %s', result)
        else:
            logger.error('PayTech API error [%s]: %s', resp.status_code, resp.text)
    except requests.RequestException as e:
        logger.exception('PayTech request failed: %s', e)
    return None, None


def get_status(token):
    try:
        resp = requests.get(
            f'{PAYTECH_API}/payment/get-status',
            params={'token_payment': token},
            headers=_headers(),
            timeout=15,
        )
        if resp.ok:
            result = resp.json()
            if result.get('success') == 1:
                return result
            logger.error('PayTech get_status failed: %s', result)
        else:
            logger.error('PayTech get_status error [%s]: %s', resp.status_code, resp.text)
    except requests.RequestException as e:
        logger.exception('PayTech get_status request failed: %s', e)
    return None


def decode_custom_field(raw):
    if not raw:
        return {}
    for candidate in (raw, base64.b64decode(raw).decode('utf-8', errors='ignore') if _is_base64(raw) else ''):
        try:
            data = json.loads(candidate)
            if isinstance(data, dict):
                return data
        except (ValueError, TypeError):
            continue
    return {}


def _is_base64(value):
    try:
        base64.b64decode(value)
        return True
    except Exception:
        return False


def verify_ipn(post_data):
    hmac_compute = post_data.get('hmac_compute', '')
    if hmac_compute:
        final_price = post_data.get('final_item_price') or post_data.get('item_price', '')
        message = f'{final_price}|{post_data.get("ref_command", "")}|{settings.PAYTECH_API_KEY}'
        expected = hmac.new(
            settings.PAYTECH_API_SECRET.encode(),
            message.encode(),
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(expected, hmac_compute)

    api_key_sha256 = post_data.get('api_key_sha256', '')
    api_secret_sha256 = post_data.get('api_secret_sha256', '')
    expected_key = hashlib.sha256(settings.PAYTECH_API_KEY.encode()).hexdigest()
    expected_secret = hashlib.sha256(settings.PAYTECH_API_SECRET.encode()).hexdigest()
    return (
        hmac.compare_digest(expected_key, api_key_sha256)
        and hmac.compare_digest(expected_secret, api_secret_sha256)
    )
