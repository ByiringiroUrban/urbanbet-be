from rest_framework import generics, permissions, filters, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone

from .models import Sport, Country, League, SportEvent, Market
from .serializers import (
    SportSerializer,
    CountrySerializer,
    LeagueSerializer,
    MarketSerializer,
    SportEventListSerializer,
    SportEventDetailSerializer,
    SportEventWriteSerializer,
)


class SportListView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = SportSerializer
    queryset = Sport.objects.filter(is_active=True)


class CountryListView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = CountrySerializer
    queryset = Country.objects.all()


class LeagueListView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = LeagueSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['sport', 'country']
    queryset = League.objects.filter(is_active=True).select_related('sport', 'country')


class SportEventListView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = SportEventListSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['sport', 'league', 'country', 'status']
    search_fields = ['home_team', 'away_team', 'league__name']

    def get_queryset(self):
        qs = SportEvent.objects.select_related('sport', 'league', 'country')
        sport_name = self.request.query_params.get('sport_name')
        country_name = self.request.query_params.get('country_name')
        league_name = self.request.query_params.get('league_name')
        is_live = self.request.query_params.get('is_live')

        if sport_name:
            qs = qs.filter(sport__name__iexact=sport_name)
        if country_name:
            qs = qs.filter(country__name__iexact=country_name)
        if league_name:
            qs = qs.filter(league__name__iexact=league_name)
        if is_live is not None:
            if is_live.lower() == 'true':
                qs = qs.filter(status=SportEvent.STATUS_LIVE)
            else:
                qs = qs.exclude(status=SportEvent.STATUS_LIVE)
        return qs.order_by('start_time')


class LiveEventsView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = SportEventListSerializer

    def get_queryset(self):
        return SportEvent.objects.filter(
            status=SportEvent.STATUS_LIVE
        ).select_related('sport', 'league', 'country').order_by('start_time')


class SportEventDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = SportEventDetailSerializer
    queryset = SportEvent.objects.select_related('sport', 'league', 'country').prefetch_related('markets')


class MarketListView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = MarketSerializer

    def get_queryset(self):
        event_id = self.kwargs.get('event_id')
        return Market.objects.filter(event_id=event_id, is_active=True)


# ---- Admin views ----

class AdminEventCreateView(generics.CreateAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = SportEventWriteSerializer


class AdminEventUpdateView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = SportEventWriteSerializer
    queryset = SportEvent.objects.all()


@api_view(['POST'])
@permission_classes([permissions.IsAdminUser])
def update_event_score(request, pk):
    try:
        event = SportEvent.objects.get(pk=pk)
    except SportEvent.DoesNotExist:
        return Response({'detail': 'Event not found.'}, status=status.HTTP_404_NOT_FOUND)

    home_score = request.data.get('home_score')
    away_score = request.data.get('away_score')
    new_status = request.data.get('status')

    if home_score is not None:
        event.home_score = home_score
    if away_score is not None:
        event.away_score = away_score
    if new_status:
        event.status = new_status

    event.save()
    return Response(SportEventDetailSerializer(event).data)


class AdminSportCreateView(generics.CreateAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = SportSerializer


class AdminSportUpdateView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = SportSerializer
    queryset = Sport.objects.all()


class AdminLeagueCreateView(generics.CreateAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = LeagueSerializer


class AdminLeagueUpdateView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = LeagueSerializer
    queryset = League.objects.all()


class AdminCountryCreateView(generics.CreateAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = CountrySerializer


class AdminCountryUpdateView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = CountrySerializer
    queryset = Country.objects.all()
