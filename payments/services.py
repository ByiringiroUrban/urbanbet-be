import logging

from django.db import transaction

from .models import Transaction
from .pawapay import PawaPayClient, PawaPayError

logger = logging.getLogger(__name__)

FINAL_DEPOSIT_STATUSES = {'COMPLETED', 'FAILED'}
FINAL_PAYOUT_STATUSES = {'COMPLETED', 'FAILED'}


@transaction.atomic
def complete_deposit(txn: Transaction) -> Transaction:
    txn = Transaction.objects.select_for_update().select_related('user').get(pk=txn.pk)
    if txn.status == Transaction.STATUS_COMPLETED:
        return txn

    txn.status = Transaction.STATUS_COMPLETED
    txn.save(update_fields=['status', 'updated_at'])

    user = txn.user
    user.balance += txn.amount
    user.save(update_fields=['balance'])
    return txn


@transaction.atomic
def fail_deposit(txn: Transaction) -> Transaction:
    txn = Transaction.objects.select_for_update().get(pk=txn.pk)
    if txn.status in (Transaction.STATUS_FAILED, Transaction.STATUS_COMPLETED):
        return txn

    txn.status = Transaction.STATUS_FAILED
    txn.save(update_fields=['status', 'updated_at'])
    return txn


@transaction.atomic
def complete_withdrawal(txn: Transaction) -> Transaction:
    txn = Transaction.objects.select_for_update().get(pk=txn.pk)
    if txn.status == Transaction.STATUS_COMPLETED:
        return txn

    txn.status = Transaction.STATUS_COMPLETED
    txn.save(update_fields=['status', 'updated_at'])
    return txn


@transaction.atomic
def fail_withdrawal(txn: Transaction) -> Transaction:
    txn = Transaction.objects.select_for_update().select_related('user').get(pk=txn.pk)
    if txn.status == Transaction.STATUS_FAILED:
        return txn

    if txn.status == Transaction.STATUS_PENDING:
        user = txn.user
        user.balance += txn.amount
        user.save(update_fields=['balance'])

    txn.status = Transaction.STATUS_FAILED
    txn.save(update_fields=['status', 'updated_at'])
    return txn


def _apply_pawapay_status(txn: Transaction, pawapay_status: str) -> Transaction:
    if txn.transaction_type == Transaction.TYPE_DEPOSIT:
        if pawapay_status == 'COMPLETED':
            return complete_deposit(txn)
        if pawapay_status == 'FAILED':
            return fail_deposit(txn)
    elif txn.transaction_type == Transaction.TYPE_WITHDRAWAL:
        if pawapay_status == 'COMPLETED':
            return complete_withdrawal(txn)
        if pawapay_status == 'FAILED':
            return fail_withdrawal(txn)
    return txn


def sync_transaction_with_pawapay(txn: Transaction) -> Transaction:
    if not txn.pawapay_id or txn.status != Transaction.STATUS_PENDING:
        return txn

    client = PawaPayClient()
    try:
        if txn.transaction_type == Transaction.TYPE_DEPOSIT:
            result = client.check_deposit_status(txn.pawapay_id)
        elif txn.transaction_type == Transaction.TYPE_WITHDRAWAL:
            result = client.check_payout_status(txn.pawapay_id)
        else:
            return txn
    except PawaPayError:
        logger.exception('Failed to sync transaction %s with PawaPay.', txn.pk)
        return txn

    if result.get('status') == 'NOT_FOUND':
        return fail_deposit(txn) if txn.transaction_type == Transaction.TYPE_DEPOSIT else fail_withdrawal(txn)

    data = result.get('data') or {}
    pawapay_status = data.get('status')
    if pawapay_status in FINAL_DEPOSIT_STATUSES | FINAL_PAYOUT_STATUSES:
        return _apply_pawapay_status(txn, pawapay_status)

    return txn


def handle_pawapay_callback(payload: dict) -> Transaction | None:
    deposit_id = payload.get('depositId')
    payout_id = payload.get('payoutId')
    status = payload.get('status')

    if deposit_id:
        txn = Transaction.objects.filter(
            pawapay_id=deposit_id,
            transaction_type=Transaction.TYPE_DEPOSIT,
        ).first()
    elif payout_id:
        txn = Transaction.objects.filter(
            pawapay_id=payout_id,
            transaction_type=Transaction.TYPE_WITHDRAWAL,
        ).first()
    else:
        return None

    if not txn or status not in FINAL_DEPOSIT_STATUSES | FINAL_PAYOUT_STATUSES:
        return txn

    return _apply_pawapay_status(txn, status)
