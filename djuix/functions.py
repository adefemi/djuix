from controllers.directory_controller import DirectoryManager
from django.conf import settings
import requests
import json
import time
from django.template.loader import render_to_string
from abstractions.defaults import app_email_name, support_mail
from .tasks import send_email
import random
import string


def write_to_file(path_data, file_name, content):
    try:
        directory_manager = DirectoryManager(path_data)
        file_data = directory_manager.create_file(file_name)
        directory_manager.write_file(file_data, content)
        return True
    except Exception as e:
        print(e)
        return False


def send_socket(process_type, projectId, message, done=False):

    data = {
        "process_type": process_type,
        "id": projectId,
        "message": message,
        "done": done,
    }

    headers = {
        'Content-Type': 'application/json',
    }
    try:
        res = requests.post(settings.SOCKET_SERVER, json.dumps(
            data), headers=headers)
    except Exception as e:
        pass
    return True


def send_process_message(project_id, message, wait_sec=1, done=False):

    send_socket("project_creation", project_id, message, done)
    time.sleep(wait_sec)
    return


def send_verification_email(user, token):
    subject = "Welcome to Djuix.io"
    html_message = render_to_string("verification.html", {
        'username': str(user.username).capitalize(),
        'code': token,
        'support_mail': support_mail,
        "app_email_name": app_email_name
    })

    send_email.delay(subject, html_message, user.email)


def send_password_reset(user, token):
    subject = "Password reset request"
    html_message = render_to_string("forgot_password.html", {
        'username': str(user.username).capitalize(),
        'code': token,
        'support_mail': support_mail,
        "app_email_name": app_email_name
    })

    send_email.delay(subject, html_message, user.email)


def generate_random_string(length):
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choices(characters, k=length))
    return random_string
