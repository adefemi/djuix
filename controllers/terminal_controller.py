import os
import subprocess
import shlex
from abstractions.defaults import PACKAGE_LIST
from controllers.command_template import CommandTemplate, OsType
from djuix.functions import send_process_message
from project_controller.models import Project
from .directory_controller import DirectoryManager


class TerminalController(CommandTemplate):

    def __init__(self, path, project_name, delete_if_project_exist=False, project_id=None):
        super().__init__(OsType.mac)
        self.path = self.transform_path(path) 
        self.project_name = project_name
        self.delete_if_project_exist = delete_if_project_exist
        self.project_id = project_id
        
    def get_settings_path(self):
        return f"{self.path}/{self.project_name}/{self.project_name}/"
    
    def handle_terminal_error(self, error):
        raise Exception(error)

    def create_project(self):
        status = DirectoryManager.check_if_path_exist(self.path)
        if not status:
            # this is a new project
            username = self.path.split("/")[-1] # this is the unique username
            temp_path = self.path
            self.path = self.path.removesuffix(f"/{username}")
            # create a new folder with the username
            self.create_project_folder(username)
            self.path = temp_path
        self.check_if_project_already_exist()
        self.create_project_folder()
        self.create_env()
        if self.project_id:
            self.install_packages(PACKAGE_LIST, Project.objects.get(id=self.project_id))
        
        command = 'django-admin startproject'

        command_template = self.get_access_template(command, self.project_name)
        p = subprocess.Popen(command_template, cwd=self.path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.wait()
        [_, err] = p.communicate()
        if err:
            self.handle_terminal_error(err.decode())

        return True
    
    def define_project_standard_name(self):
        return self.project_name + "_main"
    
    def create_project_folder(self, name=None):
        if self.project_id:
            send_process_message(self.project_id, "creating project folder...")
        project_name = name or self.define_project_standard_name()
        
        if os.path.exists(self.get_project_full_path()):
            command_template = "rm -r {}"
            command = shlex.split(command_template.format(project_name))
            p = subprocess.Popen(command, cwd=self.path,
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            p.wait()
            [_, err] = p.communicate()
            if err:
                self.handle_terminal_error(err.decode())
        
        p = subprocess.Popen(["mkdir", project_name], cwd=self.path,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.wait()
        [_, err] = p.communicate()
        if err:
            self.handle_terminal_error(err.decode())
        
        self.path = f"{self.path}/{project_name}"
        
        print("created project folder")
        
        return True
    
    def check_if_project_already_exist(self):
        project_path = self.path + "/" + self.define_project_standard_name()
        if os.path.exists(project_path):
            if self.delete_if_project_exist:
                DirectoryManager.delete_directory(project_path)
            else:
                raise Exception("A project with the provided path already exist")
        return True

    def get_env(self):
        return self.project_name + "_env"
    
    def get_project_full_path(self):
        return f"{self.path}/{self.project_name}"
    
    @staticmethod
    def transform_path(path):
        return path.replace("\\", "/")

    def create_env(self):
        p = subprocess.Popen(["virtualenv", self.get_env()], cwd=self.path,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.wait()
        [_, err] = p.communicate()
        if err:
            self.handle_terminal_error(err.decode())
        
        print("created virtual env")
        return True

    def install_packages(self, custom_packages=None, project=None):
        if self.project_id:
            send_process_message(self.project_id, "installing required packages...", 0)
        # upgrade pip first
        command = f"{self.get_python_command()} -m pip install --upgrade pip"
        command_template = self.get_access_template(command)

        p = subprocess.Popen(command_template, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.wait()
        [_, err] = p.communicate()
        if err:
            self.handle_terminal_error(err.decode())
        print("updated pip")
        
        packages_to_use = custom_packages if custom_packages is not None else PACKAGE_LIST
        
        package_string_list = ""
        for package in packages_to_use:
            package_string_list += package["version"] + " "
            
        command = "pip install"
        command_template = self.get_access_template(command, package_string_list)
        p = subprocess.Popen(command_template, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.wait()
        [_, err] = p.communicate()
        if err:
            self.handle_terminal_error(err.decode())
            
        # freeze out the required packages
        command = "pip freeze > requirements.txt"
        command_template = self.get_access_template(command)
        p = subprocess.Popen(command_template, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.wait()
        [_, err] = p.communicate()
        if err:
            self.handle_terminal_error(err.decode())
            
        project.project_setting.packages = custom_packages
        project.project_setting.save()
        
        return True

    def create_app(self, app_name):
        command = "python manage.py startapp"
        command_template = self.get_access_template(command, app_name)

        p = subprocess.Popen(command_template, cwd=self.get_project_full_path(),
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        p.wait()
        [_, err] = p.communicate()
        if err:
            self.handle_terminal_error(err.decode())
        print("created app")

        # create serializer.py and url.py files
        from .directory_controller import DirectoryManager
        dir_path = f"{self.get_project_full_path()}/{app_name}/"
        dir_manager = DirectoryManager(dir_path)

        dir_manager.create_file("serializers.py", "a")
        dir_manager.create_file("urls.py", "a")
        print("created serializers and urls")

        return True

    def run_migration(self):
        settings_path = f"{self.project_name}.settings";
        export_settings = f"DJANGO_SETTINGS_MODULE={settings_path}"
        
        export_op_key = "SET"
        if self.os_type == OsType.mac:
            export_op_key =  "export"
            
        project_dir = self.get_project_full_path()
        
        command = f"{export_op_key} {export_settings} && cd {project_dir} && python manage.py makemigrations --noinput && python manage.py migrate"
        command_template = self.get_access_template(command, "")
        
        p = subprocess.Popen(command_template, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        [_, err] = p.communicate()
        if err:
            self.handle_terminal_error(err.decode())
        
        if p.returncode == 3:
            raise Exception("We could not fulfill the request for the modification. We sugestions you provide a default value for fields just added")

        return True
