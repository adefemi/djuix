from rest_framework.viewsets import ModelViewSet
from .serializers import (
    AuthSerializer, CustomUser, UpdatePasswordSerializer,
    CustomUserSerializer, UserActivities, UserActivitiesSerializer, CreateUserSerializer
)
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from datetime import datetime
from djuix.utils import CustomPagination, get_access_token, get_query


def add_user_activity(user, action):
    UserActivities.objects.create(
        user_id=user.id,
        email=user.email,
        action=action
    )
    
class CreateUserView(ModelViewSet):
    http_method_names = ["post"]
    queryset = CustomUser.objects.all()
    serializer_class = CreateUserSerializer
    permission_classes = []

    def create(self, request):
        valid_request = self.serializer_class(data=request.data)
        valid_request.is_valid(raise_exception=True)

        CustomUser.objects.create_user(**valid_request.validated_data)

        return Response(
            {"success": "User created successfully"},
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

        access = get_access_token({"user_id": user.id}, 1)

        user.last_login = datetime.now()
        user.save()

        add_user_activity(user, "logged in")

        return Response({"access": access})


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