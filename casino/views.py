import random
from decimal import Decimal
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import CasinoGame, CasinoGameSession
from .serializers import (
    CasinoGameSerializer,
    CasinoGameWriteSerializer,
    StartSessionSerializer,
    CasinoGameSessionSerializer,
)


class CasinoGameListView(generics.ListAPIView):
    serializer_class = CasinoGameSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category', 'is_new', 'is_popular', 'provider']

    def get_queryset(self):
        return CasinoGame.objects.filter(is_active=True)


class CasinoGameDetailView(generics.RetrieveAPIView):
    serializer_class = CasinoGameSerializer
    permission_classes = [permissions.AllowAny]
    queryset = CasinoGame.objects.filter(is_active=True)


class StartSessionView(generics.GenericAPIView):
    serializer_class = StartSessionSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        game_id = serializer.validated_data['game_id']
        currency = serializer.validated_data['currency']

        try:
            game = CasinoGame.objects.get(pk=game_id, is_active=True)
        except CasinoGame.DoesNotExist:
            return Response({'detail': 'Game not found.'}, status=status.HTTP_404_NOT_FOUND)

        session = CasinoGameSession.objects.create(
            user=request.user,
            game=game,
            currency=currency,
        )
        return Response(CasinoGameSessionSerializer(session).data, status=status.HTTP_201_CREATED)


class EndSessionView(generics.GenericAPIView):
    def post(self, request, pk):
        try:
            session = CasinoGameSession.objects.get(pk=pk, user=request.user, status=CasinoGameSession.STATUS_ACTIVE)
        except CasinoGameSession.DoesNotExist:
            return Response({'detail': 'Active session not found.'}, status=status.HTTP_404_NOT_FOUND)

        session.status = CasinoGameSession.STATUS_FINISHED
        session.ended_at = timezone.now()
        session.save(update_fields=['status', 'ended_at'])

        return Response(CasinoGameSessionSerializer(session).data)


@api_view(['POST'])
def spin_slot(request, pk):
    """
    Simulate a single slot spin within an active session.
    Deducts bet amount from user balance, applies RTP-based random win.
    """
    try:
        session = CasinoGameSession.objects.select_related('game', 'user').get(
            pk=pk, user=request.user, status=CasinoGameSession.STATUS_ACTIVE
        )
    except CasinoGameSession.DoesNotExist:
        return Response({'detail': 'Active session not found.'}, status=status.HTTP_404_NOT_FOUND)

    bet_amount = request.data.get('bet_amount')
    if not bet_amount:
        return Response({'detail': 'bet_amount is required.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        bet_amount = Decimal(str(bet_amount))
    except Exception:
        return Response({'detail': 'Invalid bet_amount.'}, status=status.HTTP_400_BAD_REQUEST)

    game = session.game
    if bet_amount < game.min_bet or bet_amount > game.max_bet:
        return Response(
            {'detail': f'Bet must be between {game.min_bet} and {game.max_bet}.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = session.user
    if user.balance < bet_amount:
        return Response({'detail': 'Insufficient balance.'}, status=status.HTTP_400_BAD_REQUEST)

    rtp = float(game.rtp or 96) / 100
    win = random.random() < rtp
    win_amount = Decimal('0')
    if win:
        multiplier = Decimal(str(round(random.uniform(1.1, 10.0), 2)))
        win_amount = bet_amount * multiplier

    user.balance -= bet_amount
    user.balance += win_amount
    user.save(update_fields=['balance'])

    session.amount_wagered += bet_amount
    session.amount_won += win_amount
    session.save(update_fields=['amount_wagered', 'amount_won'])

    return Response({
        'win': win,
        'bet_amount': str(bet_amount),
        'win_amount': str(win_amount),
        'new_balance': str(user.balance),
    })


class SessionHistoryView(generics.ListAPIView):
    serializer_class = CasinoGameSessionSerializer

    def get_queryset(self):
        return CasinoGameSession.objects.filter(user=self.request.user).order_by('-started_at')


# ---- Admin views ----

class AdminGameCreateView(generics.CreateAPIView):
    serializer_class = CasinoGameWriteSerializer
    permission_classes = [permissions.IsAdminUser]


class AdminGameUpdateView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CasinoGameWriteSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = CasinoGame.objects.all()
