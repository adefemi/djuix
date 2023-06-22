from rest_framework.views import exception_handler
from rest_framework.response import Response
import traceback 
from django.core.files.storage import default_storage
import shutil
import os
import subprocess
import boto3
from django.conf import settings
from abstractions.deployment import get_docker_compose_content, get_dockerfile_content
from abstractions.project_readme import readme_content
from django.utils import timezone


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
        
    # remove existing folder if it exists
    try:
        subprocess.run(["rm", "-r", working_dir])
    except Exception:
        pass
        
    subprocess.run(["mkdir", working_dir])
    subprocess.call(["unzip", "-o", extract_folder, '-d', working_dir])
    
    try:
        os.remove(extract_folder)
    except Exception:
        pass
    default_storage.delete(file_location)
    

def delete_folder_if_exists(name, default_path):
    from controllers.directory_controller import DirectoryManager
    file_path = os.path.join(default_path, name)
    try:
        DirectoryManager.delete_file(file_path)
    except Exception:
        pass
    
def setup_for_download(project):
    
    from controllers.directory_controller import DirectoryManager
    
    # create .sh script to start server
    
    project_path = os.path.join(project.project_path, project.formatted_name)
    dir_controller = DirectoryManager(project_path)
    
    delete_folder_if_exists('Readme.md', project_path)
    
    start_server_file = dir_controller.create_file('/Readme.md')
    dir_controller.write_file(start_server_file, readme_content)
    
    
    start_server_content = f"""
#!/bin/bash
        
# Build Project
docker-compose build

# Start Server
docker-compose up -d
"""
    
    delete_folder_if_exists('start_server.sh', project_path)
    
    start_server_file = dir_controller.create_file('/start_server.sh')
    dir_controller.write_file(start_server_file, start_server_content)
    
    # push docker artifacts
    delete_folder_if_exists('Dockerfile', project_path)
    
    dockerfile = dir_controller.create_file('/Dockerfile')
    dir_controller.write_file(dockerfile, get_dockerfile_content(project.formatted_name))
    
    delete_folder_if_exists('docker-compose.yml', project_path)
    
    docker_compose_file = dir_controller.create_file('/docker-compose.yml')
    dir_controller.write_file(docker_compose_file, get_docker_compose_content(project.formatted_name, 8000))
    
    
def download_project(project):
    from controllers.terminal_controller import TerminalController

    
    project_path = os.path.join(project.project_path, project.formatted_name)
    
    project_name = project.formatted_name
    object_name = f"{project_name}.zip"
    zip_filename = project_path + ".zip"
    
    shutil.make_archive(project_path, 'zip', project_path)
    
    default_storage.save(os.path.join("downloads", object_name), open(zip_filename, 'rb'))
    
    os.remove(zip_filename)
    
    client = boto3.client('s3', region_name=settings.AWS_S3_REGION_NAME, aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
    download_link = client.generate_presigned_url(
        'get_object',
        Params={'Bucket': settings.AWS_STORAGE_BUCKET_NAME, 'Key': f"downloads/{object_name}"}, 
        HttpMethod="GET", ExpiresIn=3600)
    
    return download_link

def get_minutes_remaining(time_sec, created_at):
    # calculate the difference between now and the creation time
    delta = timezone.now() - created_at

    # calculate remaining minutes
    minutes_remaining = time_sec - delta.total_seconds()

    return minutes_remaining/60