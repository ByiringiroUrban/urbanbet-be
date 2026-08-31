from django.urls import path
from . import views

urlpatterns = [
    path('place/', views.PlaceBetView.as_view(), name='place_bet'),
    path('history/', views.BetHistoryView.as_view(), name='bet_history'),
    path('<int:pk>/', views.BetDetailView.as_view(), name='bet_detail'),

    # Admin
    path('admin/all/', views.AdminBetListView.as_view(), name='admin_bet_list'),
    path('admin/<int:pk>/status/', views.AdminBetStatusUpdateView.as_view(), name='admin_bet_status'),
    path('admin/stats/', views.bet_stats, name='admin_bet_stats'),
]
