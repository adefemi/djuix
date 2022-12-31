from django.core.mail.message import EmailMessage
from celery import shared_task
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .custom_methods import upload_folder_zip
from controllers.directory_controller import DirectoryManager
from abstractions.defaults import DEFAULT_PROJECT_DIR
import os


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
    
    # get users that has their last activity more that 1 hour and has not been backed up yet
    one_hour_ago = timezone.now() - timedelta(minutes=10)
    users = CustomUser.objects.filter(last_activity__lt=one_hour_ago, removed_folder=False)
    
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
        