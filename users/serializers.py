from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import User


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'name', 'phone', 'password', 'password_confirm', 'currency']

    def validate(self, attrs):
        if attrs['password'] != attrs.pop('password_confirm'):
            raise serializers.ValidationError({'password_confirm': 'Passwords do not match.'})
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            name=validated_data.get('name', ''),
            phone=validated_data.get('phone', ''),
            password=validated_data['password'],
            currency=validated_data.get('currency', User.CURRENCY_RWF),
            balance=0,
        )
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(username=attrs['email'], password=attrs['password'])
        if not user:
            raise serializers.ValidationError('Invalid email or password.')
        if not user.is_active:
            raise serializers.ValidationError('Account is disabled.')
        attrs['user'] = user
        return attrs


class SocialLoginSerializer(serializers.Serializer):
    provider = serializers.ChoiceField(choices=['google', 'facebook', 'apple'])
    provider_user_id = serializers.CharField()
    email = serializers.EmailField()
    name = serializers.CharField(required=False, default='')


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'email', 'name', 'phone', 'balance', 'currency',
            'role', 'provider', 'avatar', 'is_verified', 'date_joined', 'last_login',
        ]
        read_only_fields = ['id', 'email', 'balance', 'role', 'provider', 'date_joined', 'last_login']


class UpdateProfileSerializer(serializers.ModelSerializer):
    avatar = serializers.URLField(required=False, allow_null=True, allow_blank=True)

    class Meta:
        model = User
        fields = ['name', 'phone', 'currency', 'avatar']

    def validate_avatar(self, value):
        if not value:
            return None
        if not value.startswith('https://'):
            raise serializers.ValidationError('Avatar must be a secure HTTPS URL.')
        return value



class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)
    new_password_confirm = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs.pop('new_password_confirm'):
            raise serializers.ValidationError({'new_password_confirm': 'Passwords do not match.'})
        return attrs


class UserListSerializer(serializers.ModelSerializer):
    """Lightweight serializer used by the admin user list endpoint."""
    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'balance', 'currency', 'role', 'is_active', 'date_joined']


class TokenPairSerializer(serializers.Serializer):
    """Used to return access + refresh tokens in responses."""
    access = serializers.CharField()
    refresh = serializers.CharField()
    user = UserProfileSerializer()

    @staticmethod
    def get_tokens(user):
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserProfileSerializer(user).data,
        }


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("No user is registered with this email address.")
        return value


class ResetPasswordSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs['password'] != attrs.pop('password_confirm'):
            raise serializers.ValidationError({'password_confirm': 'Passwords do not match.'})
        return attrs

