from rest_framework.test import APITestCase, APITransactionTestCase
from controllers.terminal_controller import TerminalController
import json
import os
import time


def clean_up(path="/home/adefemigreat/Desktop/DjuixFiles/"):
    # some cleanup
    TerminalController.delete_path(path+"test_project")
    TerminalController.delete_path(path+"test_project_env")
    time.sleep(1)


class TestProject(APITransactionTestCase):
    project_endpoint = "/project-controls/project"

    def setUp(self):
        data = {
            "name": "test_project",
            "description": "this is a test project",
            "project_path": "/home/adefemigreat/Desktop/DjuixFiles/"
        }

        self.response = self.client.post(self.project_endpoint, data=json.dumps(
            data), content_type='application/json')

    def test_create_project(self):
        result = self.response.json()

        self.assertEqual(self.response.status_code, 201)
        self.assertEqual(result["name"], "test_project")
        self.assertTrue(os.path.exists(
            "/home/adefemigreat/Desktop/DjuixFiles/test_project"))
        self.assertTrue(os.path.exists(
            "/home/adefemigreat/Desktop/DjuixFiles/test_project_env"))

        # some cleanup
        clean_up()

    def test_get_projects(self):
        response = self.client.get(self.project_endpoint)
        result = response.json()["results"]

        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(result, list))
        self.assertEqual(result[0]["name"], "test_project")
        self.assertTrue(os.path.exists(
            result[0]["project_path"]+"test_project"))
        self.assertTrue(os.path.exists(
            result[0]["project_path"]+"test_project_env"))

        # some cleanup
        clean_up()


class TestApp(APITransactionTestCase):
    project_endpoint = "/project-controls/project"
    app_endpoint = "/project-controls/app"

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

        self.response = self.client.post(self.app_endpoint, data=json.dumps(
            app_data), content_type='application/json')

    def test_create_app(self):
        result = self.response.json()

        self.assertEqual(self.response.status_code, 201)
        self.assertEqual(result["name"], "test_app")
        self.assertTrue(os.path.exists(
            "/home/adefemigreat/Desktop/DjuixFiles/test_project/test_app/serializers.py"))
        self.assertTrue(os.path.exists(
            "/home/adefemigreat/Desktop/DjuixFiles/test_project/test_app/urls.py"))

        # some cleanup
        clean_up()

    def test_get_apps(self):
        response = self.client.get(self.app_endpoint)
        result = response.json()["results"]

        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(result, list))
        self.assertEqual(result[0]["name"], "test_app")
        self.assertTrue(os.path.exists(
            result[0]["project"]["project_path"]+"test_project/test_app/serializers.py"))
        self.assertTrue(os.path.exists(
            result[0]["project"]["project_path"]+"test_project/test_app/urls.py"))

        # some cleanup
        clean_up()
