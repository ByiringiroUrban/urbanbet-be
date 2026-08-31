from django.urls import path
from . import views

urlpatterns = [
    path('games/', views.CasinoGameListView.as_view(), name='casino_game_list'),
    path('games/<int:pk>/', views.CasinoGameDetailView.as_view(), name='casino_game_detail'),
    path('sessions/start/', views.StartSessionView.as_view(), name='casino_start_session'),
    path('sessions/<int:pk>/end/', views.EndSessionView.as_view(), name='casino_end_session'),
    path('sessions/<int:pk>/spin/', views.spin_slot, name='casino_spin'),
    path('sessions/history/', views.SessionHistoryView.as_view(), name='casino_session_history'),

    # Admin
    path('admin/games/', views.AdminGameCreateView.as_view(), name='admin_casino_game_create'),
    path('admin/games/<int:pk>/', views.AdminGameUpdateView.as_view(), name='admin_casino_game_update'),
]
