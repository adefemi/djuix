from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser, PermissionsMixin, BaseUserManager
)

class CustomUserManager(BaseUserManager):
    
    def create_user(self, username, email, password, **extra_fields):
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        if not email:
            raise ValueError("Email field is required")
        
        if not username:
            raise ValueError("Username field is required")

        user = self.create_user(username, email, password, **extra_fields)
        return user


class CustomUser(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=100, null=True)
    username = models.CharField(max_length=100, unique=True)
    last_name = models.CharField(max_length=100, null=True)
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    last_login = models.DateTimeField(null=True)
    last_activity = models.DateTimeField(null=True)
    removed_folder = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    objects = CustomUserManager()
    
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

    class Meta:
        ordering = ("created_at", )


class UserActivities(models.Model):
    user = models.ForeignKey(
        CustomUser, related_name="user_activities", null=True, on_delete=models.SET_NULL)
    email = models.EmailField()
    action = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at", )

    def __str__(self):
        return f"{self.email} {self.action} on {self.created_at.strftime('%Y-%m-%d %H:%M')}"