from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),

    # API schema & docs
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    # JWT token refresh
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # App routes
    path('api/auth/', include('users.urls')),
    path('api/sports/', include('sports.urls')),
    path('api/bets/', include('bets.urls')),
    path('api/payments/', include('payments.urls')),
    path('api/predictions/', include('predictions.urls')),
    path('api/casino/', include('casino.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
