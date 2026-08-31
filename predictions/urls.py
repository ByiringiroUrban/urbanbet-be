from django.urls import path
from . import views

urlpatterns = [
    path('', views.PredictionListView.as_view(), name='prediction_list'),
    path('featured/', views.FeaturedPredictionListView.as_view(), name='prediction_featured'),
    path('<int:pk>/', views.PredictionDetailView.as_view(), name='prediction_detail'),

    # Admin
    path('admin/create/', views.AdminPredictionCreateView.as_view(), name='admin_prediction_create'),
    path('admin/<int:pk>/', views.AdminPredictionUpdateView.as_view(), name='admin_prediction_update'),
]
