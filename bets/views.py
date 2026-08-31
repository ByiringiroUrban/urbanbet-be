from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import Bet
from .serializers import PlaceBetSerializer, BetSerializer, BetStatusUpdateSerializer


class PlaceBetView(generics.CreateAPIView):
    serializer_class = PlaceBetSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            bet = serializer.save()
            return Response(BetSerializer(bet).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BetHistoryView(generics.ListAPIView):
    serializer_class = BetSerializer

    def get_queryset(self):
        return Bet.objects.filter(user=self.request.user).order_by('-created_at')


class BetDetailView(generics.RetrieveAPIView):
    serializer_class = BetSerializer

    def get_queryset(self):
        return Bet.objects.filter(user=self.request.user)


# ---- Admin views ----

class AdminBetListView(generics.ListAPIView):
    serializer_class = BetSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'currency', 'user']
    queryset = Bet.objects.select_related('user').order_by('-created_at')


class AdminBetStatusUpdateView(generics.UpdateAPIView):
    serializer_class = BetStatusUpdateSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = Bet.objects.all()
    http_method_names = ['patch']


@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def bet_stats(request):
    from django.db.models import Sum, Count

    stats = Bet.objects.aggregate(
        total_bets=Count('id'),
        total_wagered=Sum('amount'),
        total_payout=Sum('potential_winnings'),
    )
    by_status = {}
    for s in [Bet.STATUS_PENDING, Bet.STATUS_WON, Bet.STATUS_LOST, Bet.STATUS_CANCELLED]:
        by_status[s] = Bet.objects.filter(status=s).count()

    return Response({'summary': stats, 'by_status': by_status})
