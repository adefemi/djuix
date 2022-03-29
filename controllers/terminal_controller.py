import os
import subprocess
import shlex
from abstractions.packages import PackageList
import shutil


class TerminalController:

    def __init__(self, path, project_name, delete_if_project_exist=False):
        self.path = self.transform_path(path) 
        self.project_name = project_name
        self.delete_if_project_exist = delete_if_project_exist
        
    def get_settings_path(self):
        formatted_project_name = self.get_formatted_name(self.project_name)
        return f"{self.path}/{formatted_project_name}/{formatted_project_name}/"

    def create_project(self):
        self.check_if_path_exist()
        self.check_if_project_already_exist()
        self.create_project_folder()
        self.create_env()
        self.install_packages()

        command_template = f"{self.get_env_full_path()} && django-admin startproject {self.get_formatted_name()}"
        p = subprocess.Popen(command_template, cwd=self.path,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
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
                self.delete_path(project_path)
            else:
                raise Exception("A project with the provided path already exist")
        return True

    def check_if_path_exist(self):
        if not os.path.exists(self.path):
            raise Exception("path do not exist")
        
        print("path exist")
        return True

    def get_formatted_name(self, name=None):
        if name:
            return name.lower().replace(" ", "_")
        return self.project_name.lower().replace(" ", "_")

    def get_env(self):
        return self.get_formatted_name() + "_env"
    
    def get_project_full_path(self):
        return f"{self.path}/{self.get_formatted_name()}"
    
    @staticmethod
    def transform_path(path):
        return path.replace("\\", "/")

    def get_env_full_path(self):
        return f"{self.path}/{self.get_env()}/Scripts/activate.bat"

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
        command_template = f"{self.get_env_full_path()} && python.exe -m pip install --upgrade pip"
        p = subprocess.Popen(command_template, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.wait()
        [_, err] = p.communicate()
        if err:
            raise Exception(err.decode())
        
        package_string_list = ""
        for package in PackageList.get_packages():
            package_string_list += package + " "
        command_template = f"{self.get_env_full_path()} && pip install {package_string_list}"
        p = subprocess.Popen(command_template, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.wait()
        [_, err] = p.communicate()
        if err:
            raise Exception(err.decode())
        
        print("installed packages")
        return True

    def create_app(self, app_name):
        command_template = "{} && python manage.py startapp {}"
        command = shlex.split(command_template.format(
            self.get_env_full_path(), self.get_formatted_name(app_name)))

        p = subprocess.Popen(command, cwd=self.get_project_full_path(),
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        p.wait()
        [_, err] = p.communicate()
        if err:
            raise Exception(err.decode())
        print("created app")

        # create serializer.py and url.py files
        from .directory_controller import DirectoryManager
        dir_manager = DirectoryManager(f"{self.path}/{self.project_name}/{app_name}/")

        dir_manager.create_file("serializers.py", "a")
        dir_manager.create_file("urls.py", "a")
        print("created serializers and urls")

        return True

    def run_migration(self):
        command_template = '/bin/bash -c "source {} && export {} && python manage.py makemigrations && python manage.py migrate"'
        export_settings = f"DJANGO_SETTINGS_MODULE={self.get_formatted_name()}.settings"
        command = shlex.split(command_template.format(
            self.get_env_full_path(), export_settings))
        p = subprocess.Popen(command, cwd=self.path + self.get_formatted_name(),
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.wait()
        [_, err] = p.communicate()
        if err:
            raise Exception(err.decode())
        return True

    @staticmethod
    def delete_path(path):
        try:
            shutil.rmtree(path)
        except OSError as e:
            raise Exception(e)
