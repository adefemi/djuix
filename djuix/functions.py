from controllers.directory_controller import DirectoryManager
from django.conf import settings
import requests
import json
import time

    
def write_to_file(path_data, file_name, content):
    try:
        directory_manager = DirectoryManager(path_data)
        file_data = directory_manager.create_file(file_name)
        directory_manager.write_file(file_data, content)
        return True
    except Exception as e:
        print(e)
        return False
    
def send_socket(process_type, projectId, message):
    
    data = {
        "process_type": process_type,
        "id": projectId,
        "message": message
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


def send_process_message(project_id, message, wait_sec=1):
    
    send_socket("project_creation", project_id, message)
    time.sleep(wait_sec)
    return
        
    
