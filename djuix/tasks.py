from django.core.mail.message import EmailMessage
from celery import shared_task
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .custom_methods import upload_folder_zip
from controllers.directory_controller import DirectoryManager
from abstractions.defaults import DEFAULT_PROJECT_DIR, TEST_SERVER_TIMEOUT
import os
from sentry_sdk import capture_message


@shared_task
def send_email(subject, html_msg, email):
    mail = EmailMessage(
        subject,
        html_msg,
        f"Djuix.io <{settings.EMAIL_HOST_USER}>",
        [email],
    )
    mail.content_subtype = 'html'
    mail.send(fail_silently=False)
    

@shared_task
def backup_project():
    from user_management.models import CustomUser
    
    # get users that has their last activity more that 3 hours and has not been backed up yet
    expiry = timezone.now() - timedelta(hours=3)
    users = CustomUser.objects.filter(last_activity__lt=expiry, removed_folder=False)
    
    for user in users:
        
        if user.project_owner.all().count() < 1:
            continue
        
        user.removed_folder = True
        user.save()
        
        folder_name = user.username.lower()
        
        upload_folder_zip(DEFAULT_PROJECT_DIR, folder_name, folder_name)
        
        try:
            DirectoryManager.delete_directory(os.path.join(DEFAULT_PROJECT_DIR, folder_name))
        except Exception:
            # directory already deleted
            pass
        
        
@shared_task
def remove_test_server(server_id):
    from project_controller.services.test_server_creation import TestServerCreation
    from project_controller.models import TestServer
    
    try:
        test_server = TestServer.objects.get(id=server_id)
    except TestServer.DoesNotExist:
        return
    
    test_server_creation = TestServerCreation(test_server.project, test_server.port)
    
    try:
        test_server_creation.deploy_down()
        test_server.delete()
    except Exception as e:
        capture_message(e)
        

@shared_task
def delete_lingering_test_server():
    from project_controller.models import TestServer
    
    expiry = timezone.now() - timedelta(seconds=TEST_SERVER_TIMEOUT)
    test_servers = TestServer.objects.filter(created_at__lt=expiry)
    
    for test_server in test_servers:
        remove_test_server(test_server.id)