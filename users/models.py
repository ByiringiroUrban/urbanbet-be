from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', User.ADMIN)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    ADMIN = 'admin'
    USER = 'user'
    ROLE_CHOICES = [
        (ADMIN, 'Admin'),
        (USER, 'User'),
    ]

    CURRENCY_USD = 'USD'
    CURRENCY_RWF = 'RWF'
    CURRENCY_CHOICES = [
        (CURRENCY_USD, 'USD'),
        (CURRENCY_RWF, 'RWF'),
    ]

    PROVIDER_EMAIL = 'email'
    PROVIDER_GOOGLE = 'google'
    PROVIDER_FACEBOOK = 'facebook'
    PROVIDER_APPLE = 'apple'
    PROVIDER_CHOICES = [
        (PROVIDER_EMAIL, 'Email'),
        (PROVIDER_GOOGLE, 'Google'),
        (PROVIDER_FACEBOOK, 'Facebook'),
        (PROVIDER_APPLE, 'Apple'),
    ]

    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    balance = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default=CURRENCY_RWF)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=USER)
    provider = models.CharField(max_length=10, choices=PROVIDER_CHOICES, default=PROVIDER_EMAIL)
    provider_user_id = models.CharField(max_length=255, blank=True)
    avatar = models.URLField(max_length=500, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    last_login = models.DateTimeField(null=True, blank=True)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    class Meta:
        db_table = 'users'
        ordering = ['-date_joined']

    def __str__(self):
        return self.email

    @property
    def is_admin(self):
        return self.role == self.ADMIN
