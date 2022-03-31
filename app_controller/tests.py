from rest_framework.test import APITestCase, APITransactionTestCase
from controllers.terminal_controller import TerminalController
from controllers.directory_controller import DirectoryManager
import json
import os
import time


def clean_up(path="/home/adefemigreat/Desktop/DjuixFiles/"):
    # some cleanup
    DirectoryManager.delete_directory(path+"test_project")
    DirectoryManager.delete_directory(path+"test_project_env")
    time.sleep(1)


class TestWriteToModel(APITransactionTestCase):
    project_endpoint = "/project-controls/project"
    app_endpoint = "/project-controls/app"
    model_endpoint = "/app-controls/model"
    serializer_endpoint = "/app-controls/serializer"

    def setUp(self):
        project_data = {
            "name": "test_project",
            "description": "this is a test project",
            "project_path": "/home/adefemigreat/Desktop/DjuixFiles/"
        }

        response = self.client.post(self.project_endpoint, data=json.dumps(
            project_data), content_type='application/json')
        res = response.json()

        app_data = {
            "name": "test_app",
            "description": "this is a test app",
            "project_id": res["id"]
        }

        response = self.client.post(self.app_endpoint, data=json.dumps(
            app_data), content_type='application/json')
        res = response.json()

        self.app_id = res["id"]

    def test_create_model(self):
        model_data = {
            "name": "test_model",
            "app_id": self.app_id,
            "fields": [
                {
                    "name": "test_field_1",
                    "field_type": "CharField",
                },
                {
                    "name": "test_field_2",
                    "field_type": "TextField",
                    "is_blank": True,
                    "is_null": True
                },
                {
                    "name": "created_at",
                    "field_type": "DateTimeField",
                    "is_created_at": True
                },
                {
                    "name": "updated_at",
                    "field_type": "DateTimeField",
                },
            ]
        }

        response = self.client.post(self.model_endpoint, data=json.dumps(
            model_data), content_type='application/json')
        res = response.json()

        data = {
            "model_relation_id": res["id"],
            "app_id": self.app_id,
            "name": "test_model_serializer"
        }

        response = self.client.post(self.serializer_endpoint, data=json.dumps(
            data), content_type='application/json')

        res = response.json()

        # no model serializer
        data = {
            "app_id": self.app_id,
            "name": "test_no_model_serializer",
            "fields": [
                {
                    "name": "test_field_1",
                    "field_type": "CharField",
                    "is_write_only": True
                },
                {
                    "name": "test_field_2",
                    "field_type": "TextField",
                    "is_read_only": True,
                }
            ]
        }

        response = self.client.post(self.serializer_endpoint, data=json.dumps(
            data), content_type='application/json')

        res = response.json()

        print(res)
        # clean_up()
