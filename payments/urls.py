from django.urls import path
from . import views

urlpatterns = [
    path('deposit/', views.DepositView.as_view(), name='payment_deposit'),
    path('withdraw/', views.WithdrawalView.as_view(), name='payment_withdraw'),
    path('history/', views.TransactionHistoryView.as_view(), name='payment_history'),
    path('<int:pk>/sync/', views.TransactionSyncView.as_view(), name='payment_sync'),
    path('<int:pk>/', views.TransactionDetailView.as_view(), name='payment_detail'),
    path('pawapay/callback/', views.PawaPayCallbackView.as_view(), name='pawapay_callback'),

    # Admin
    path('admin/all/', views.AdminTransactionListView.as_view(), name='admin_transaction_list'),
    path('admin/stats/', views.payment_stats, name='admin_payment_stats'),
]
