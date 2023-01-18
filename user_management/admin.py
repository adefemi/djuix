from django.contrib import admin
from .models import CustomUser, UserActivities, VerificationUser, UserStatus


admin.site.register((CustomUser, UserActivities, VerificationUser, UserStatus))