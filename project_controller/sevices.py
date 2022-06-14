

from ast import literal_eval
from functools import reduce
from abstractions.enums import Enums
from controllers.terminal_controller import TerminalController
from djuix import functions
from project_controller.models import App, SettingValue
from project_controller.serializers import AppSerializer


def process_app_creation(data):
        serializer = AppSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        queryset = App.objects.prefetch_related("project")
        
        project = serializer.data["project"]

        terminal_controller = TerminalController(
            project["project_path"], project["name"])

        try:
            terminal_controller.create_app(serializer.data["name"])
        except Exception as e:
            queryset.filter(id=serializer.data["id"]).delete()
            raise Exception(e)
        
        # update setting installed app with new app
        # get project settings installed app values
        installed_apps = SettingValue.objects.get(project_id=project["id"], name=Enums.INSTALLED_APPS)
        installed_apps_array = literal_eval(installed_apps.value)
        new_installed_app = """[
    {}'{}',
]""".format(reduce(lambda a, b:f"{a}'{b}',\n    ", installed_apps_array, ""), serializer.data["name"])
        installed_apps.value = new_installed_app
        installed_apps.save()
        
        try:
            functions.update_settings(
                terminal_controller.get_settings_path(), project["id"])
            print("settings updated")
        except Exception as e:
            queryset.filter(id=serializer.data["id"]).delete()
            print(e)
            raise Exception(e)
        
        app = App.objects.get(id=serializer.data["id"])
        
        return app