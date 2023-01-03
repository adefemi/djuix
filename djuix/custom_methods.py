from rest_framework.views import exception_handler
from rest_framework.response import Response
import traceback 
from django.core.files.storage import default_storage
import zipfile
import shutil
import os
import shlex
import subprocess


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

def upload_folder_zip(folder_parent_path, folder_name, file_name):
    
    object_name = f"{file_name}.zip"
    zip_filename = os.path.join(folder_parent_path, object_name)
    folder_path = os.path.join(folder_parent_path, folder_name)
    
    shutil.make_archive(os.path.join(folder_parent_path, file_name), 'zip', folder_path)
    
    default_storage.save(os.path.join("history", object_name), open(zip_filename, 'rb'))
    
    os.remove(zip_filename)
    
def download_zip(folder_parent_path, folder_name, file_name):
    
    object_name = f"{file_name}.zip"
    file_location = os.path.join("history", object_name)
    extract_folder = os.path.join(folder_parent_path, object_name)
    working_dir = os.path.join(folder_parent_path, folder_name)
    
    with default_storage.open(file_location, 'rb') as f:
        contents = f.read()

    with open(extract_folder, 'wb') as f:
        f.write(contents)
        
    subprocess.run(["mkdir", working_dir])
    subprocess.call(["unzip", "-o", extract_folder, '-d', working_dir])
    
    try:
        os.remove(extract_folder)
    except Exception:
        pass
    default_storage.delete(file_location)