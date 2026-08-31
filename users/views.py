from django.utils import timezone
from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings

from .models import User
from .cloudinary_service import is_cloudinary_configured, upload_avatar_image
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    SocialLoginSerializer,
    UserProfileSerializer,
    UpdateProfileSerializer,
    ChangePasswordSerializer,
    UserListSerializer,
    TokenPairSerializer,
    ForgotPasswordSerializer,
    ResetPasswordSerializer,
)


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(TokenPairSerializer.get_tokens(user), status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            user.last_login = timezone.now()
            user.save(update_fields=['last_login'])
            return Response(TokenPairSerializer.get_tokens(user))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SocialLoginView(APIView):
    """
    Handles social login (Google / Facebook / Apple).
    Creates user if not exists, then returns JWT tokens.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = SocialLoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        user, created = User.objects.get_or_create(
            email=data['email'],
            defaults={
                'name': data.get('name', ''),
                'provider': data['provider'],
                'provider_user_id': data['provider_user_id'],
                'balance': 0,
                'currency': User.CURRENCY_RWF,
                'is_verified': True,
            }
        )
        if not created:
            user.last_login = timezone.now()
            user.save(update_fields=['last_login'])

        return Response(
            TokenPairSerializer.get_tokens(user),
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class LogoutView(APIView):
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return Response({'detail': 'Refresh token required.'}, status=status.HTTP_400_BAD_REQUEST)
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'detail': 'Logged out successfully.'}, status=status.HTTP_205_RESET_CONTENT)
        except TokenError:
            return Response({'detail': 'Invalid or expired token.'}, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer

    def get_object(self):
        return self.request.user

    def put(self, request, *args, **kwargs):
        serializer = UpdateProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(UserProfileSerializer(request.user).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):
        return self.put(request, *args, **kwargs)


class AvatarUploadView(APIView):
    MAX_FILE_SIZE = 2 * 1024 * 1024
    ALLOWED_CONTENT_TYPES = {
        'image/jpeg',
        'image/png',
        'image/webp',
        'image/gif',
    }

    def post(self, request):
        if not is_cloudinary_configured():
            return Response(
                {
                    'detail': (
                        'Cloudinary is not configured. Set CLOUDINARY_CLOUD_NAME, '
                        'CLOUDINARY_API_KEY, and CLOUDINARY_API_SECRET in backend/.env.'
                    ),
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        uploaded_file = request.FILES.get('avatar')
        if not uploaded_file:
            return Response({'avatar': 'No image file provided.'}, status=status.HTTP_400_BAD_REQUEST)

        if uploaded_file.content_type not in self.ALLOWED_CONTENT_TYPES:
            return Response(
                {'avatar': 'Unsupported image type. Use JPEG, PNG, WEBP, or GIF.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if uploaded_file.size > self.MAX_FILE_SIZE:
            return Response(
                {'avatar': 'Image must be 2 MB or smaller.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            secure_url = upload_avatar_image(file_obj=uploaded_file, user_id=request.user.id)
        except Exception as exc:
            return Response(
                {'detail': f'Cloudinary upload failed: {exc}'},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        request.user.avatar = secure_url
        request.user.save(update_fields=['avatar'])

        return Response(
            {
                'avatar': secure_url,
                'user': UserProfileSerializer(request.user).data,
            },
            status=status.HTTP_200_OK,
        )


class ChangePasswordView(APIView):
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        if not user.check_password(serializer.validated_data['old_password']):
            return Response({'old_password': 'Incorrect password.'}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({'detail': 'Password changed successfully.'})


class DeleteAccountView(APIView):
    def delete(self, request):
        user = request.user
        user.is_active = False
        user.save(update_fields=['is_active'])
        return Response({'detail': 'Account deactivated.'}, status=status.HTTP_204_NO_CONTENT)


# ---- Admin views ----

class AdminUserListView(generics.ListAPIView):
    serializer_class = UserListSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = User.objects.all().order_by('-date_joined')


class AdminUserDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserListSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = User.objects.all()


@api_view(['POST'])
@permission_classes([permissions.IsAdminUser])
def adjust_balance(request, pk):
    """Admin: add or subtract from a user's balance."""
    try:
        user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

    amount = request.data.get('amount')
    if amount is None:
        return Response({'detail': 'Amount is required.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        amount = float(amount)
    except (TypeError, ValueError):
        return Response({'detail': 'Amount must be a number.'}, status=status.HTTP_400_BAD_REQUEST)

    user.balance += amount
    if user.balance < 0:
        return Response({'detail': 'Insufficient balance.'}, status=status.HTTP_400_BAD_REQUEST)
    user.save(update_fields=['balance'])
    return Response({'balance': str(user.balance)})


class ForgotPasswordView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data['email']
        user = User.objects.get(email=email)

        # Generate token and uid
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        # Build reset link
        # Use HTTP_REFERER or default origin to point to front-end page
        referer = request.META.get('HTTP_REFERER')
        if referer:
            from urllib.parse import urlparse
            parsed_referer = urlparse(referer)
            frontend_origin = f"{parsed_referer.scheme}://{parsed_referer.netloc}"
        else:
            frontend_origin = "http://localhost:8080" # Default frontend port

        reset_link = f"{frontend_origin}/reset-password?token={token}&uid={uid}"

        # Send email
        subject = "Password Reset Requested - Urban Bet"
        message = (
            f"Hello {user.name or 'User'},\n\n"
            f"You are receiving this email because we received a password reset request for your account.\n\n"
            f"Please click the link below to reset your password:\n"
            f"{reset_link}\n\n"
            f"If you did not request a password reset, no further action is required.\n\n"
            f"Best regards,\n"
            f"Urban Bet Team"
        )
        
        send_mail(
            subject=subject,
            message=message,
            from_email=None,  # Uses DEFAULT_FROM_EMAIL
            recipient_list=[email],
            fail_silently=False,
        )

        response_data = {'detail': 'Password reset link sent to your email.'}
        if settings.DEBUG:
            response_data['reset_link'] = reset_link

        return Response(response_data, status=status.HTTP_200_OK)


class ResetPasswordView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        uid_b64 = serializer.validated_data['uid']
        token = serializer.validated_data['token']
        new_password = serializer.validated_data['password']

        try:
            uid = force_str(urlsafe_base64_decode(uid_b64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({'detail': 'Invalid user ID.'}, status=status.HTTP_400_BAD_REQUEST)

        if not default_token_generator.check_token(user, token):
            return Response({'detail': 'Invalid or expired reset token.'}, status=status.HTTP_400_BAD_REQUEST)

        # Token is valid, set password
        user.set_password(new_password)
        user.save()

        return Response({'detail': 'Password has been reset successfully.'}, status=status.HTTP_200_OK)

