from django.urls import path
from . import views

urlpatterns = [
    path('', views.SportListView.as_view(), name='sport_list'),
    path('countries/', views.CountryListView.as_view(), name='country_list'),
    path('leagues/', views.LeagueListView.as_view(), name='league_list'),
    path('events/', views.SportEventListView.as_view(), name='event_list'),
    path('events/live/', views.LiveEventsView.as_view(), name='live_events'),
    path('events/<int:pk>/', views.SportEventDetailView.as_view(), name='event_detail'),
    path('events/<int:event_id>/markets/', views.MarketListView.as_view(), name='market_list'),

    # Admin
    path('admin/events/', views.AdminEventCreateView.as_view(), name='admin_event_create'),
    path('admin/events/<int:pk>/', views.AdminEventUpdateView.as_view(), name='admin_event_update'),
    path('admin/events/<int:pk>/score/', views.update_event_score, name='admin_update_score'),

    path('admin/sports/', views.AdminSportCreateView.as_view(), name='admin_sport_create'),
    path('admin/sports/<int:pk>/', views.AdminSportUpdateView.as_view(), name='admin_sport_update'),
    
    path('admin/leagues/', views.AdminLeagueCreateView.as_view(), name='admin_league_create'),
    path('admin/leagues/<int:pk>/', views.AdminLeagueUpdateView.as_view(), name='admin_league_update'),
    
    path('admin/countries/', views.AdminCountryCreateView.as_view(), name='admin_country_create'),
    path('admin/countries/<int:pk>/', views.AdminCountryUpdateView.as_view(), name='admin_country_update'),
]
