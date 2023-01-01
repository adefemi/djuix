from django.contrib import admin
from .models import CustomUser, UserActivities, VerificationUser


admin.site.register((CustomUser, UserActivities, VerificationUser))