import uuid
import logging
from decimal import Decimal

from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend

from .models import Transaction
from .pawapay import (
    PawaPayClient,
    PawaPayError,
    format_amount,
    resolve_phone_and_provider,
    uses_pawapay,
)
from .serializers import DepositSerializer, WithdrawalSerializer, TransactionSerializer
from .services import (
    complete_withdrawal,
    fail_deposit,
    fail_withdrawal,
    handle_pawapay_callback,
    sync_transaction_with_pawapay,
)

logger = logging.getLogger(__name__)


def _generate_reference(prefix='TXN'):
    return f"{prefix}-{uuid.uuid4().hex[:12].upper()}"


def _transaction_response(txn, user, *, message: str, pending: bool = False):
    user.refresh_from_db(fields=['balance'])
    payload = {
        'success': True,
        'pending': pending,
        'transaction_id': txn.id,
        'reference': txn.reference,
        'status': txn.status,
        'message': message,
        'new_balance': str(user.balance),
    }
    status_code = status.HTTP_202_ACCEPTED if pending else status.HTTP_201_CREATED
    return Response(payload, status=status_code)


class DepositView(generics.GenericAPIView):
    serializer_class = DepositSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        user = request.user
        reference = _generate_reference('DEP')
        method = data['method']

        if not uses_pawapay(method):
            txn = Transaction.objects.create(
                user=user,
                transaction_type=Transaction.TYPE_DEPOSIT,
                method=method,
                amount=data['amount'],
                currency=data['currency'],
                status=Transaction.STATUS_COMPLETED,
                reference=reference,
                description=data.get('description', 'Deposit'),
                phone_number=data.get('phone_number', ''),
            )

            user.balance += Decimal(str(data['amount']))
            user.save(update_fields=['balance'])

            return _transaction_response(
                txn,
                user,
                message=f"Deposit of {data['currency']} {data['amount']:,} processed successfully.",
            )

        deposit_id = str(uuid.uuid4())
        phone_number, provider = resolve_phone_and_provider(method, data['phone_number'])

        txn = Transaction.objects.create(
            user=user,
            transaction_type=Transaction.TYPE_DEPOSIT,
            method=method,
            amount=data['amount'],
            currency=data['currency'],
            status=Transaction.STATUS_PENDING,
            reference=reference,
            pawapay_id=deposit_id,
            description=data.get('description', 'Deposit'),
            phone_number=phone_number,
        )

        client = PawaPayClient()
        try:
            result = client.initiate_deposit(
                deposit_id=deposit_id,
                amount=format_amount(data['amount']),
                currency=data['currency'],
                phone_number=phone_number,
                provider=provider,
                customer_message=data.get('description', 'UrbanBet deposit') or 'UrbanBet deposit',
            )
        except PawaPayError as exc:
            fail_deposit(txn)
            return Response(
                {'success': False, 'message': str(exc)},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        initiation_status = result.get('status')
        if initiation_status == 'REJECTED':
            fail_deposit(txn)
            failure = result.get('failureReason', {})
            message = failure.get('failureMessage') or 'Deposit was rejected by PawaPay.'
            return Response({'success': False, 'message': message}, status=status.HTTP_400_BAD_REQUEST)

        if initiation_status in ('ACCEPTED', 'DUPLICATE_IGNORED'):
            txn = sync_transaction_with_pawapay(txn)
            if txn.status == Transaction.STATUS_COMPLETED:
                return _transaction_response(
                    txn,
                    user,
                    message=f"Deposit of {data['currency']} {data['amount']:,} completed successfully.",
                )
            if txn.status == Transaction.STATUS_FAILED:
                return Response(
                    {'success': False, 'message': 'Deposit failed. Please try again.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            return _transaction_response(
                txn,
                user,
                pending=True,
                message=(
                    'Deposit initiated via PawaPay. '
                    'Approve the payment on your phone or wait for confirmation.'
                ),
            )

        fail_deposit(txn)
        return Response(
            {'success': False, 'message': 'Unexpected response from PawaPay.'},
            status=status.HTTP_502_BAD_GATEWAY,
        )


class WithdrawalView(generics.GenericAPIView):
    serializer_class = WithdrawalSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        user = request.user

        if user.balance < Decimal(str(data['amount'])):
            return Response(
                {'detail': 'Insufficient balance.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        reference = _generate_reference('WIT')
        method = data['method']

        if not uses_pawapay(method):
            txn = Transaction.objects.create(
                user=user,
                transaction_type=Transaction.TYPE_WITHDRAWAL,
                method=method,
                amount=data['amount'],
                currency=data['currency'],
                status=Transaction.STATUS_COMPLETED,
                reference=reference,
                phone_number=data.get('phone_number', ''),
            )

            user.balance -= Decimal(str(data['amount']))
            user.save(update_fields=['balance'])

            return _transaction_response(
                txn,
                user,
                message=f"Withdrawal of {data['currency']} {data['amount']:,} processed successfully.",
            )

        payout_id = str(uuid.uuid4())
        phone_number, provider = resolve_phone_and_provider(method, data['phone_number'])

        user.balance -= Decimal(str(data['amount']))
        user.save(update_fields=['balance'])

        txn = Transaction.objects.create(
            user=user,
            transaction_type=Transaction.TYPE_WITHDRAWAL,
            method=method,
            amount=data['amount'],
            currency=data['currency'],
            status=Transaction.STATUS_PENDING,
            reference=reference,
            pawapay_id=payout_id,
            phone_number=phone_number,
        )

        client = PawaPayClient()
        try:
            result = client.initiate_payout(
                payout_id=payout_id,
                amount=format_amount(data['amount']),
                currency=data['currency'],
                phone_number=phone_number,
                provider=provider,
            )
        except PawaPayError as exc:
            fail_withdrawal(txn)
            return Response(
                {'success': False, 'message': str(exc)},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        initiation_status = result.get('status')
        if initiation_status == 'REJECTED':
            fail_withdrawal(txn)
            failure = result.get('failureReason', {})
            message = failure.get('failureMessage') or 'Withdrawal was rejected by PawaPay.'
            return Response({'success': False, 'message': message}, status=status.HTTP_400_BAD_REQUEST)

        if initiation_status in ('ACCEPTED', 'DUPLICATE_IGNORED'):
            txn = sync_transaction_with_pawapay(txn)
            if txn.status == Transaction.STATUS_COMPLETED:
                return _transaction_response(
                    txn,
                    user,
                    message=f"Withdrawal of {data['currency']} {data['amount']:,} completed successfully.",
                )
            if txn.status == Transaction.STATUS_FAILED:
                return Response(
                    {'success': False, 'message': 'Withdrawal failed. Your balance has been restored.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            return _transaction_response(
                txn,
                user,
                pending=True,
                message='Withdrawal initiated via PawaPay. Waiting for confirmation.',
            )

        fail_withdrawal(txn)
        return Response(
            {'success': False, 'message': 'Unexpected response from PawaPay.'},
            status=status.HTTP_502_BAD_GATEWAY,
        )


class TransactionHistoryView(generics.ListAPIView):
    serializer_class = TransactionSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['transaction_type', 'status', 'currency']

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user).order_by('-created_at')


class TransactionDetailView(generics.RetrieveAPIView):
    serializer_class = TransactionSerializer

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)


class TransactionSyncView(generics.GenericAPIView):
    def post(self, request, pk):
        txn = Transaction.objects.filter(user=request.user, pk=pk).first()
        if not txn:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

        txn = sync_transaction_with_pawapay(txn)
        user = request.user
        user.refresh_from_db(fields=['balance'])

        return Response({
            'success': txn.status == Transaction.STATUS_COMPLETED,
            'pending': txn.status == Transaction.STATUS_PENDING,
            'status': txn.status,
            'transaction_id': txn.id,
            'reference': txn.reference,
            'new_balance': str(user.balance),
            'message': {
                Transaction.STATUS_COMPLETED: 'Transaction completed successfully.',
                Transaction.STATUS_PENDING: 'Transaction is still processing.',
                Transaction.STATUS_FAILED: 'Transaction failed.',
            }.get(txn.status, 'Transaction updated.'),
        })


class PawaPayCallbackView(APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        payload = request.data
        logger.info('PawaPay callback received: %s', payload.get('depositId') or payload.get('payoutId'))

        txn = handle_pawapay_callback(payload)
        if txn is None:
            return Response({'received': True}, status=status.HTTP_200_OK)

        return Response({
            'received': True,
            'transaction_id': txn.id,
            'status': txn.status,
        })


# ---- Admin views ----

class AdminTransactionListView(generics.ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['transaction_type', 'status', 'currency', 'user']
    queryset = Transaction.objects.select_related('user').order_by('-created_at')


@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def payment_stats(request):
    from django.db.models import Sum, Count

    deposits = Transaction.objects.filter(
        transaction_type=Transaction.TYPE_DEPOSIT,
        status=Transaction.STATUS_COMPLETED,
    ).aggregate(total=Sum('amount'), count=Count('id'))

    withdrawals = Transaction.objects.filter(
        transaction_type=Transaction.TYPE_WITHDRAWAL,
        status=Transaction.STATUS_COMPLETED,
    ).aggregate(total=Sum('amount'), count=Count('id'))

    return Response({
        'deposits': deposits,
        'withdrawals': withdrawals,
    })
