from rest_framework.viewsets import ModelViewSet
from .serializers import Project, ProjectSerializer, App, AppSerializer
from controllers.terminal_controller import TerminalController
from rest_framework.response import Response
from djuix import functions
from djuix.helper import Helper


class ProjectView(ModelViewSet):
    serializer_class = ProjectSerializer
    queryset = Project.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        project_path = serializer.data["project_path"]
        active_project = None

        terminal_controller = TerminalController(project_path, serializer.data["name"])

        try:
            terminal_controller.create_project()
            project_path = terminal_controller.path
            active_project = self.queryset.get(id=serializer.data["id"])
            active_project.project_path = project_path
            active_project.save()
            print("project created")
        except Exception as e:
            self.queryset.filter(id=serializer.data["id"]).delete()
            raise Exception(e)

        try:
            functions.create_settings(
                serializer.data["name"], serializer.data["id"])
            print("settings created")
        except Exception as e:
            self.queryset.filter(id=serializer.data["id"]).delete()
            raise Exception(e)

        try:
            functions.update_settings(
                f"{project_path}/{serializer.data['name']}/{serializer.data['name']}/", serializer.data["id"])
            print("settings updated")
        except Exception as e:
            self.queryset.filter(id=serializer.data["id"]).delete()
            raise Exception(e)

        return Response(self.serializer_class(active_project).data, status=201)


class AppView(ModelViewSet):
    serializer_class = AppSerializer
    queryset = App.objects.prefetch_related("project")

    def create(self, request, *args, **kwargs):
        data = Helper.normalizer_request(request.data)
        project = ProjectView.queryset.filter(id=data.get("project_id", None))

        if not project:
            raise Exception("Project with the specified id does not exist")

        project = project[0]

        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        terminal_controller = TerminalController(
            project.project_path, project.name)

        try:
            terminal_controller.create_app(serializer.data["name"])
        except Exception as e:
            self.queryset.filter(id=serializer.data["id"]).delete()
            raise Exception(e)

        if serializer.data["is_auth"]:
            self.create_auth_data()
            pass

        return Response(serializer.data, status="201")

    def create_auth_data(self):
        pass
