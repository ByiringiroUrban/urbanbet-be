from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import AIPrediction
from .serializers import AIPredictionSerializer, AIPredictionWriteSerializer


class PredictionListView(generics.ListAPIView):
    serializer_class = AIPredictionSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_featured']

    def get_queryset(self):
        return AIPrediction.objects.order_by('-created_at')


class PredictionDetailView(generics.RetrieveAPIView):
    serializer_class = AIPredictionSerializer
    permission_classes = [permissions.AllowAny]
    queryset = AIPrediction.objects.all()


class FeaturedPredictionListView(generics.ListAPIView):
    serializer_class = AIPredictionSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return AIPrediction.objects.filter(is_featured=True).order_by('-created_at')


# ---- Admin views ----

class AdminPredictionCreateView(generics.CreateAPIView):
    serializer_class = AIPredictionWriteSerializer
    permission_classes = [permissions.IsAdminUser]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class AdminPredictionUpdateView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AIPredictionWriteSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = AIPrediction.objects.all()
