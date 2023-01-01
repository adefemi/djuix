from rest_framework.viewsets import ModelViewSet
from .serializers import (
    AuthSerializer, CustomUser, UpdatePasswordSerializer,
    CustomUserSerializer, UserActivities, UserActivitiesSerializer, CreateUserSerializer,
    VerifyUserSerializer, ResentEmailSerializer
)
from .models import VerificationUser
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from django.utils import timezone
from djuix.utils import CustomPagination, get_access_token, get_query
from djuix.functions import generate_random_string, send_verification_email
from datetime import timedelta


def add_user_activity(user, action):
    UserActivities.objects.create(
        user_id=user.id,
        email=user.email,
        action=action
    )
    
def send_v_mail(user):
    v_token = generate_random_string(10)
    expiry = timezone.now() + timedelta(days=1)
    
    VerificationUser.objects.create(user=user, expiry=expiry, token=v_token)
    
    send_verification_email(user, v_token)
    
class CreateUserView(ModelViewSet):
    http_method_names = ["post"]
    queryset = CustomUser.objects.all()
    serializer_class = CreateUserSerializer
    permission_classes = []

    def create(self, request):
        valid_request = self.serializer_class(data=request.data)
        valid_request.is_valid(raise_exception=True)

        user = CustomUser.objects.create_user(**valid_request.validated_data)
        
        send_v_mail(user)

        return Response(
            {"success": "User created successfully. We've sent a verification mail to your email address."},
            status=status.HTTP_201_CREATED
        )


class LoginView(ModelViewSet):
    http_method_names = ["post"]
    queryset = CustomUser.objects.all()
    serializer_class = AuthSerializer
    permission_classes = []

    def create(self, request):
        valid_request = self.serializer_class(data=request.data)
        valid_request.is_valid(raise_exception=True)

        user = authenticate(
            username=valid_request.validated_data["email"],
            password=valid_request.validated_data.get("password", None)
        )

        if not user:
            return Response(
                {"error": "Invalid email or password"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        if not user.is_verified:
            return Response("Access Denied", status=203)

        access = get_access_token({"user_id": user.id}, 1)
        mystatus = 200

        user.last_login = timezone.now()
        user.save()
        
        if user.removed_folder:
            mystatus = 202

        add_user_activity(user, "logged in")

        return Response({"access": access}, status=mystatus)


class UpdatePasswordView(ModelViewSet):
    serializer_class = UpdatePasswordSerializer
    http_method_names = ["post"]
    queryset = CustomUser.objects.all()
    permission_classes = []

    def create(self, request):
        valid_request = self.serializer_class(data=request.data)
        valid_request.is_valid(raise_exception=True)

        user = CustomUser.objects.filter(
            id=valid_request.validated_data["user_id"])

        if not user:
            raise Exception("User with id not found")

        user = user[0]

        user.set_password(valid_request.validated_data["password"])
        user.save()

        add_user_activity(user, "updated password")

        return Response({"success": "User password updated"})


class MeView(ModelViewSet):
    serializer_class = CustomUserSerializer
    http_method_names = ["get"]
    queryset = CustomUser.objects.all()

    def list(self, request):
        data = self.serializer_class(request.user).data
        return Response(data)


class UserActivitiesView(ModelViewSet):
    serializer_class = UserActivitiesSerializer
    http_method_names = ["get"]
    queryset = UserActivities.objects.all()
    pagination_class = CustomPagination
    
    def get_queryset(self):
        if self.request.method.lower() != "get":
            return self.queryset

        data = self.request.query_params.dict()
        data.pop("page", None)
        keyword = data.pop("keyword", None)

        results = self.queryset.filter(**data)

        if keyword:
            search_fields = (
                "first_name", "last_name", "email", "action"
            )
            query = get_query(keyword, search_fields)
            results = results.filter(query)
        
        return results
    

class VerifyUser(ModelViewSet):
    serializer_class = VerifyUserSerializer
    http_method_names = ["post"]
    permission_classes = []
    
    def create(self, request):
        data = self.serializer_class(data=request.data)
        data.is_valid(raise_exception=True)
        
        try:
            current_time = timezone.now()
            v_user = VerificationUser.objects.get(token=data.validated_data["token"], expiry__gt=current_time)
            
        except Exception:
            raise Exception("Provided token is either invalid or expired")
        
        v_user.user.is_verified = True
        v_user.user.save()
        v_user.delete()
        
        return Response("Verification Successful")
    

class ResendVerification(ModelViewSet):
    serializer_class = ResentEmailSerializer
    http_method_names = ["post"]
    permission_classes = []
    
    def create(self, request):
        data = self.serializer_class(data=request.data)
        data.is_valid(raise_exception=True)
        
        try:
            user = CustomUser.objects.get(email=data.validated_data["email"])
            VerificationUser.objects.filter(user=user).delete()
            send_v_mail(user)
        except Exception:
            pass
        
        return Response("Verification mail sent successfully")
    
    