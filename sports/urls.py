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
]
