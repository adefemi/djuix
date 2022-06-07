from rest_framework.viewsets import ModelViewSet
from .serializers import Project, ProjectSerializer, App, AppSerializer
from .models import SettingValue
from controllers.terminal_controller import TerminalController
from rest_framework.response import Response
from djuix import functions
from djuix.helper import Helper
from abstractions.enums import Enums
from ast import literal_eval
from functools import reduce


class ProjectView(ModelViewSet):
    serializer_class = ProjectSerializer
    queryset = Project.objects.all()

    def create(self, request, *args, **kwargs):
        data = Helper.normalizer_request(request.data)
        
        delete_if_project_exist = data.get("delete_if_project_exist", False)
        if(delete_if_project_exist):
            Project.objects.filter(name=data["name"]).delete()
                
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data.pop("delete_if_project_exist", None)
        serializer.save()
        
        project_path = serializer.data["project_path"]
        active_project = None

        terminal_controller = TerminalController(project_path, serializer.data["name"], delete_if_project_exist)

        try:
            terminal_controller.create_project()
            project_path = terminal_controller.path
            active_project = self.queryset.get(id=serializer.data["id"])
            active_project.project_path = project_path
            active_project.save()
            print("project created")
        except Exception as e:
            self.queryset.filter(id=serializer.data["id"]).delete()
            print(e)
            raise Exception(e)

        try:
            functions.create_settings(
                serializer.data["name"], serializer.data["id"])
            print("settings created")
        except Exception as e:
            self.queryset.filter(id=serializer.data["id"]).delete()
            print(e)
            raise Exception(e)

        try:
            functions.update_settings(
                terminal_controller.get_settings_path(), serializer.data["id"])
            print("settings updated")
        except Exception as e:
            self.queryset.filter(id=serializer.data["id"]).delete()
            print(e)
            raise Exception(e)

        return Response(self.serializer_class(active_project).data, status=201)


class AppView(ModelViewSet):
    serializer_class = AppSerializer
    queryset = App.objects.prefetch_related("project")

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        project = serializer.data["project"]
        

        terminal_controller = TerminalController(
            project["project_path"], project["name"])

        try:
            terminal_controller.create_app(serializer.data["name"])
        except Exception as e:
            self.queryset.filter(id=serializer.data["id"]).delete()
            raise Exception(e)
        
        print("got here")
        
        # update setting installed app with new app
        # get project settings installed app values
        installed_apps = SettingValue.objects.get(project_id=project["id"], name=Enums.INSTALLED_APPS)
        installed_apps_array = literal_eval(installed_apps.value)
        new_installed_app = """[
    {}'{}',
]""".format(reduce(lambda a, b:f"{a}'{b}',\n    ", installed_apps_array, ""), serializer.data["name"])
        installed_apps.value = new_installed_app
        installed_apps.save()
        
        print("got here")
        
        try:
            functions.update_settings(
                terminal_controller.get_settings_path(), project["id"])
            print("settings updated")
        except Exception as e:
            self.queryset.filter(id=serializer.data["id"]).delete()
            print(e)
            raise Exception(e)
  

        return Response(serializer.data, status="201")
