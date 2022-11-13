from rest_framework.permissions import BasePermission
from .utils import decodeJWT

class IsAuthenticatedCustom(BasePermission):
    
    def has_permission(self, request, _):
        status = True
        try:
            auth_token = request.META.get("HTTP_AUTHORIZATION", None)
        except Exception:
            status = False
        if not auth_token:
            status = False

        user = decodeJWT(auth_token)

        if not user:
            status = False
        
        if not status:
            raise Exception("Authentication issue.")

        request.user = user
        return status