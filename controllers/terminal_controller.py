import os
import subprocess
import shlex
from abstractions.packages import PackageList
from controllers.command_template import CommandTemplate, OsType
from .directory_controller import DirectoryManager


class TerminalController(CommandTemplate):

    def __init__(self, path, project_name, delete_if_project_exist=False):
        super().__init__(OsType.mac)
        self.path = self.transform_path(path) 
        self.project_name = project_name
        self.delete_if_project_exist = delete_if_project_exist
        
    def get_settings_path(self):
        formatted_project_name = self.get_formatted_name(self.project_name)
        return f"{self.path}/{formatted_project_name}/{formatted_project_name}/"

    def create_project(self):
        DirectoryManager.check_if_path_exist(self.path)
        self.check_if_project_already_exist()
        self.create_project_folder()
        self.create_env()
        self.install_packages()
        
        command = 'django-admin startproject'

        command_template = self.get_access_template(command, self.get_formatted_name())
        p = subprocess.Popen(command_template, cwd=self.path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.wait()
        [_, err] = p.communicate()
        if err:
            raise Exception(err.decode())

        return True
    
    def define_project_standard_name(self):
        return self.get_formatted_name() + "_main"
    
    def create_project_folder(self):
        project_name = self.define_project_standard_name()
        
        if os.path.exists(self.get_project_full_path()):
            command_template = "rm -r {}"
            command = shlex.split(command_template.format(project_name))
            p = subprocess.Popen(command, cwd=self.path,
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            p.wait()
            [_, err] = p.communicate()
            if err:
                raise Exception(err.decode())
        
        p = subprocess.Popen(["mkdir", project_name], cwd=self.path,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.wait()
        [_, err] = p.communicate()
        if err:
            raise Exception(err.decode())
        
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
        return self.get_formatted_name() + "_env"
    
    def get_project_full_path(self):
        return f"{self.path}/{self.get_formatted_name()}"
    
    @staticmethod
    def transform_path(path):
        return path.replace("\\", "/")

    def create_env(self):
        p = subprocess.Popen(["virtualenv", self.get_env()], cwd=self.path,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.wait()
        [_, err] = p.communicate()
        if err:
            raise Exception(err.decode())
        
        print("created virtual env")
        return True

    def install_packages(self):
        # upgrade pip first
        
        command = f"{self.get_python_command()} -m pip install --upgrade pip"
        command_template = self.get_access_template(command)

        p = subprocess.Popen(command_template, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.wait()
        [_, err] = p.communicate()
        if err:
            raise Exception(err.decode())
        print("updated pip")
        
        package_string_list = ""
        for package in PackageList.get_packages():
            package_string_list += package + " "
            
        command = "pip install"
        command_template = self.get_access_template(command, package_string_list)
        p = subprocess.Popen(command_template, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.wait()
        [_, err] = p.communicate()
        if err:
            raise Exception(err.decode())
        
        print("installed packages")
        return True

    def create_app(self, app_name):
        command = "python manage.py startapp"
        command_template = self.get_access_template(command, self.get_formatted_name(app_name))

        p = subprocess.Popen(command_template, cwd=self.get_project_full_path(),
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        p.wait()
        [_, err] = p.communicate()
        if err:
            raise Exception(err.decode())
        print("created app")

        # create serializer.py and url.py files
        from .directory_controller import DirectoryManager
        dir_manager = DirectoryManager(f"{self.path}/{self.project_name}/{self.get_formatted_name(app_name)}/")

        dir_manager.create_file("serializers.py", "a")
        dir_manager.create_file("urls.py", "a")
        print("created serializers and urls")

        return True

    def run_migration(self):
        settings_path = f"{self.get_formatted_name()}.settings";
        command_template = "{} && SET {}&& python manage.py makemigrations && python manage.py migrate"
        export_settings = f"DJANGO_SETTINGS_MODULE={settings_path}"

        command = shlex.split(command_template.format(
            self.get_env_full_path(), export_settings))
        p = subprocess.Popen(command, cwd=self.get_project_full_path(),
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        [_, err] = p.communicate()
        if err:
            raise Exception(err.decode())
        return True
