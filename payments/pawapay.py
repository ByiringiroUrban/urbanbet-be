import logging
from typing import Any

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class PawaPayError(Exception):
    def __init__(self, message: str, *, status_code: int | None = None, payload: Any = None):
        super().__init__(message)
        self.status_code = status_code
        self.payload = payload


METHOD_TO_PROVIDER = {
    'momo': 'MTN_MOMO_RWA',
    'airtel': 'AIRTEL_RWA',
}


class PawaPayClient:
    def __init__(self):
        self.base_url = settings.PAWAPAY_BASE_URL.rstrip('/')
        self.token = settings.PAWAPAY_API_TOKEN
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        })

    def _request(self, method: str, path: str, **kwargs) -> dict:
        url = f'{self.base_url}{path}'
        try:
            response = self.session.request(method, url, timeout=30, **kwargs)
        except requests.RequestException as exc:
            logger.exception('PawaPay request failed: %s %s', method, path)
            raise PawaPayError('Unable to reach PawaPay. Please try again.') from exc

        try:
            payload = response.json() if response.content else {}
        except ValueError as exc:
            raise PawaPayError(
                'Unexpected response from PawaPay.',
                status_code=response.status_code,
            ) from exc

        if response.status_code >= 400:
            failure = payload.get('failureReason', {})
            message = failure.get('failureMessage') or payload.get('message') or 'PawaPay request failed.'
            raise PawaPayError(message, status_code=response.status_code, payload=payload)

        return payload

    def predict_provider(self, phone_number: str) -> dict:
        return self._request('POST', '/v2/predict-provider', json={'phoneNumber': phone_number})

    def initiate_deposit(
        self,
        deposit_id: str,
        amount: str,
        currency: str,
        phone_number: str,
        provider: str,
        *,
        customer_message: str = 'UrbanBet deposit',
    ) -> dict:
        return self._request(
            'POST',
            '/v2/deposits',
            json={
                'depositId': deposit_id,
                'amount': amount,
                'currency': currency,
                'payer': {
                    'type': 'MMO',
                    'accountDetails': {
                        'phoneNumber': phone_number,
                        'provider': provider,
                    },
                },
                'customerMessage': customer_message[:22],
            },
        )

    def check_deposit_status(self, deposit_id: str) -> dict:
        return self._request('GET', f'/v2/deposits/{deposit_id}')

    def initiate_payout(
        self,
        payout_id: str,
        amount: str,
        currency: str,
        phone_number: str,
        provider: str,
        *,
        customer_message: str = 'UrbanBet withdrawal',
    ) -> dict:
        return self._request(
            'POST',
            '/v2/payouts',
            json={
                'payoutId': payout_id,
                'amount': amount,
                'currency': currency,
                'recipient': {
                    'type': 'MMO',
                    'accountDetails': {
                        'phoneNumber': phone_number,
                        'provider': provider,
                    },
                },
                'customerMessage': customer_message[:22],
            },
        )

    def check_payout_status(self, payout_id: str) -> dict:
        return self._request('GET', f'/v2/payouts/{payout_id}')


def is_pawapay_enabled() -> bool:
    return bool(
        settings.PAWAPAY_ENABLED
        and settings.PAWAPAY_API_TOKEN
        and settings.PAWAPAY_BASE_URL
    )


def uses_pawapay(method: str) -> bool:
    return is_pawapay_enabled() and method in METHOD_TO_PROVIDER


def resolve_phone_and_provider(method: str, phone_number: str) -> tuple[str, str]:
    provider = METHOD_TO_PROVIDER[method]
    cleaned = ''.join(ch for ch in phone_number if ch.isdigit())

    if cleaned.startswith('0') and len(cleaned) == 10:
        cleaned = f'250{cleaned[1:]}'
    elif cleaned.startswith('250'):
        pass
    elif len(cleaned) == 9:
        cleaned = f'250{cleaned}'

    if is_pawapay_enabled():
        try:
            prediction = PawaPayClient().predict_provider(cleaned)
            return prediction['phoneNumber'], prediction.get('provider', provider)
        except PawaPayError:
            logger.warning('PawaPay predict-provider failed; using local normalization.')

    return cleaned, provider


def format_amount(amount) -> str:
    normalized = f'{amount:.2f}'.rstrip('0').rstrip('.')
    return normalized or '0'
