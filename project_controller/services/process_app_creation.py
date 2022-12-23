from controllers.terminal_controller import TerminalController
from project_controller.models import App
from project_controller.serializers import AppSerializer
from project_controller.services.write_settings_file import WriteSettings


def process_app_creation(data):
        serializer = AppSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        app = App.objects.get(id=serializer.data["id"])
        
        project = app.project

        terminal_controller = TerminalController(project.project_path, project)

        try:
            terminal_controller.create_app(app.formatted_name)
        except Exception as e:
            app.delete()
            raise Exception(e)
        
        # update setting installed app with new app
        # get project settings installed app values
        project_settings = project.project_setting
        project_settings.properties["INSTALLED_APPS"]["items"].append(f"{app.formatted_name}")
        project_settings.save()
        
        settings_c = WriteSettings(project)
        settings_c.update_setting(project_settings.properties)
        
        return app