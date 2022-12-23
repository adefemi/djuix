from rest_framework.views import exception_handler
from rest_framework.response import Response
import traceback 


def custom_exception_handler(exc, context):

    response = exception_handler(exc, context)

    if response is not None:
        return response

    print(traceback.format_exc())
    exc_list = str(exc).split("DETAIL: ")
    
    status_code = 403
    auth_error = "Authentication issue." in exc_list
    
    if auth_error:
        status_code = 401
        
    print("my status: ", status_code)

    return Response({"error": exc_list}, status=status_code)
