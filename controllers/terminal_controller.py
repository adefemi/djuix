import os
import subprocess
import shlex
from abstractions.packages import PackageList
import shutil


class TerminalController:

    def __init__(self, path, project_name):
        self.path = path
        self.project_name = project_name

    def create_project(self):
        self.check_if_path_exist()
        self.create_env()
        self.install_packages()

        command_template = '/bin/bash -c "source {} && django-admin startproject {}"'
        command = shlex.split(command_template.format(
            self.get_env_full_path(), self.get_formatted_name()))
        p = subprocess.Popen(command, cwd=self.path,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.wait()
        [_, err] = p.communicate()
        if err:
            raise Exception(err.decode())

        return True

    def check_if_path_exist(self):
        if not os.path.exists(self.path):
            raise Exception("path do not exist")

    def get_formatted_name(self, name=None):
        if name:
            return name.lower().replace(" ", "_")
        return self.project_name.lower().replace(" ", "_")

    def get_env(self):
        return self.get_formatted_name() + "_env"

    def get_env_full_path(self):
        return self.path + self.get_env() + "/bin/activate"

    def create_env(self):
        if os.path.exists(self.get_env_full_path()):
            command_template = "rm -r {}"
            command = shlex.split(command_template.format(self.get_env()))
            p = subprocess.Popen(command, cwd=self.path,
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            p.wait()
            [_, err] = p.communicate()
            if err:
                raise Exception(err.decode())

        p = subprocess.Popen(["virtualenv", self.get_env()], cwd=self.path,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.wait()
        [_, err] = p.communicate()
        if err:
            raise Exception(err.decode())
        return True

    def install_packages(self):
        package_string_list = ""
        for package in PackageList.get_packages():
            package_string_list += package + " "
        command_template = '/bin/bash -c "source {} && pip install {}"'
        command = shlex.split(command_template.format(
            self.get_env_full_path(), package_string_list))
        p = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.wait()
        [_, err] = p.communicate()
        if err:
            raise Exception(err.decode())
        return True

    def create_app(self, app_name):
        command_template = '/bin/bash -c "source {} && python manage.py startapp {}"'
        command = shlex.split(command_template.format(
            self.get_env_full_path(), self.get_formatted_name(app_name)))
        p = subprocess.Popen(command, cwd=self.path + self.get_formatted_name(),
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.wait()
        [_, err] = p.communicate()
        if err:
            raise Exception(err.decode())

        # create serializer.py and url.py files
        from .directory_controller import DirectoryManager
        dir_manager = DirectoryManager(
            self.path + self.project_name + f"/{app_name}/")

        dir_manager.create_file("serializers.py", "a")
        dir_manager.create_file("urls.py", "a")

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
