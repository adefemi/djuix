from django.urls import path, include
from .views import (
    CreateUserView, LoginView, UpdatePasswordView, MeView,
    UserActivitiesView, VerifyUser, ResendVerification, FaqView,
    DocumentationView, IssueView
)

from rest_framework.routers import DefaultRouter

router = DefaultRouter(trailing_slash=False)

router.register("create-user", CreateUserView, 'create user')
router.register("login", LoginView, 'login')
router.register("update-password", UpdatePasswordView, 'update password')
router.register("me", MeView, 'me')
router.register("activities-log", UserActivitiesView, 'activities log')
router.register("verify-user", VerifyUser, 'verify-user')
router.register("resend-verification", ResendVerification, 'resend-verification')
router.register("faqs", FaqView, 'faqs')
router.register("documentations", DocumentationView, 'documentations')
router.register("issues", IssueView, 'issues')

urlpatterns = [
    path("", include(router.urls))
]

